from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.dependencies import get_db, requiere_login
from app.models import Institucion, Usuario
from app.security import hash_password
from app.utils import auditoria


router = APIRouter(prefix="/admin")
templates = None


# --------- USUARIOS ---------

@router.get("/usuarios", response_class=HTMLResponse)
def listar_usuarios(
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requiere_login),
):
    usuarios = db.query(Usuario).order_by(Usuario.nombre).all()
    flash = request.session.pop("flash", None)
    return templates.TemplateResponse(
        request=request,
        name="admin_usuarios.html",
        context={
            "titulo": "Usuarios",
            "ruta_activa": "admin",
            "usuario": usuario,
            "usuarios": usuarios,
            "flash": flash,
        },
    )


@router.get("/usuarios/nuevo", response_class=HTMLResponse)
def nuevo_usuario_form(
    request: Request,
    usuario: Usuario = Depends(requiere_login),
):
    return templates.TemplateResponse(
        request=request,
        name="admin_usuario_form.html",
        context={
            "titulo": "Nuevo usuario",
            "ruta_activa": "admin",
            "usuario": usuario,
            "u": None,
            "accion": "crear",
        },
    )


@router.post("/usuarios")
def crear_usuario(
    request: Request,
    nombre: str = Form(...),
    email: str = Form(...),
    rol: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requiere_login),
):
    nuevo = Usuario(
        nombre=nombre,
        email=email,
        rol=rol,
        password_hash=hash_password(password),
    )
    db.add(nuevo)
    db.commit()

    auditoria.registrar(db, request, usuario, "Usuario creado", f"{nombre} <{email}>")
    request.session["flash"] = f"Usuario {nombre} creado."
    return RedirectResponse("/admin/usuarios", status_code=303)


@router.get("/usuarios/{user_id}/editar", response_class=HTMLResponse)
def editar_usuario_form(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requiere_login),
):
    u = db.query(Usuario).filter(Usuario.id == user_id).first()
    return templates.TemplateResponse(
        request=request,
        name="admin_usuario_form.html",
        context={
            "titulo": "Editar usuario",
            "ruta_activa": "admin",
            "usuario": usuario,
            "u": u,
            "accion": "editar",
        },
    )


@router.post("/usuarios/{user_id}")
def actualizar_usuario(
    user_id: int,
    request: Request,
    nombre: str = Form(...),
    email: str = Form(...),
    rol: str = Form(...),
    password: str = Form(""),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requiere_login),
):
    u = db.query(Usuario).filter(Usuario.id == user_id).first()
    u.nombre = nombre
    u.email = email
    u.rol = rol
    if password:
        u.password_hash = hash_password(password)
    db.commit()

    auditoria.registrar(db, request, usuario, "Usuario editado", f"{nombre} <{email}>")
    request.session["flash"] = f"Usuario {nombre} actualizado."
    return RedirectResponse("/admin/usuarios", status_code=303)


@router.post("/usuarios/{user_id}/eliminar")
def eliminar_usuario(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requiere_login),
):
    u = db.query(Usuario).filter(Usuario.id == user_id).first()
    if u and u.id != usuario.id:
        nombre = u.nombre
        db.delete(u)
        db.commit()
        auditoria.registrar(db, request, usuario, "Usuario eliminado", nombre)
        request.session["flash"] = f"Usuario {nombre} eliminado."
    else:
        request.session["flash"] = "No podés eliminar tu propio usuario."
    return RedirectResponse("/admin/usuarios", status_code=303)


# --------- INSTITUCION ---------

@router.get("/institucion", response_class=HTMLResponse)
def institucion_form(
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requiere_login),
):
    institucion = db.query(Institucion).first()
    flash = request.session.pop("flash", None)
    return templates.TemplateResponse(
        request=request,
        name="admin_institucion.html",
        context={
            "titulo": "Institución",
            "ruta_activa": "admin",
            "usuario": usuario,
            "institucion": institucion,
            "flash": flash,
        },
    )


@router.post("/institucion")
def actualizar_institucion(
    request: Request,
    nombre: str = Form(...),
    cue: str = Form(""),
    cuit: str = Form(""),
    director: str = Form(""),
    vicedirector: str = Form(""),
    secretario: str = Form(""),
    calle: str = Form(""),
    numero: str = Form(""),
    localidad: str = Form(""),
    provincia: str = Form(""),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requiere_login),
):
    institucion = db.query(Institucion).first()
    if not institucion:
        institucion = Institucion(nombre=nombre)
        db.add(institucion)

    institucion.nombre = nombre
    institucion.cue = cue
    institucion.cuit = cuit
    institucion.director = director
    institucion.vicedirector = vicedirector
    institucion.secretario = secretario
    institucion.calle = calle
    institucion.numero = numero
    institucion.localidad = localidad
    institucion.provincia = provincia
    db.commit()

    auditoria.registrar(db, request, usuario, "Institucion editada", nombre)
    request.session["flash"] = "Datos institucionales actualizados."
    return RedirectResponse("/admin/institucion", status_code=303)
