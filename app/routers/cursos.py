from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.dependencies import get_db, requiere_login
from app.models import Alumno, Curso, EventoAuditoria, Usuario


router = APIRouter()
templates = None


@router.get("/cursos", response_class=HTMLResponse)
def listar_cursos(
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requiere_login),
):
    cursos = db.query(Curso).order_by(Curso.grado, Curso.seccion).all()
    grados = sorted({c.grado for c in cursos})
    total_alumnos = sum(c.cantidad_alumnos for c in cursos)

    return templates.TemplateResponse(
        request=request,
        name="cursos.html",
        context={
            "titulo": "Cursos",
            "ruta_activa": "cursos",
            "usuario": usuario,
            "cursos": cursos,
            "total_cursos": len(cursos),
            "total_alumnos": total_alumnos,
            "total_grados": len(grados),
        },
    )


@router.get("/cursos/{curso_id}/alumnos", response_class=HTMLResponse)
def alumnos_del_curso(
    curso_id: int,
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requiere_login),
):
    curso = db.query(Curso).filter(Curso.id == curso_id).first()
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    alumnos = (
        db.query(Alumno)
        .filter(Alumno.curso_id == curso_id)
        .order_by(Alumno.apellido, Alumno.nombre)
        .all()
    )
    return templates.TemplateResponse(
        request=request,
        name="alumnos_curso.html",
        context={
            "titulo": f"Alumnos {curso.grado} {curso.seccion}",
            "ruta_activa": "cursos",
            "usuario": usuario,
            "curso": curso,
            "alumnos": alumnos,
        },
    )


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requiere_login),
):
    cursos = db.query(Curso).all()
    grados = sorted({c.grado for c in cursos})
    total_alumnos = sum(c.cantidad_alumnos for c in cursos)
    total_libretas = db.query(EventoAuditoria).filter(
        EventoAuditoria.accion == "Libreta generada"
    ).count()
    flash = request.session.pop("flash", None)

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "titulo": "Dashboard",
            "ruta_activa": "dashboard",
            "usuario": usuario,
            "total_cursos": len(cursos),
            "total_alumnos": total_alumnos,
            "total_grados": len(grados),
            "total_libretas": total_libretas,
            "flash": flash,
        },
    )
