import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.database import Base, engine
from model import blueprint, discover, disk, network, project, storage, user # This is for Base to get table context, do not cleanup!!!
from routes import (
    auth,
    blueprint as blueprint_r,
    discover as discover_r,
    locations,
    master,
    project as project_r,
    status,
    storage as storage_r,
    stream,
    vm_types
    ) # import with alias to avoid overrides

Base.metadata.create_all(bind=engine)
app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(blueprint_r.router)
app.include_router(discover_r.router)
app.include_router(locations.router)
app.include_router(master.router)
app.include_router(project_r.router)
app.include_router(status.router)
app.include_router(storage_r.router)
app.include_router(stream.router)
app.include_router(vm_types.router)

#Exception
from exception import handler
from exception.exception import GcpRegionNotFound
#app.register_error_handler(404, handler.page_not_found)
#app.register_error_handler(Exception, handler.internal_server_error)
#app.register_error_handler(GcpRegionNotFound, handler.bad_request)


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)
    # app.run(host='0.0.0.0', port=8000, debug=True, threaded=True)
