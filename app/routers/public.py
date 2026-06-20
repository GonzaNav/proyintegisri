from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse


router = APIRouter()
templates = None


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={"titulo": "Inicio", "ruta_activa": "home"},
    )
