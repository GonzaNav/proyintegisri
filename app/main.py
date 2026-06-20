from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.config import AUTOR, INSTITUCION, SECRET_KEY, STATIC_DIR, TEMPLATES_DIR
from app.database import Base, engine
from app.dependencies import RedirectException
from app.routers import admin, auditoria, auth, cursos, libretas, public


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Libretas.py")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
templates.env.globals["AUTOR"] = AUTOR
templates.env.globals["INSTITUCION"] = INSTITUCION

for modulo in (public, cursos, auth, admin, libretas, auditoria):
    modulo.templates = templates
    app.include_router(modulo.router)


@app.exception_handler(RedirectException)
async def _redirect_handler(request: Request, exc: RedirectException):
    return RedirectResponse(exc.url, status_code=303)
