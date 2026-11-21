"""Consultas sobre la logica de negocio de Libretas.py.

Reutiliza las mismas piezas que la aplicacion web, para que el bot y la web
muestren siempre lo mismo:
- app/utils/escala.py: regla de conversion de notas a escala cualitativa.
- app/models: cursos y alumnos de la base del sistema.
- construir_datos_libreta(): arma la libreta de un alumno para un periodo.

No depende de Telegram: devuelve datos o texto HTML listo para enviar.
"""

import html
import re
import unicodedata
from dataclasses import dataclass

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Alumno, Curso
from app.routers.libretas import PERIODOS, construir_datos_libreta
from app.utils.escala import (
    calificar_area,
    calificar_convivencia,
    es_primer_ciclo,
)

GRADOS = ("1°", "2°", "3°", "4°", "5°", "6°")

# Codigo corto de periodo (se usa en comandos y botones) -> nombre del periodo en la app.
PERIODOS_CORTOS = {
    "1": "Primer trimestre",
    "2": "Segundo trimestre",
    "3": "Tercer trimestre",
    "f": "Calificación final",
}
assert set(PERIODOS_CORTOS.values()) == set(PERIODOS)

_ORDINALES = {"primer": 1, "primero": 1, "segundo": 2, "tercer": 3, "tercero": 3, "cuarto": 4, "quinto": 5, "sexto": 6}
_SUFIJO_GRADO = r"(?:°|º|ro|do|er|to|mo|vo)?"


# ----------------------------------------------------------------------
# Interpretacion de texto
# ----------------------------------------------------------------------
def simplificar(texto: str) -> str:
    """Minusculas y sin tildes, pero conservando numeros, comas y el simbolo de grado."""
    texto = unicodedata.normalize("NFD", texto.lower().replace("º", "°"))
    return "".join(c for c in texto if unicodedata.category(c) != "Mn" or c == "°")


def leer_grado(texto: str) -> str | None:
    """'2', '2°', '2do', 'segundo' -> '2°'."""
    t = simplificar(texto).strip()
    m = re.fullmatch(rf"([1-6])\s*{_SUFIJO_GRADO}(?:\s*grado)?", t)
    if m:
        return f"{m.group(1)}°"
    m = re.fullmatch(r"(\w+)(?:\s*grado)?", t)
    if m and m.group(1) in _ORDINALES:
        return f"{_ORDINALES[m.group(1)]}°"
    return None


def leer_nota(texto: str) -> float | None:
    """'8', '8,5', '8.5' -> 8.0 / 8.5. Solo acepta valores entre 0 y 10."""
    t = texto.strip().replace(",", ".")
    if not re.fullmatch(r"\d{1,2}(?:\.\d{1,2})?", t):
        return None
    nota = float(t)
    return nota if 0 <= nota <= 10 else None


def leer_curso(texto: str) -> tuple[str, str] | None:
    """'3A', '3°A', '3 a', '3° b' -> ('3°', 'A')."""
    m = re.fullmatch(rf"([1-6])\s*{_SUFIJO_GRADO}\s*([ab])", simplificar(texto).strip())
    return (f"{m.group(1)}°", m.group(2).upper()) if m else None


@dataclass
class Intencion:
    tipo: str                    # "convertir" | "libreta" | "cursos" | "alumnos" | "buscar"
    texto: str | None = None
    nota: float | None = None
    grado: str | None = None
    area: str | None = None
    legajo: str | None = None
    curso: tuple[str, str] | None = None


def interpretar(mensaje: str) -> Intencion | None:
    """Detecta consultas de negocio escritas en lenguaje libre.

    Devuelve None si el mensaje no es una consulta de negocio (lo resuelve la FAQ).
    """
    t = simplificar(mensaje)

    # Legajo: 5 digitos (formato de los legajos del sistema).
    m = re.search(r"(?<!\d)(\d{5})(?!\d)", t)
    if m:
        return Intencion("libreta", legajo=m.group(1))

    # Alumnos de un curso: "alumnos de 3°A".
    m = re.search(rf"(?<![\w])([1-6]\s*{_SUFIJO_GRADO}\s*[ab])(?![\w])", t)
    if m and re.search(r"alumn|chic|nen|estudiant|lista", t):
        return Intencion("alumnos", curso=leer_curso(m.group(1)))

    # Conversion de nota: "que escala es un 8 en 2do grado".
    if re.search(r"escala|equival|correspond|convert|sac[oa]|nota|calificacion|significa|\bun \d", t):
        grado = None
        m = re.search(r"(?<![\d.,])([1-6])\s*(?:°|ro|do|er|to|mo|vo)(?![a-z])|(?<![\d.,])([1-6])\s+grado", t)
        if m:
            grado = f"{m.group(1) or m.group(2)}°"
            t_sin_grado = t[:m.start()] + " " + t[m.end():]
        else:
            m = re.search(r"\b(primer|primero|segundo|tercer|tercero|cuarto|quinto|sexto)\s+grado", t)
            if m:
                grado = f"{_ORDINALES[m.group(1)]}°"
                t_sin_grado = t[:m.start()] + " " + t[m.end():]
        if grado:
            notas = [leer_nota(n) for n in re.findall(r"(?<![\d.,])\d{1,2}(?:[.,]\d{1,2})?(?![\d])", t_sin_grado)]
            notas = [n for n in notas if n is not None]
            if notas:
                area = "Lectura" if "lectura" in t else ("Convivencia" if "conviv" in t else None)
                return Intencion("convertir", nota=notas[0], grado=grado, area=area)

    # Listado de cursos: "que cursos hay".
    if re.search(r"\bcursos\b|\bgrados\b|\bsecciones\b", t) and re.search(r"que|cuales|lista|ver|mostr|hay|todos", t):
        return Intencion("cursos")

    # Libreta por nombre: "libreta de quiroga", "notas de sofia perez".
    m = re.search(r"\b(?:libreta|notas|calificaciones|boletin)\s+de(?:l alumno| la alumna)?\s+([a-zñ]+(?:\s+[a-zñ]+)?)", t)
    if m:
        return Intencion("buscar", texto=m.group(1))

    return None


# ----------------------------------------------------------------------
# Conversion de notas
# ----------------------------------------------------------------------
def _nota_texto(nota: float) -> str:
    return str(int(nota)) if nota == int(nota) else f"{nota:.2f}".rstrip("0").replace(".", ",")


def texto_conversion(nota: float, grado: str, area: str | None = None) -> str:
    n = _nota_texto(nota)
    if es_primer_ciclo(grado):
        valor = calificar_area(nota, grado, area or "")
        return (
            f"Un <b>{n}</b> en <b>{grado} grado</b> equivale a <b>{valor}</b>.\n\n"
            "Primer ciclo (1° y 2°), todas las áreas: 10 → LA · 8–9 → L · 6–7 → EP · 1–5 → NL."
        )

    lectura = calificar_area(nota, grado, "Lectura")
    convivencia = calificar_convivencia(nota, grado)
    numerica = calificar_area(nota, grado, "Matemática")
    if area == "Lectura":
        return f"Un <b>{n}</b> en <b>Lectura</b> de <b>{grado} grado</b> equivale a <b>{lectura}</b>."
    if area == "Convivencia":
        return f"Un <b>{n}</b> en <b>Convivencia</b> de <b>{grado} grado</b> equivale a <b>{convivencia}</b>."
    return (
        f"Un <b>{n}</b> en <b>{grado} grado</b> (segundo ciclo) se muestra así:\n"
        f"• Lectura: <b>{lectura}</b>\n"
        f"• Convivencia (comportamiento, esfuerzo, respeto): <b>{convivencia}</b>\n"
        f"• Resto de las áreas: <b>{numerica}</b> (nota numérica)\n\n"
        "Escala S/MB/B/R: 10 → S · 8–9 → MB · 6–7 → B · 1–5 → R."
    )


USO_CONVERTIR = (
    "<b>Convertir una nota a la escala de la libreta</b>\n\n"
    "Uso: <code>/convertir &lt;nota&gt; &lt;grado&gt; [área]</code>\n"
    "Ejemplos:\n"
    "• <code>/convertir 8 2</code>\n"
    "• <code>/convertir 9 4 lectura</code>\n"
    "• <code>/convertir 7,5 5</code>\n\n"
    "También podés escribir: <i>¿qué escala es un 8 en 2° grado?</i>"
)


def convertir_desde_argumentos(args: list[str]) -> str:
    if len(args) < 2:
        return USO_CONVERTIR
    nota = leer_nota(args[0])
    grado = leer_grado(" ".join(args[1:2]))
    if nota is None:
        return f"No entendí la nota <b>{html.escape(args[0])}</b>: tiene que ser un número entre 0 y 10.\n\n{USO_CONVERTIR}"
    if grado is None:
        return f"No entendí el grado <b>{html.escape(args[1])}</b>: tiene que ser de 1 a 6.\n\n{USO_CONVERTIR}"
    resto = simplificar(" ".join(args[2:]))
    area = "Lectura" if "lectura" in resto else ("Convivencia" if "conviv" in resto else None)
    return texto_conversion(nota, grado, area)


# ----------------------------------------------------------------------
# Consultas a la base del sistema
# ----------------------------------------------------------------------
def hay_datos(db: Session) -> bool:
    return db.query(Curso).count() > 0


SIN_DATOS = (
    "La base del sistema no tiene datos cargados.\n"
    "Ejecutá <code>python -m data.seed</code> en la carpeta del proyecto y volvé a intentar."
)


def listar_cursos(db: Session) -> list[tuple[Curso, int]]:
    conteos = dict(db.query(Alumno.curso_id, func.count(Alumno.id)).group_by(Alumno.curso_id).all())
    cursos = db.query(Curso).order_by(Curso.grado, Curso.seccion).all()
    return [(c, conteos.get(c.id, 0)) for c in cursos]


def buscar_curso(db: Session, grado: str, seccion: str) -> Curso | None:
    return db.query(Curso).filter(Curso.grado == grado, Curso.seccion == seccion).first()


def alumnos_de_curso(db: Session, curso_id: int) -> list[Alumno]:
    return (
        db.query(Alumno)
        .filter(Alumno.curso_id == curso_id)
        .order_by(Alumno.apellido, Alumno.nombre)
        .all()
    )


def buscar_alumnos(db: Session, texto: str, limite: int = 15) -> list[Alumno]:
    """Busca por apellido o nombre, sin importar tildes ni mayusculas."""
    palabras = simplificar(texto).split()
    if not palabras:
        return []
    encontrados = []
    for alumno in db.query(Alumno).order_by(Alumno.apellido, Alumno.nombre).all():
        completo = simplificar(f"{alumno.apellido} {alumno.nombre}")
        if all(p in completo for p in palabras):
            encontrados.append(alumno)
            if len(encontrados) >= limite:
                break
    return encontrados


def alumnos_por_legajo(db: Session, legajo: str) -> list[Alumno]:
    return db.query(Alumno).filter(Alumno.legajo == legajo.strip()).all()


def alumno_por_id(db: Session, alumno_id: int) -> Alumno | None:
    return db.get(Alumno, alumno_id)


def etiqueta_alumno(alumno: Alumno) -> str:
    curso = alumno.curso
    return f"{alumno.apellido}, {alumno.nombre} ({curso.grado}{curso.seccion})"


def texto_curso(curso: Curso, alumnos: list[Alumno]) -> str:
    lineas = [
        f"<b>{curso.grado}{curso.seccion}</b> — {'Primer' if es_primer_ciclo(curso.grado) else 'Segundo'} ciclo",
        f"Docente: {html.escape(curso.docente)} · {len(alumnos)} alumnos\n",
    ]
    lineas += [f"<code>{a.legajo}</code> {html.escape(a.apellido)}, {html.escape(a.nombre)}" for a in alumnos]
    lineas.append("\nTocá un alumno para ver su libreta, o usá <code>/libreta &lt;legajo&gt;</code>.")
    return "\n".join(lineas)


# ----------------------------------------------------------------------
# Libreta
# ----------------------------------------------------------------------
def texto_libreta(alumno: Alumno, periodo: str = "Calificación final") -> str:
    curso = alumno.curso
    datos = construir_datos_libreta(alumno, curso, periodo)
    formato = "DUE" if datos["primer_ciclo"] else "Informe"
    completos = datos["trimestres_completos"]

    def valores(celdas) -> str:
        return " · ".join(c["valor"] or "—" for c in celdas)

    lineas = [
        f"📘 <b>Libreta de {html.escape(alumno.apellido)}, {html.escape(alumno.nombre)}</b>",
        f"Legajo <code>{alumno.legajo}</code> · {curso.grado}{curso.seccion} · {datos['ciclo_texto']} ({formato})",
        f"Docente: {html.escape(curso.docente)}",
        f"Período: <b>{periodo}</b>\n",
        "<b>Áreas</b> (1°T · 2°T · 3°T" + (" → final)" if datos["mostrar_final"] else ")"),
    ]
    for area in datos["areas"]:
        linea = f"• {area['area']}: {valores(area['trimestres'])}"
        if datos["mostrar_final"]:
            linea += f" → <b>{area['final']['valor']}</b>"
        lineas.append(linea)

    lineas.append("\n<b>Convivencia y asistencia</b>")
    for item in datos["convivencia"]:
        lineas.append(f"• {item['nombre']}: {valores(item['trimestres'])}")

    if completos < 3:
        lineas.append(f"\n<i>Llenado progresivo: se muestran los {completos} trimestre(s) cursado(s).</i>")
    lineas.append("<i>Datos ficticios de ejemplo del sistema.</i>")
    return "\n".join(lineas)
