import fastapi
import http

import birblog.database.actions as blg_act
from birblog.database.models import Bird


def create_application(database_url: str) -> fastapi.FastAPI:
    app = fastapi.FastAPI(version="1.0.0", docs_url="/api/docs")
    

    @app.get("/bird/{bird_id}", response_model=Bird)
    async def get_bird_entry(bird_id: int) -> None:
        if not (_bird := blg_act.get_bird(bird_id, database_url)):
            raise fastapi.HTTPException(
                status_code=http.HTTPStatus.NOT_FOUND, detail="No such bird."
            )
        return _bird
    
    @app.post("/bird", response_model=Bird)
    async def add_bird(bird_name: str) -> None:
        return blg_act.add_bird(database_url, bird_name)
    
    return app
