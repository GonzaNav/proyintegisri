import random

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.dependencies import get_db, requiere_login
from app.models import Alumno, Curso, Institucion, Usuario
from app.utils import auditoria
from app.utils.escala import a_cualitativa, color_cualitativa


router = APIRouter(prefix="/libretas")
templates = None


ESPACIOS = ["Matemática", "Lengua", "Ciencias Sociales", "Ciencias Naturales", "Educación Física"]
EVALUACIONES = ["E1", "E2", "E3", "E4", "Final"]
PERIODOS = ["Primer trimestre", "Segundo trimestre", "Tercer trimestre", "Calificación final"]


def generar_calificaciones(alumno: Alumno, grado: str):
    random.seed(alumno.id)
    filas = []
    for espacio in ESPACIOS:
        notas = []
        for _ in EVALUACIONES[:-1]:
            valor = random.choice([6, 7, 7, 8, 8, 8, 9, 9, 10])
            notas.append(valor)
        promedio = round(sum(notas) / len(notas))
        notas.append(promedio)
        cualitativas = [(n, a_cualitativa(n, grado)) for n in notas]
        filas.append((espacio, cualitativas))
    return filas


@router.get("", response_class=HTMLResponse)
def seleccion_form(
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requiere_login),
):
    cursos = db.query(Curso).order_by(Curso.grado, Curso.seccion).all()
    return templates.TemplateResponse(
        request=request,
        name="libretas_select.html",
        context={
            "titulo": "Libretas",
            "ruta_activa": "libretas",
            "usuario": usuario,
            "cursos": cursos,
            "periodos": PERIODOS,
        },
    )


@router.post("/preview", response_class=HTMLResponse)
def preview(
    request: Request,
    curso_id: int = Form(...),
    periodo: str = Form(...),
    alumno_id: int = Form(...),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requiere_login),
):
    alumno = db.query(Alumno).filter(Alumno.id == alumno_id).first()
    curso = db.query(Curso).filter(Curso.id == curso_id).first()
    institucion = db.query(Institucion).first()

    filas = generar_calificaciones(alumno, curso.grado)
    convivencia = a_cualitativa(random.Random(alumno.id + 1000).choice([7, 8, 9, 10]), curso.grado)

    auditoria.registrar(
        db, request, usuario,
        "Libreta generada",
        f"{alumno.apellido}, {alumno.nombre} ({curso.grado}{curso.seccion}) - {periodo}",
    )

    return templates.TemplateResponse(
        request=request,
        name="libretas_preview.html",
        context={
            "titulo": "Vista previa de libreta",
            "ruta_activa": "libretas",
            "usuario": usuario,
            "alumno": alumno,
            "curso": curso,
            "institucion": institucion,
            "periodo": periodo,
            "espacios": ESPACIOS,
            "evaluaciones": EVALUACIONES,
            "filas": filas,
            "convivencia": convivencia,
            "color_cualitativa": color_cualitativa,
        },
    )


@router.get("/alumnos/{curso_id}")
def alumnos_por_curso(curso_id: int, db: Session = Depends(get_db)):
    """Endpoint JSON usado por el form de seleccion para refrescar la lista de alumnos."""
    alumnos = db.query(Alumno).filter(Alumno.curso_id == curso_id).order_by(Alumno.apellido).all()
    return [{"id": a.id, "texto": f"{a.apellido}, {a.nombre} - Legajo {a.legajo}"} for a in alumnos]
