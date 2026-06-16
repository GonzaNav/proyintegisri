from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models import Curso


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
