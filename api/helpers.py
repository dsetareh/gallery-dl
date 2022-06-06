import os, datetime, uuid, zipfile, mysql.connector
from PIL import Image, UnidentifiedImageError
from io import StringIO
from html.parser import HTMLParser


################################################ PIXIV #################################################
# p gallery table
artist_p_sql_init_query = '''create table if not exists ARTISTS_P(
    ID INTEGER PRIMARY KEY AUTO_INCREMENT,
    ARTIST_ID INTEGER,
    NUM_IMAGES INTEGER DEFAULT 0,
    ARTIST_NAME TEXT);'''

gallery_p_sql_init_query = '''create table if not exists GALLERIES_P(
    ID INTEGER PRIMARY KEY AUTO_INCREMENT,
    GALLERY_NAME LONGTEXT,
    GALLERY_ARTIST LONGTEXT,
    GALLERY_ID TEXT,
    GALLERY_VIEWS INTEGER,
    NUM_IMAGES INTEGER DEFAULT 0,
    DIRECTORYNAME TEXT,
    GALLERY_URL TEXT,
    DELETED BIT DEFAULT 0,
    CREATED_DATE DATETIME,
    LINKED_ARTIST_ID INTEGER,
    FOREIGN KEY (LINKED_ARTIST_ID) REFERENCES ARTISTS_P (ID),
    DOWNLOADED_DATE DATETIME DEFAULT CURRENT_TIMESTAMP);'''

# p img table
images_p_sql_init_query = '''create table if not exists IMAGES_P(
    ID INTEGER PRIMARY KEY AUTO_INCREMENT,
    IMAGE_NUM INTEGER,
    FILENAME TEXT,
    DELETED BIT DEFAULT 0,
    GALLERY_ID TEXT,
    LINKED_GALLERY_ID INTEGER,
    WIDTH INTEGER,
    HEIGHT INTEGER,
    LINKED_ARTIST_ID INTEGER,
    FOREIGN KEY (LINKED_ARTIST_ID) REFERENCES ARTISTS_P (ID),
    FOREIGN KEY (LINKED_GALLERY_ID) REFERENCES GALLERIES_P (ID));'''

# p archive download table
archive_p_sql_init_query = '''create table if not exists ARCHIVES_P(
    ID INTEGER PRIMARY KEY AUTO_INCREMENT,
    ARCHIVE_SIZE INTEGER,
    ARCHIVE_FILENAME TEXT);'''

# p archive junct table
junction_p_sql_query = '''create table if not exists JUNCT_GALL_ARCHIVE_P(
    ID INTEGER PRIMARY KEY AUTO_INCREMENT,
    LINKED_ARCH_ID INTEGER,
    FOREIGN KEY (LINKED_ARCH_ID) REFERENCES ARCHIVES_P (ID),
    LINKED_GALL_ID INTEGER,
    FOREIGN KEY (LINKED_GALL_ID) REFERENCES GALLERIES_P (ID));'''

################################################ DV #################################################

# d artists table
artists_d_sql_init_query = '''create table if not exists ARTISTS_D(
    ID INTEGER PRIMARY KEY AUTO_INCREMENT,
    ARTIST_ID TEXT,
    ARTIST_NAME TEXT,
    ARTIST_URL TEXT,
    NUM_IMAGES INTEGER DEFAULT 0,
    DIRECTORY_NAME TEXT,
    DELETED BIT DEFAULT 0);'''

# d img table
images_d_sql_init_query = '''create table if not exists IMAGES_D(
    ID INTEGER PRIMARY KEY AUTO_INCREMENT,
    IMAGE_INDEX INTEGER,
    FILENAME TEXT,
    IMAGE_TITLE TEXT,
    DELETED BIT DEFAULT 0,
    LINKED_ARTIST_ID INTEGER,
    FOREIGN KEY (LINKED_ARTIST_ID) REFERENCES ARTISTS_D (ID));'''

# d gallery table
gallery_d_sql_init_query = '''create table if not exists GALLERIES_D(
    ID INTEGER PRIMARY KEY AUTO_INCREMENT,
    GALLERY_NAME LONGTEXT,
    NUM_IMAGES INTEGER DEFAULT 0,
    DELETED BIT DEFAULT 0,
    LINKED_ARTIST_ID INTEGER,
    FOREIGN KEY (LINKED_ARTIST_ID) REFERENCES ARTISTS_D (ID));'''

# d junction table (Images - Galleries)

junction_d_sql_query = '''create table if not exists JUNCT_GALL_IMAGE_D(
    ID INTEGER PRIMARY KEY AUTO_INCREMENT,
    LINKED_IMG_ID INTEGER,
    LINKED_GALL_ID INTEGER,
    FOREIGN KEY (LINKED_IMG_ID) REFERENCES IMAGES_D (ID),
    FOREIGN KEY (LINKED_GALL_ID) REFERENCES GALLERIES_D (ID));'''
####################################################################################################

def db_connect():
    return mysql.connector.connect(host="mysql-db",
                                   port=3306,
                                   user="root",
                                   passwd="asdfasdfasdf",
                                   database="gallerydb",
                                   connection_timeout=20)


def db_init():
    db = db_connect()
    if db:
        print_message("info", "connected to db")
        cursor = db.cursor(buffered=True)
        cursor.execute(artist_p_sql_init_query)
        cursor.execute(gallery_p_sql_init_query)
        cursor.execute(images_p_sql_init_query)
        cursor.execute(archive_p_sql_init_query)
        cursor.execute(junction_p_sql_query)
        

        cursor.execute(artists_d_sql_init_query)
        cursor.execute(images_d_sql_init_query)
        cursor.execute(gallery_d_sql_init_query)
        cursor.execute(junction_d_sql_query)

        db.commit()
        cursor.close()
    else:
        print_message("error", "couldnt connect to db")
        exit()
    db.close()



MAX_WEBP_SIZE = 16382, 16382

GALLERY_DIR = r'./img/'
DA_GALLERY_DIR = r'./img/da/'
ZIP_DIR = r'./img/zip/'
GALLERY_DL = r'gallery-dl'
GALLERY_DL_CONF = r'./gallery-dl.conf'

CELERY_BROKER = os.getenv('CELERY_BROKER')
CELERY_BACKEND = os.getenv('CELERY_BACKEND')

FILE_TYPES = ('.jpg', '.jpeg', '.webp', '.png', '.gif')

MAX_GPAGE_SIZE = 100

def create_folder_if_not_exist(folderpath):
    os.makedirs(folderpath, exist_ok=True)


def getFileSize(filePath):
    return os.stat(filePath).st_size

class MLStripper(HTMLParser):

    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    raise TypeError("Unknown type")


def print_message(type, msg):
    print(f"[{type.upper()}] : {msg.upper()}")


def gen_rand_str(randstr_len=8):
    return str(uuid.uuid4())[:randstr_len]


def webp_conv_and_move(tmpImagePath, finalImagePath):
    try:
        Image.MAX_IMAGE_PIXELS = 933120000
        image = Image.open(tmpImagePath)
        image = image.convert("RGBA")
        image.thumbnail(MAX_WEBP_SIZE, Image.LANCZOS)
        imgInfo = image.info
        image.save(finalImagePath,
                   format='webp',
                   lossless=False,
                   quality=75,
                   method=6,
                   **imgInfo)
    except UnidentifiedImageError:
        print_message('error', f"{tmpImagePath} not supported")
        return 0
    return 1