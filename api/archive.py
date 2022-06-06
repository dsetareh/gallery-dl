from helpers import *

archive_insert_query = '''INSERT INTO ARCHIVES_P(ARCHIVE_SIZE, ARCHIVE_FILENAME)VALUES(%s,%s)'''
archive_junction_insert_query = '''INSERT INTO JUNCT_GALL_ARCHIVE_P(LINKED_ARCH_ID, LINKED_GALL_ID)VALUES(%s,%s)'''


def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(
                os.path.join(root, file),
                os.path.relpath(os.path.join(root, file),
                                os.path.join(path, '..')))

def zipdir_a(path, ziph, dir_name):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(
                os.path.join(root, file),
                os.path.join(dir_name, file))

def zip_directory(dir_, zip_name, artist_name):
    zipf = zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED)
    zipdir_a(dir_, zipf, artist_name)
    zipf.close()


def zip_directories(dir_list, zip_name, gallery_ids):
    zipf = zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED)
    for dir in dir_list:
        zipdir(dir, zipf)
    zipf.close()
    zipfsize = getFileSize(zip_name)
    arch_id = db_ins_archive(zipfsize, zip_name)
    for g_id in gallery_ids:
        db_ins_archive_junction(arch_id, g_id)


def db_ins_archive(ARCHIVE_SIZE, ARCHIVE_FILENAME):
    db = db_connect()
    cursor = db.cursor(buffered=True)
    cursor.execute(
        archive_insert_query, (ARCHIVE_SIZE, ARCHIVE_FILENAME))
    db.commit()
    lastrowid = cursor.lastrowid
    cursor.close()
    db.close()
    print_message(
        "archive added",
        f"{ARCHIVE_FILENAME} | {ARCHIVE_SIZE}")
    return lastrowid

def db_ins_archive_junction(LINKED_ARCH_ID, LINKED_GALL_ID):
    db = db_connect()
    cursor = db.cursor(buffered=True)
    cursor.execute(
        archive_junction_insert_query, (LINKED_ARCH_ID, LINKED_GALL_ID))
    db.commit()
    lastrowid = cursor.lastrowid
    cursor.close()
    db.close()
    print_message(
        "archive junction added",
        f"{LINKED_ARCH_ID} | {LINKED_GALL_ID}")
    return lastrowid

def getIDfromArchiveFilename(archFileName):
    db = db_connect()
    cursor = db.cursor(buffered=True)
    sql_query = f"SELECT ID FROM ARCHIVES_P WHERE ARCHIVE_FILENAME = '{archFileName}');"
    cursor.execute(sql_query)
    resultData = cursor.fetchall()
    db.commit()
    cursor.close()
    db.close()
    print(resultData)