from fastapi import FastAPI

from app.core.config import newConfig

app = FastAPI()

config = newConfig()


@app.get("/")
def read_root():
    return {"Hello": config.database.uri}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
