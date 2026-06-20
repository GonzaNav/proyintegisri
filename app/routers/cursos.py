from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.dependencies import get_db, requiere_login
from app.models import Curso, Usuario


router = APIRouter()
templates = None


@router.get("/cursos", response_class=HTMLResponse)
def listar_cursos(request: Request, db: Session = Depends(get_db)):
    cursos = db.query(Curso).order_by(Curso.grado, Curso.seccion).all()
    grados = sorted({c.grado for c in cursos})
    total_alumnos = sum(c.cantidad_alumnos for c in cursos)

    return templates.TemplateResponse(
        request=request,
        name="cursos.html",
        context={
            "titulo": "Cursos",
            "ruta_activa": "cursos",
            "cursos": cursos,
            "total_cursos": len(cursos),
            "total_alumnos": total_alumnos,
            "total_grados": len(grados),
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
            "flash": flash,
        },
    )
