import os, subprocess, json, traceback, logging, tempfile
from helpers import *
import dateutil.parser

pixiv_gallery_insert_query = '''INSERT INTO GALLERIES_P (GALLERY_NAME, GALLERY_ARTIST, GALLERY_ID, GALLERY_VIEWS, DIRECTORYNAME, GALLERY_URL, CREATED_DATE, LINKED_ARTIST_ID)
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s)'''
pixiv_image_insert_query = '''INSERT INTO IMAGES_P(LINKED_GALLERY_ID, IMAGE_NUM, FILENAME, GALLERY_ID, WIDTH, HEIGHT, LINKED_ARTIST_ID)VALUES(%s,%s,%s,%s,%s,%s,%s)'''
pixiv_artist_insert_query = '''INSERT INTO ARTISTS_P(ARTIST_ID, ARTIST_NAME)VALUES(%s,%s)'''


def getDirsFromArtistIdQuery(artistid):
    return (
        f"SELECT DIRECTORYNAME, ID "
        f"FROM GALLERIES_P "
        f"WHERE LINKED_ARTIST_ID = {artistid}; "
    )

def getDirsFromArtistId(artistId):
    db = db_connect()
    cursor = db.cursor(buffered=True)
    cursor.execute(getDirsFromArtistIdQuery(artistId))
    resultData = cursor.fetchall()
    db.commit()
    cursor.close()
    db.close()
    dirs = []
    g_ids = []
    for ent in resultData:
        dirs.append(ent[0])
        g_ids.append(ent[1])
    return (dirs, g_ids)

def get_p_imgs_by_gallid_query(gallery_id, page_num):
    return (
        f"SELECT g.DIRECTORYNAME, i.IMAGE_NUM, i.FILENAME, i.WIDTH, i.HEIGHT, i.LINKED_ARTIST_ID "
        f"FROM IMAGES_P i "
        f"INNER JOIN (SELECT * "
        f"FROM GALLERIES_P "
        f"GROUP BY ID) AS g "
        f"WHERE g.ID = {gallery_id} AND i.LINKED_GALLERY_ID = {gallery_id} "
        f"LIMIT {MAX_GPAGE_SIZE} OFFSET {MAX_GPAGE_SIZE * page_num};"
    )   


def get_p_imgs_by_gallid(gallery_id, page_num):
    db = db_connect()
    cursor = db.cursor(buffered=True, dictionary=True)
    cursor.execute(get_p_imgs_by_gallid_query(gallery_id, page_num))
    resultData = cursor.fetchall()
    db.commit()
    cursor.close()
    db.close()
    return resultData


def get_p_gall_by_artist_query(artist_id):
    return (
        f"SELECT g.ID, g.GALLERY_NAME, g.NUM_IMAGES, g.GALLERY_VIEWS, g.DIRECTORYNAME, g.GALLERY_URL, g.CREATED_DATE, i.FILENAME, i.WIDTH, i.HEIGHT "
        f"FROM GALLERIES_P g  "
        f"INNER JOIN (SELECT * "
        f"FROM IMAGES_P "
        f"GROUP BY LINKED_GALLERY_ID) AS i "
        f"WHERE i.LINKED_GALLERY_ID = g.ID AND g.LINKED_ARTIST_ID  = {artist_id} AND i.LINKED_ARTIST_ID = {artist_id}; "
    )



def get_p_gall_by_artist(artist_id):
    db = db_connect()
    cursor = db.cursor(buffered=True, dictionary=True)
    cursor.execute(get_p_gall_by_artist_query(artist_id))
    resultData = cursor.fetchall()
    db.commit()
    cursor.close()
    db.close()
    return resultData




pixiv_get_all_artists_query = (
    "SELECT a.ID, a.ARTIST_ID, a.ARTIST_NAME, a.NUM_IMAGES, i.FILENAME, i.WIDTH, i.HEIGHT, g.DIRECTORYNAME  "
    "FROM ARTISTS_P a   "
    "INNER JOIN (SELECT *    "
    "FROM IMAGES_P    "
    "GROUP BY LINKED_ARTIST_ID) AS i   "
    "INNER JOIN (SELECT *    "
    "FROM GALLERIES_P) AS g   "
    "WHERE i.LINKED_ARTIST_ID = a.ID AND i.LINKED_GALLERY_ID = g.ID;  "
)

def get_all_artists():
    db = db_connect()
    cursor = db.cursor(buffered=True, dictionary=True)
    cursor.execute(pixiv_get_all_artists_query)
    resultData = cursor.fetchall()
    db.commit()
    cursor.close()
    db.close()
    return resultData


def getGalleriesByPageSqlQuery(pageNumber):
    return (
        f"SELECT g.ID, g.GALLERY_URL, g.DIRECTORYNAME, g.NUM_IMAGES, i.FILENAME, i.WIDTH, i.HEIGHT g.ARTIST_ID, g.GALLERY_ID, g.CREATED_DATE "
        f"FROM GALLERIES_P g "
        f"INNER JOIN IMAGES_P i ON g.ID = i.LINKED_GALLERY_ID "
        f"WHERE i.IMAGE_NUM = 0 "
        f"ORDER BY g.DOWNLOADED_DATE DESC LIMIT {MAX_GPAGE_SIZE} OFFSET {pageNumber * MAX_GPAGE_SIZE};"
    )

def add_pixiv_url(gallery_url):
    print_message("ADD", f"adding {gallery_url}")

    tempdir = tempfile.TemporaryDirectory()

    download_info = download_gallery(gallery_url, tempdir.name)

    if len(download_info) == 0:
        return -1

    num_galleries_added = 0
    num_images_added = 0
    for gallery_info in download_info:
        if galleryIdAlreadyStored(gallery_info['GALLERY_ID']):
            continue
        gallery_info = create_gallery_folder(gallery_info)
        if (gallery_info['DIRECTORYNAME'] == ""):
            continue
        artist_db_id = create_artist_if_not_exist(gallery_info)
        gallery_info["DB_ID"] = db_ins_gallery(
            gallery_info["GALLERY_NAME"],
            gallery_info["GALLERY_ARTIST"], 
            gallery_info['GALLERY_ID'],
            gallery_info['GALLERY_VIEWS'],
            gallery_info["DIRECTORYNAME"], 
            gallery_info["GALLERY_URL"],
            gallery_info['CREATED_DATE'],
            artist_db_id)
        num_galleries_added += 1
        num_images_added += addImages(gallery_info, tempdir.name, artist_db_id)
    tempdir.cleanup()
    return [num_galleries_added, num_images_added]

def create_artist_if_not_exist(gall_data):
    existing_id = get_artist_db_id(gall_data['ARTIST_ID'])
    if existing_id != -1:
        return existing_id
    return db_ins_artist(gall_data['ARTIST_ID'], gall_data['ARTIST_NAME'])
    


def get_artist_db_id(artist_id):
    db = db_connect()
    cursor = db.cursor(buffered=True)
    cursor.execute(
        f"SELECT ID, ARTIST_NAME FROM ARTISTS_P WHERE ARTIST_ID = {artist_id} LIMIT 1;"
    )
    data = cursor.fetchall()
    cursor.close()
    if len(data) == 0:
        return -1
    return data[0][0]

def db_ins_artist(ARTIST_ID, ARTIST_NAME):
    db = db_connect()
    cursor = db.cursor(buffered=True)
    cursor.execute(
        pixiv_artist_insert_query, (ARTIST_ID, ARTIST_NAME))
    db.commit()
    print_message(
        "pixiv artist added",
        f"{ARTIST_ID} | {ARTIST_NAME} ")
    lastrowid = cursor.lastrowid
    cursor.close()
    db.close()
    return lastrowid

def db_ins_gallery(GALLERY_NAME, GALLERY_ARTIST, GALLERY_ID,
                   GALLERY_VIEWS, DIRECTORYNAME, GALLERY_URL, CREATED_DATE, LINKED_ARTIST_ID):
    db = db_connect()
    cursor = db.cursor(buffered=True)
    cursor.execute(
        pixiv_gallery_insert_query, ( GALLERY_NAME, GALLERY_ARTIST, GALLERY_ID,
                GALLERY_VIEWS, DIRECTORYNAME, GALLERY_URL, CREATED_DATE, LINKED_ARTIST_ID))
    db.commit()
    print_message(
        "gallery added",
        f"{GALLERY_ID} | {DIRECTORYNAME} | {GALLERY_URL}")
    lastrowid = cursor.lastrowid
    cursor.close()
    db.close()
    return lastrowid


def db_ins_image(GALLERY_DB_ID, IMAGE_NUM, FILENAME, GALLERY_ID, WIDTH, HEIGHT, LINKED_ARTIST_ID):
    db = db_connect()
    cursor = db.cursor(buffered=True)
    cursor.execute(pixiv_image_insert_query, (GALLERY_DB_ID, IMAGE_NUM, FILENAME, GALLERY_ID, WIDTH, HEIGHT, LINKED_ARTIST_ID))
    db.commit()
    currentMaxId = cursor.lastrowid
    cursor.close()

    cursor = db.cursor(buffered=True)
    sql_query = "UPDATE GALLERIES_P SET NUM_IMAGES = NUM_IMAGES + 1 WHERE ID = %s;"
    cursor.execute(sql_query, (GALLERY_DB_ID, ))
    db.commit()
    cursor.close()

    cursor = db.cursor(buffered=True)
    sql_query = "UPDATE ARTISTS_P SET NUM_IMAGES = NUM_IMAGES + 1 WHERE ID = %s;"
    cursor.execute(sql_query, (LINKED_ARTIST_ID, ))
    db.commit()
    cursor.close()
    db.close()
    return currentMaxId

def getDirsFromGalleryIds(galleryIdArray):
    db = db_connect()
    cursor = db.cursor(buffered=True)
    queryArgs = ""
    for gId in galleryIdArray:
        queryArgs += str(gId) + ","

    sql_query = f"SELECT DIRECTORYNAME FROM GALLERIES_P WHERE ID IN ({queryArgs[:-1]});"
    cursor.execute(sql_query)
    resultData = cursor.fetchall()
    mapTuple = map(lambda tup: tup[0], resultData)
    fullDirList = list(mapTuple)
    db.commit()
    cursor.close()
    db.close()
    return fullDirList


def galleryIdAlreadyStored(galleryId):
    db = db_connect()
    cursor = db.cursor(buffered=True)
    cursor.execute(f"SELECT * FROM GALLERIES_P WHERE GALLERY_ID = '{galleryId}';")
    data = cursor.fetchall()
    cursor.close()
    return (len(data) > 0)


def getInfoOnDownloadContents(galleryIdArray, tempdir):
    galleryInfoArray = []
    for galleryId in galleryIdArray:
        try:
            galleryInfo = open(
                os.path.join(tempdir, galleryIdArray[galleryId][0] + ".json"))
            galleryJson = json.load(galleryInfo)
            galleryInfo.close()
        except:
            print("Error loading galleryInfo")
            continue

        galleryInfo = {}
        galleryInfo['GALLERY_NAME'] = galleryJson['title']
        galleryInfo['GALLERY_ARTIST'] = galleryJson['user']['name']
        galleryInfo['ARTIST_ID'] = galleryJson['user']['id']
        galleryInfo['GALLERY_ID'] = galleryJson['id']
        galleryInfo['GALLERY_VIEWS'] = galleryJson['total_view']
        galleryInfo['tempdirImagefilenames'] = galleryIdArray[galleryId]
        galleryInfo['NUM_FILES'] = len(galleryIdArray[galleryId])
        galleryInfo['CREATED_DATE'] = dateutil.parser.isoparse(
            galleryJson["create_date"]).strftime('%Y-%m-%d %H:%M:%S')
        galleryInfo[
            'GALLERY_URL'] = 'https://www.pixiv.net/en/artworks/' + galleryId

        galleryInfo['ARTIST_NAME'] = galleryJson['user']['account']
        galleryInfo['HEIGHT'] = galleryJson['height']
        galleryInfo['WIDTH'] = galleryJson['width']
        galleryInfoArray.append(galleryInfo)
    return galleryInfoArray


def getGalleriesInDir(dir):
    uniqueGalleryIds = {}
    # iterating over all files
    for entry in os.scandir(dir):
        if entry.is_dir() or not entry.name.endswith(FILE_TYPES):
            # skip directories
            continue
        uniqueGalleryIds.setdefault(entry.name.split("_")[0],
                                    []).append(entry.name)
    return uniqueGalleryIds


def download_gallery(gallery_url, tempdir):
    print_message("exec", "gallery-dl")
    result = subprocess.Popen([
        GALLERY_DL, "--write-metadata", "-c", GALLERY_DL_CONF, "-D", tempdir,
        gallery_url
    ],
                              text=True)

    result.wait()
    print_message("exit", "gallery-dl")
    if result.returncode != 0:
        print_message("error", "unable to dl gallery, check stdout")
        return 0
    galleryIdArray = getGalleriesInDir(tempdir)
    gallery_info = getInfoOnDownloadContents(galleryIdArray, tempdir)
    return gallery_info
    
def create_gallery_folder(gallery_info):
    gallery_info[
        'DIRECTORYNAME'] = f"{gallery_info['GALLERY_ID']}_{gen_rand_str()}"
    try:
        os.mkdir(os.path.join(GALLERY_DIR, gallery_info['DIRECTORYNAME']))
    except OSError as error:
        print(error)
        gallery_info['DIRECTORYNAME'] = ""
    return gallery_info


def addImages(gallery_info, tempBaseDir, artist_db_id):
    num_images_added = 0
    for idx, tmpImageFileName in enumerate(
            gallery_info['tempdirImagefilenames']):
        # convert and move
        newfname = f"p{idx}_{gallery_info['GALLERY_ID']}_{gen_rand_str()}"
        webp_conv_and_move(
            os.path.join(tempBaseDir, tmpImageFileName),
            os.path.join(GALLERY_DIR, gallery_info['DIRECTORYNAME'],
                         f"{newfname}") + '.webp')
        # add to db
        try:
            db_ins_image(gallery_info["DB_ID"], idx, newfname,
                         gallery_info['GALLERY_ID'], gallery_info['WIDTH'], gallery_info['HEIGHT'], artist_db_id)
        except Exception as e:
            logging.error(traceback.format_exc())
            continue
        num_images_added += 1
    return num_images_added

def get_galleries_by_page(page_num):
    db = db_connect()
    cursor = db.cursor(buffered=True, dictionary=True)
    cursor.execute(getGalleriesByPageSqlQuery(page_num))
    resultData = cursor.fetchall()
    db.commit()
    cursor.close()
    db.close()
    return resultData