import os, subprocess, json, traceback, logging, tempfile
from helpers import *

da_artist_insert_query = '''INSERT INTO ARTISTS_D(ARTIST_ID, ARTIST_NAME, ARTIST_URL, DIRECTORY_NAME)VALUES(%s,%s,%s,%s)'''
da_img_insert_query = '''INSERT INTO IMAGES_D(IMAGE_INDEX, FILENAME, IMAGE_TITLE, LINKED_ARTIST_ID)VALUES(%s,%s,%s,%s)'''
da_gallery_insert_query = '''INSERT INTO GALLERIES_D(GALLERY_NAME, LINKED_ARTIST_ID)VALUES(%s,%s)'''
da_junction_insert_query = '''INSERT INTO JUNCT_GALL_IMAGE_D(LINKED_IMG_ID, LINKED_GALL_ID)VALUES(%s,%s)'''

def getDirFromArtistId(artistId):
    db = db_connect()
    cursor = db.cursor(buffered=True)
    sql_query = f"SELECT DIRECTORY_NAME, ARTIST_NAME FROM ARTISTS_D WHERE ID = {artistId} LIMIT 1;"
    cursor.execute(sql_query)
    resultData = cursor.fetchall()
    db.commit()
    cursor.close()
    db.close()
    return resultData[0]

def getImageDataByGalleryId(gallery_id, page_num):
    return (
        f"SELECT i.ID, i.IMAGE_INDEX, i.FILENAME, i.IMAGE_TITLE, a.ARTIST_NAME, a.DIRECTORY_NAME, g.GALLERY_NAME "
        f"FROM JUNCT_GALL_IMAGE_D AS j "
        f"JOIN IMAGES_D AS i ON i.ID = j.LINKED_IMG_ID "
        f"JOIN ARTISTS_D AS a ON a.ID = i.LINKED_ARTIST_ID "
        f"JOIN GALLERIES_D AS g ON g.ID = j.LINKED_GALL_ID "
        f"WHERE j.LINKED_GALL_ID = {gallery_id} "
        f"LIMIT {MAX_GPAGE_SIZE} OFFSET {page_num * MAX_GPAGE_SIZE};"
    )

def getImagesByGalleryIdPaged(gallery_id, page_num):
    db = db_connect()
    cursor = db.cursor(buffered=True, dictionary=True)
    cursor.execute(getImageDataByGalleryId(gallery_id, page_num))
    resultData = cursor.fetchall()
    db.commit()
    cursor.close()
    db.close()
    return resultData


def getGalleriesByArtistQuery(artist_id):
    return (
        f"SELECT g.ID, g.GALLERY_NAME, g.NUM_IMAGES, i.FILENAME, a.DIRECTORY_NAME, a.ARTIST_NAME "
        f"FROM GALLERIES_D g "
        f"INNER JOIN (SELECT *  "
        f"FROM IMAGES_D  "
        f"GROUP BY LINKED_ARTIST_ID) AS i "
        f"INNER JOIN (SELECT *  "
        f"FROM ARTISTS_D) AS a "
        f"WHERE i.LINKED_ARTIST_ID = g.LINKED_ARTIST_ID AND a.ID = {artist_id} AND g.LINKED_ARTIST_ID = {artist_id};"
    )

def getGalleriesByArtist(artist_id):
    db = db_connect()
    cursor = db.cursor(buffered=True, dictionary=True)
    cursor.execute(getGalleriesByArtistQuery(artist_id))
    resultData = cursor.fetchall()
    db.commit()
    cursor.close()
    db.close()
    return resultData


def getArtistsQuery():
    return (
        f"SELECT a.ARTIST_NAME, a.ID, a.NUM_IMAGES, a.DIRECTORY_NAME, d.FILENAME "
        f"FROM ARTISTS_D a "
        f"INNER JOIN IMAGES_D d "
        f"WHERE d.LINKED_ARTIST_ID = a.ID "
        f"GROUP BY a.ID "
        f"ORDER BY a.ID DESC;"
    )

def getArtists():
    db = db_connect()
    cursor = db.cursor(buffered=True, dictionary=True)
    cursor.execute(getArtistsQuery())
    resultData = cursor.fetchall()
    db.commit()
    cursor.close()
    db.close()
    return resultData

def add_da_url(download_url):
    print_message("DA ADD", f"adding {download_url}")
    tempdir = tempfile.TemporaryDirectory()
    if not download_img(download_url, tempdir.name):
        return [0, 0]
    result = load_images(tempdir.name)
    tempdir.cleanup()
    return result


def download_img(download_url, tempdir):
    print_message("exec", f"gallery-dl ({download_url})")
    result = subprocess.Popen([
        GALLERY_DL, "--write-metadata", "-c", GALLERY_DL_CONF, "-D", tempdir,
        download_url
    ],
                              text=True)
    result.wait()
    print_message("exit", f"gallery-dl ({download_url})")

    if result.returncode != 0:
        print_message("error",
                      f"unable to dl link ({download_url}), check stdout")
        return False
    return True


def isArtistAlreadyStored(artist_id):
    db = db_connect()
    cursor = db.cursor(buffered=True)
    cursor.execute(
        f"SELECT ID, DIRECTORY_NAME FROM ARTISTS_D WHERE ARTIST_ID = '{artist_id}' LIMIT 1;"
    )
    data = cursor.fetchall()
    cursor.close()
    if len(data) == 0:
        return (-1, '')
    return data[0]


def isImageAlreadyStored(image_index):
    db = db_connect()
    cursor = db.cursor(buffered=True)
    cursor.execute(
        f"SELECT ID, LINKED_ARTIST_ID FROM IMAGES_D WHERE IMAGE_INDEX = {image_index} LIMIT 1;"
    )
    data = cursor.fetchall()
    cursor.close()
    if len(data) == 0:
        return False
    return True


def isGalleryAlreadyStored(gallery_name, artist_id):
    db = db_connect()
    cursor = db.cursor(buffered=True)
    cursor.execute(
        f"SELECT ID FROM GALLERIES_D WHERE GALLERY_NAME = '{gallery_name}' and LINKED_ARTIST_ID = {artist_id} LIMIT 1;"
    )
    data = cursor.fetchall()
    cursor.close()
    if len(data) == 0:
        return -1
    return data[0][0]


def doesJunctionAlreadyExist(LINKED_IMG_ID, LINKED_GALL_ID):
    db = db_connect()
    cursor = db.cursor(buffered=True)
    cursor.execute(
        f"SELECT ID FROM JUNCT_GALL_IMAGE_D WHERE LINKED_IMG_ID = {LINKED_IMG_ID} and LINKED_GALL_ID = {LINKED_GALL_ID} LIMIT 1;"
    )
    data = cursor.fetchall()
    cursor.close()
    if len(data) == 0:
        return -1
    return data[0]


def load_images(tempdir):
    # iterating over all files
    img_added = 0
    for entry in os.scandir(tempdir):
        if entry.is_dir() or not entry.name.endswith(FILE_TYPES):
            continue  # skip directories and non-images

        result = load_image(entry.path)

        if (result == -1):
            continue
        img_added += 1
    return [img_added, img_added]


def load_image(imgPath):
    imgData = getImageData(imgPath)
    if isImageAlreadyStored(imgData["IMAGE_INDEX"]):
        print("IMAGE ALREADY STORED: " + str(imgData["IMAGE_INDEX"]))
        return -1
    (artist_id, artist_dir) = getArtistData(imgData["ARTIST_ID"],
                                            imgData["ARTIST_NAME"],
                                            imgData["ARTIST_URL"])
    if artist_id == -1 or artist_dir == "":
        return -1
    newfname = str(imgData["IMAGE_INDEX"]) + "_" + gen_rand_str()
    webp_conv_and_move(
        imgPath, os.path.join(DA_GALLERY_DIR, artist_dir, newfname + ".webp"))
    try:
        img_id_added = db_ins_image(imgData["IMAGE_INDEX"], newfname,
                                    imgData["IMAGE_TITLE"], artist_id)
        print_message(
            "IMAGE ADDED",
            f"ID: {img_id_added} | ID: " + str(imgData["IMAGE_INDEX"]))
    except Exception as e:
        logging.error(traceback.format_exc())
        return -1
    add_gallery_info(imgData["GALLERIES"], img_id_added, artist_id)
    return img_id_added


def add_gallery_info(galleries, image_id, artist_id):
    for gallery in galleries:
        gall_id = isGalleryAlreadyStored(gallery, artist_id)
        if gall_id == -1:
            print_message("GALLERY ADDED",
                          f"GALLERY ID: {gall_id} | GALLERY NAME: {gallery}")
            gall_id = db_ins_gallery(gallery, artist_id)
        junc_id = doesJunctionAlreadyExist(image_id, gall_id)
        if junc_id == -1:
            db_ins_junction(image_id, gall_id)
            print_message("JUNCTION ADDED",
                          f"IMAGE ID: {image_id} | GALLERY NAME: {gallery} | GALLERY ID: {gall_id}")


def getArtistData(_ARTIST_ID, ARTIST_NAME, ARTIST_URL):
    (artist_id, artist_dir) = isArtistAlreadyStored(_ARTIST_ID)
    if artist_id == -1 or artist_dir == "":
        (artist_id, artist_dir) = add_new_artist(_ARTIST_ID, ARTIST_NAME,
                                                 ARTIST_URL)
        if artist_id == -1 or artist_dir == "":
            return (-1, '')
        print_message("ARTIST ADDED", f"ID: {artist_id} | DIR: {artist_dir}")
    return (artist_id, artist_dir)


def add_new_artist(ARTIST_ID, ARTIST_NAME, ARTIST_URL):
    ARTIST_DIRECTORY = create_artist_folder(ARTIST_ID)
    return (db_ins_artist(ARTIST_ID, ARTIST_NAME, ARTIST_URL,
                          ARTIST_DIRECTORY), ARTIST_DIRECTORY)


def create_artist_folder(ARTIST_ID):
    dir_to_make = os.path.join(DA_GALLERY_DIR, ARTIST_ID)
    try:
        os.mkdir(dir_to_make)
    except OSError as error:
        print(error)
        return ""
    return ARTIST_ID


def getImageData(imgPath):
    isImageAlreadyStored
    imgData = {}
    with open(imgPath + '.json') as datafp:
        data = json.load(datafp)
    if ("folders" not in data):
        data['folders'] = ["None"]
    imgData["ARTIST_ID"] = data['author']['userid']
    imgData["ARTIST_NAME"] = data['author']['username']
    imgData["IMAGE_INDEX"] = data['index']
    imgData["IMAGE_TITLE"] = data['title']
    imgData["ARTIST_URL"] = "https://www.deviantart.com/" + data['author'][
        'username']
    imgData["GALLERIES"] = data['folders']
    return imgData


def db_ins_artist(ARTIST_ID, ARTIST_NAME, ARTIST_URL, DIRECTORY_NAME):
    db = db_connect()
    cursor = db.cursor(buffered=True)
    cursor.execute(da_artist_insert_query,
                   (ARTIST_ID, ARTIST_NAME, ARTIST_URL, DIRECTORY_NAME))
    db.commit()
    currentMaxId = cursor.lastrowid
    cursor.close()
    return currentMaxId


def db_ins_image(IMAGE_INDEX, FILENAME, IMAGE_TITLE, LINKED_ARTIST_ID):
    db = db_connect()
    cursor = db.cursor(buffered=True)
    cursor.execute(da_img_insert_query,
                   (IMAGE_INDEX, FILENAME, IMAGE_TITLE, LINKED_ARTIST_ID))
    db.commit()
    currentMaxId = cursor.lastrowid
    cursor.close()

    cursor = db.cursor(buffered=True)
    sql_query = "UPDATE ARTISTS_D SET NUM_IMAGES = NUM_IMAGES + 1 WHERE ID = %s;"
    cursor.execute(sql_query, (LINKED_ARTIST_ID, ))
    db.commit()
    cursor.close()
    db.close()
    return currentMaxId


def db_ins_gallery(GALLERY_NAME, LINKED_ARTIST_ID):
    db = db_connect()
    cursor = db.cursor(buffered=True)
    cursor.execute(da_gallery_insert_query, (GALLERY_NAME, LINKED_ARTIST_ID))
    db.commit()
    currentMaxId = cursor.lastrowid
    cursor.close()
    return currentMaxId


def db_ins_junction(LINKED_IMG_ID, LINKED_GALL_ID):
    db = db_connect()
    cursor = db.cursor(buffered=True)
    cursor.execute(da_junction_insert_query, (LINKED_IMG_ID, LINKED_GALL_ID))
    db.commit()
    currentMaxId = cursor.lastrowid
    cursor.close()

    cursor = db.cursor(buffered=True)
    sql_query = "UPDATE GALLERIES_D SET NUM_IMAGES = NUM_IMAGES + 1 WHERE ID = %s;"
    cursor.execute(sql_query, (LINKED_GALL_ID, ))
    db.commit()
    cursor.close()
    db.close()
    return currentMaxId
