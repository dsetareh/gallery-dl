# gallery-dl webui thing

accepts gallery urls from webui, worker picks it up

worker runs gallery-dl with full metadata generation

worker parses metadata, loads imagedata into db tables (IMAGES, GALLERIES, ARTISTS)

webui allows navigation from artist => gallery => image level

also allows archive generation (worker generated) only at artist level for now

api endpoints:
```py
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

/gallery - request url download
app.add_route('/tasks/gallery', Tasks(), suffix='download')

# ALL OF THESE DO THE SAME THING
# GET /tasks/{task_id} -  check task_id's status
# GET /tasks/gallery/{task_id} -  check task_id's status
# GET /tasks/archive/{task_id} - check task_id's status
app.add_route('/tasks/{task_id}', Tasks())
app.add_route('/tasks/gallery/{task_id}', Tasks())
app.add_route('/tasks/parchive/{task_id}', Tasks())
app.add_route('/tasks/darchive/{task_id}', Tasks())
```


### dont try to run this
needs gallery-dl.conf in ./api/, get a default one from here:
` https://raw.githubusercontent.com/mikf/gallery-dl/master/docs/gallery-dl.conf `

needs dirs to exist under uid/gid 1000:
```
api/logs # celery logs
api/db # sql db
api/img # all images (root dir p source)
api/img/zip # archives
api/img/da # da source
```



nginx proxies mounted npm devenv including node_modules so `npm install` in ui

unicode support soon™
