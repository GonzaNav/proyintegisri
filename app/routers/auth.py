from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models import Usuario
from app.security import verificar_password
from app.utils import auditoria


router = APIRouter()
templates = None


@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    error = request.session.pop("error_login", None)
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"titulo": "Login", "ruta_activa": "login", "error": error},
    )


@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    usuario = db.query(Usuario).filter(Usuario.email == email).first()

    if not usuario or not verificar_password(password, usuario.password_hash):
        request.session["error_login"] = "Email o contraseña incorrectos."
        return RedirectResponse("/login", status_code=303)

    request.session["usuario_id"] = usuario.id
    request.session["usuario_nombre"] = usuario.nombre
    request.session["usuario_rol"] = usuario.rol
    request.session["flash"] = f"Bienvenido, {usuario.nombre}."

    auditoria.registrar(db, request, usuario, "Login", f"Inicio de sesion como {usuario.rol}")
    return RedirectResponse("/dashboard", status_code=303)


@router.get("/logout")
def logout(request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("usuario_id")
    if uid:
        usuario = db.query(Usuario).filter(Usuario.id == uid).first()
        auditoria.registrar(db, request, usuario, "Logout", "Cierre de sesion")
    request.session.clear()
    return RedirectResponse("/", status_code=303)
