import json, falcon
from tasks import *
from celery.result import AsyncResult
from helpers import datetime_handler


class Galleries(object):
    def on_get_da(self, req, resp, art_id):
        result = get_da_gall_by_artist(art_id)
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(result)
    def on_get_p(self, req, resp, art_id):
        result = get_p_gall_by_artist(art_id)
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(result, default=datetime_handler)

class Images(object):
    def on_get_da(self, req, resp, gall_id):
        page_num = -1
        for key, value in req.params.items():
            if key == "p":
                page_num = int(value)
        if page_num == -1:
            resp.status = falcon.HTTP_400
            resp.body = json.dumps({"error": "no page number requested"})
        else:
            result = get_da_imgs_by_gallid(gall_id, page_num)
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(result)
    def on_get_p(self, req, resp, gall_id):
        page_num = -1
        for key, value in req.params.items():
            if key == "p":
                page_num = int(value)
        if page_num == -1:
            resp.status = falcon.HTTP_400
            resp.body = json.dumps({"error": "no page number requested"})
        else:
            result = get_p_imgs_by_gallid(gall_id, page_num)
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(result, default=datetime_handler)

class Artists(object):
    def on_get_da(self, req, resp):
        result = get_da_artists()
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(result)
    def on_get_p(self, req, resp):
        result = get_p_artists()
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(result, default=datetime_handler)


class Archive(object):
    def on_post_p(self, req, resp):
        raw_data = json.load(req.bounded_stream)
        artistID = raw_data.get('artistID')
        # start task
        task = archivePixivArtist.delay(artistID)
        resp.status = falcon.HTTP_200
        result = {
            'status': 'success',
            'data': {
                'task_id': task.id,
            }
        }
        # return task_id to client
        resp.text = json.dumps(result)
        
    def on_post_da(self, req, resp):
        raw_data = json.load(req.bounded_stream)
        artistID = raw_data.get('artistID')
        # start task
        task = archiveDaArtist.delay(artistID)
        resp.status = falcon.HTTP_200
        result = {
            'status': 'success',
            'data': {
                'task_id': task.id,
            }
        }
        # return task_id to client
        resp.text = json.dumps(result)

class Tasks(object):
    def on_post_download(self, req, resp):
        raw_data = json.load(req.bounded_stream)
        gallery_url = raw_data.get('gallery_url')
        # start task
        task = add_gallery.delay(gallery_url)
        resp.status = falcon.HTTP_200
        result = {'status': task.status, 'task_id': task.id}
        # return task_id to client
        resp.text = json.dumps(result)
    def on_get(self, req, resp, task_id):
        if task_id == "":
            resp.status = falcon.HTTP_400
            resp.body = json.dumps({"error": "no task id requested"})
        else:
            task_result = AsyncResult(task_id)
            result = {
                'status': task_result.status,
                'result': task_result.result
            }
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(result)


app = falcon.App(cors_enable=True)



# ================== DA ==================

# GET: request Artist data
app.add_route('/da/artists', Artists(), suffix="da")
# GET: request Gallery Data by Artist
app.add_route('/da/gallery/{art_id}', Galleries(), suffix="da")
# GET: request Image Data by Gallery
app.add_route('/da/gallery/images/{gall_id}', Images(), suffix="da")



# POST /tasks/archive - request archive creation (by artist_db_id for now)
app.add_route('/tasks/darchive', Archive(), suffix="da")
# ========================================


# ================== PIXIV ==================
# GET: request Artist data
app.add_route('/pixiv/artists', Artists(), suffix="p")
# GET: request Gallery Data by Artist
app.add_route('/pixiv/gallery/{art_id}', Galleries(), suffix="p")
# GET: request Image Data by Gallery
app.add_route('/pixiv/gallery/images/{gall_id}', Images(), suffix="p")


# POST /tasks/archive - request archive creation (by artist_db_id for now)
app.add_route('/tasks/parchive', Archive(), suffix='p')
# ========================================




# POST /tasks/gallery - request url download
app.add_route('/tasks/gallery', Tasks(), suffix='download')

# ALL OF THESE DO THE SAME THING
# GET /tasks/{task_id} -  check task_id's status
# GET /tasks/gallery/{task_id} -  check task_id's status
# GET /tasks/archive/{task_id} - check task_id's status
app.add_route('/tasks/{task_id}', Tasks())
app.add_route('/tasks/gallery/{task_id}', Tasks())
app.add_route('/tasks/parchive/{task_id}', Tasks())
app.add_route('/tasks/darchive/{task_id}', Tasks())

