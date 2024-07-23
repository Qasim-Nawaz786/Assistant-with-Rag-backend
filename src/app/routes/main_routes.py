from typing import Union

from fastapi import FastAPI
from app.routes.webscrap_routes import router as webscrap_routes


app = FastAPI()

app.include_router(webscrap_routes,prefix="/webscrap")

@app.get('/')
def read_root():
    return {'Hello': 'World'}
