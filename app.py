# Model imports are for fetching table contexts, they are unused here but is necessary.
# The order of model imports needs to be preserved for proper foreign key relations.
# The context can also be loaded from inside the imports given in routes but,
# they needn't necessarily be ordered as required, hence the explicit import.
from model import user, project, mapping, storage, discover, blueprint, disk
# import routes with alias to avoid overrides
from routes import (auth,
                    blueprint as blueprint_r,
                    discover as discover_r,
                    locations, master,
                    project as project_r,
                    status, storage as storage_r,
                    stream,
                    vm_types)
from utils.database import Base, engine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn


Base.metadata.create_all(bind=engine)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)
