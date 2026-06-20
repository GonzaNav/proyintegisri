import random

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.dependencies import get_db, requiere_login
from app.models import Alumno, Curso, Institucion, Usuario
from app.utils import auditoria
from app.utils.escala import (
    calificar_area,
    calificar_convivencia,
    calificar_inasistencia,
    color,
    es_primer_ciclo,
)


router = APIRouter(prefix="/libretas")
templates = None


# Espacios curriculares por ciclo
AREAS_PRIMER_CICLO = [
    "Lengua",
    "Matemática",
    "Ambiente Social y Natural",
    "Educación Física",
    "Educación Artística",
]

AREAS_SEGUNDO_CICLO = [
    "Lengua",
    "Lectura",
    "Matemática",
    "Ciencias Sociales",
    "Ciencias Naturales",
    "Educación Física",
    "Educación Artística",
    "Educación Tecnológica",
]

TRIMESTRES = ["1°T", "2°T", "3°T"]
PERIODOS = ["Primer trimestre", "Segundo trimestre", "Tercer trimestre", "Calificación final"]

# Cuantos trimestres tiene completos cada periodo
PERIODO_TRIMESTRES = {
    "Primer trimestre": 1,
    "Segundo trimestre": 2,
    "Tercer trimestre": 3,
    "Calificación final": 3,
}


def _nota_simulada(rnd: random.Random, base: int = 7) -> int:
    """Genera una nota numerica simulada entre 6 y 10."""
    return rnd.choice([base, base, base + 1, base + 1, base + 1, base + 2, base + 2, base + 3])


def construir_datos_libreta(alumno: Alumno, curso: Curso, periodo: str):
    """Genera los datos de la libreta segun el ciclo (1°-2° o 3°-6°).

    Las celdas se llenan de manera progresiva: solo los trimestres
    correspondientes al periodo seleccionado tienen valor; el resto queda
    vacio. La columna/fila "Final" solo se completa cuando el periodo es
    "Calificación final".
    """
    rnd = random.Random(alumno.id)
    primer_ciclo = es_primer_ciclo(curso.grado)
    areas = AREAS_PRIMER_CICLO if primer_ciclo else AREAS_SEGUNDO_CICLO

    trim_completos = PERIODO_TRIMESTRES.get(periodo, 3)
    mostrar_final = periodo == "Calificación final"

    def _celda(valor):
        return {"valor": valor, "color": color(valor)}

    def _vacia():
        return {"valor": "", "color": ""}

    # Notas por area y trimestre
    notas_areas = []
    for area in areas:
        trimestrales = []
        notas_reales = []
        for idx in range(len(TRIMESTRES)):
            nota = _nota_simulada(rnd)
            if idx < trim_completos:
                valor = calificar_area(nota, curso.grado, area)
                trimestrales.append({"nota": nota, "valor": valor, "color": color(valor)})
                notas_reales.append(nota)
            else:
                trimestrales.append({"nota": None, "valor": "", "color": ""})

        if mostrar_final and notas_reales:
            prom = round(sum(notas_reales) / len(notas_reales))
            final_valor = calificar_area(prom, curso.grado, area)
            final = {"nota": prom, "valor": final_valor, "color": color(final_valor)}
        else:
            final = {"nota": None, "valor": "", "color": ""}

        notas_areas.append({
            "area": area,
            "trimestres": trimestrales,
            "final": final,
        })

    # Items de convivencia / asistencia por trimestre
    if primer_ciclo:
        # 1° ciclo: Convivencia (C), Asistencias (P), Inasistencias (I)
        convivencia_items = [
            ("Convivencia", "C", calificar_convivencia),
            ("Asistencias", "P", lambda n, g: str(int(n))),
            ("Inasistencias", "I", lambda n, g: calificar_inasistencia(n)),
        ]
    else:
        # 2° ciclo: Convivencia con 4 dimensiones + Inasistencias detalladas + Tardanzas
        convivencia_items = [
            ("Comportamiento", "C", calificar_convivencia),
            ("Esfuerzo", "E", calificar_convivencia),
            ("Respeto", "R", calificar_convivencia),
            ("Integración grupal", "I", calificar_convivencia),
            ("Inasistencias justificadas", "IJ", lambda n, g: calificar_inasistencia(n)),
            ("Inasistencias injustificadas", "II", lambda n, g: calificar_inasistencia(n)),
            ("Tardanzas", "T", lambda n, g: calificar_inasistencia(n)),
        ]

    convivencia = []
    for nombre, prefijo, fn in convivencia_items:
        valores = []
        for idx in range(len(TRIMESTRES)):
            if idx >= trim_completos:
                valores.append(_vacia())
                continue
            if prefijo in ("I", "IJ", "II", "T"):
                nota = rnd.choice([0, 0, 1, 1, 2, 3])
                valor = fn(nota, curso.grado) if callable(fn) else str(int(nota))
            elif prefijo == "P":
                nota = rnd.choice([55, 58, 60, 62, 65])
                valor = str(nota)
            else:
                nota = _nota_simulada(rnd, base=7)
                valor = fn(nota, curso.grado)
            valores.append(_celda(valor))
        convivencia.append({"nombre": nombre, "prefijo": prefijo, "trimestres": valores})

    return {
        "primer_ciclo": primer_ciclo,
        "ciclo_texto": "Primer Ciclo" if primer_ciclo else "Segundo Ciclo",
        "areas": notas_areas,
        "convivencia": convivencia,
        "trimestres": TRIMESTRES,
        "trimestres_completos": trim_completos,
        "mostrar_final": mostrar_final,
        "periodo": periodo,
    }


@router.get("", response_class=HTMLResponse)
def seleccion_form(
    request: Request,
    curso_id: int | None = None,
    alumno_id: int | None = None,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requiere_login),
):
    cursos = db.query(Curso).order_by(Curso.grado, Curso.seccion).all()
    alumnos_curso = []
    if curso_id:
        alumnos_curso = (
            db.query(Alumno)
            .filter(Alumno.curso_id == curso_id)
            .order_by(Alumno.apellido, Alumno.nombre)
            .all()
        )
    return templates.TemplateResponse(
        request=request,
        name="libretas_select.html",
        context={
            "titulo": "Libretas",
            "ruta_activa": "libretas",
            "usuario": usuario,
            "cursos": cursos,
            "periodos": PERIODOS,
            "curso_id_sel": curso_id,
            "alumno_id_sel": alumno_id,
            "alumnos_curso": alumnos_curso,
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

    datos = construir_datos_libreta(alumno, curso, periodo)

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
            "datos": datos,
        },
    )


@router.get("/alumnos/{curso_id}")
def alumnos_por_curso(
    curso_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requiere_login),
):
    alumnos = db.query(Alumno).filter(Alumno.curso_id == curso_id).order_by(Alumno.apellido).all()
    return [{"id": a.id, "texto": f"{a.apellido}, {a.nombre} - Legajo {a.legajo}"} for a in alumnos]
