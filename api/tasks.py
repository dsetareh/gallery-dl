#!/usr/bin/python
import celery, tldextract, da, pixiv, archive, validators
from helpers import *


app = celery.Celery('tasks', broker=CELERY_BROKER, backend=CELERY_BACKEND)
db_init()



def get_all_tasks():
    return celery.current_app.tasks.keys()


def get_da_imgs_by_gallid(gallery_id, page_num):
    return da.getImagesByGalleryIdPaged(gallery_id, page_num)

def get_p_imgs_by_gallid(gallery_id, page_num):
    return pixiv.get_p_imgs_by_gallid(gallery_id, page_num)




def get_da_gall_by_artist(artist_id):
    return da.getGalleriesByArtist(artist_id)

def get_p_gall_by_artist(artist_id):
    return pixiv.get_p_gall_by_artist(artist_id)




def get_da_artists():
    return da.getArtists()

def get_p_artists():
    return pixiv.get_all_artists()




@app.task
def archivePixivArtist(artistId):
    zipFullFilePath = os.path.join(ZIP_DIR, f'{gen_rand_str()}.zip')
    directories, gallery_ids = pixiv.getDirsFromArtistId(artistId)
    mapDirs = map(lambda _dir: os.path.join(GALLERY_DIR, _dir), directories)
    fullDirList = list(mapDirs)
    archive.zip_directories(fullDirList, zipFullFilePath, gallery_ids)
    return zipFullFilePath[6:]

@app.task
def archiveDaArtist(artistId):
    zipFullFilePath = os.path.join(ZIP_DIR, f'{gen_rand_str()}.zip')
    directory, artist_name = da.getDirFromArtistId(artistId)
    directory = os.path.join(DA_GALLERY_DIR, directory)
    archive.zip_directory(directory, zipFullFilePath, artist_name)
    return zipFullFilePath[6:]


@app.task
def get_pixiv_galleries_by_page(page_num):
    return pixiv.get_galleries_by_page(page_num)



@app.task
def add_gallery(gallery_url):
    if not validators.url(gallery_url):
        print_message("error", "invalid gallery url")
        return -1
    parsedURL = tldextract.extract(gallery_url)
    if (parsedURL.domain == "deviantart"):
        return da.add_da_url(gallery_url)
    if (parsedURL.domain == "pixiv"):
        return pixiv.add_pixiv_url(gallery_url)
    return [0,0]

