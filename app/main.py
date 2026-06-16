from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import AUTOR, INSTITUCION, STATIC_DIR, TEMPLATES_DIR
from app.database import Base, engine
from app.routers import cursos, public


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Libretas.py")

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
templates.env.globals["AUTOR"] = AUTOR
templates.env.globals["INSTITUCION"] = INSTITUCION

public.templates = templates
cursos.templates = templates

app.include_router(public.router)
app.include_router(cursos.router)
