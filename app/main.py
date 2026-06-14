from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import AUTOR, INSTITUCION, STATIC_DIR, TEMPLATES_DIR
from app.routers import public


app = FastAPI(title="Libretas.py")

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
templates.env.globals["AUTOR"] = AUTOR
templates.env.globals["INSTITUCION"] = INSTITUCION

public.templates = templates

app.include_router(public.router)
