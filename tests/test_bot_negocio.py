from html.parser import HTMLParser

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Alumno, Curso
from bot import negocio


# ----------------------------------------------------------------------
# Base en memoria con datos de prueba
# ----------------------------------------------------------------------
@pytest.fixture
def db():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    sesion = sessionmaker(bind=engine)()
    c1 = Curso(grado="1°", seccion="A", cantidad_alumnos=2, docente="María García")
    c4 = Curso(grado="4°", seccion="B", cantidad_alumnos=1, docente="Mario Suárez")
    sesion.add_all([c1, c4])
    sesion.flush()
    sesion.add_all([
        Alumno(nombre="Sofía", apellido="Quiroga", legajo="01967", curso_id=c1.id),
        Alumno(nombre="Bruno", apellido="Méndez", legajo="01583", curso_id=c1.id),
        Alumno(nombre="Sofía", apellido="Quiroga", legajo="08111", curso_id=c4.id),
    ])
    sesion.commit()
    yield sesion
    sesion.close()


class _ValidadorHTML(HTMLParser):
    PERMITIDAS = {"b", "i", "code", "u", "s", "a", "pre"}

    def __init__(self):
        super().__init__()
        self.pila, self.invalidas = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in self.PERMITIDAS:
            self.invalidas.append(tag)
        self.pila.append(tag)

    def handle_endtag(self, tag):
        if not self.pila or self.pila.pop() != tag:
            self.invalidas.append(f"/{tag}")


def assert_html_valido(texto: str) -> None:
    v = _ValidadorHTML()
    v.feed(texto)
    assert v.invalidas == [] and v.pila == []
    assert len(texto) < 4096


# ----------------------------------------------------------------------
# Lectura de datos escritos por el usuario
# ----------------------------------------------------------------------
@pytest.mark.parametrize(("texto", "esperado"), [
    ("2", "2°"), ("2°", "2°"), ("2do", "2°"), ("4to grado", "4°"), ("segundo", "2°"), ("Sexto grado", "6°"),
    ("7", None), ("0", None), ("abc", None),
])
def test_leer_grado(texto, esperado):
    assert negocio.leer_grado(texto) == esperado


@pytest.mark.parametrize(("texto", "esperado"), [
    ("8", 8.0), ("8,5", 8.5), ("8.5", 8.5), ("10", 10.0), ("0", 0.0), ("11", None), ("-1", None), ("ocho", None),
])
def test_leer_nota(texto, esperado):
    assert negocio.leer_nota(texto) == esperado


@pytest.mark.parametrize(("texto", "esperado"), [
    ("3A", ("3°", "A")), ("3°a", ("3°", "A")), ("3 b", ("3°", "B")), ("7A", None), ("3C", None),
])
def test_leer_curso(texto, esperado):
    assert negocio.leer_curso(texto) == esperado


# ----------------------------------------------------------------------
# Conversion de notas (misma regla que app/utils/escala.py)
# ----------------------------------------------------------------------
@pytest.mark.parametrize(("nota", "grado", "esperado"), [
    (10, "1°", "LA"), (8, "2°", "L"), (9, "2°", "L"), (6, "1°", "EP"), (4, "2°", "NL"),
])
def test_conversion_primer_ciclo(nota, grado, esperado):
    assert f"equivale a <b>{esperado}</b>" in negocio.texto_conversion(nota, grado)


def test_conversion_segundo_ciclo_muestra_las_tres_formas():
    texto = negocio.texto_conversion(8.5, "5°")
    assert "Lectura: <b>MB</b>" in texto
    assert "Convivencia (comportamiento, esfuerzo, respeto): <b>MB</b>" in texto
    assert "Resto de las áreas: <b>8,50</b>" in texto


def test_conversion_segundo_ciclo_por_area():
    assert "equivale a <b>S</b>" in negocio.texto_conversion(10, "4°", "Lectura")
    assert "equivale a <b>B</b>" in negocio.texto_conversion(6, "6°", "Convivencia")


def test_convertir_desde_argumentos():
    assert "equivale a <b>L</b>" in negocio.convertir_desde_argumentos(["8", "2"])
    assert "equivale a <b>MB</b>" in negocio.convertir_desde_argumentos(["9", "4", "lectura"])
    assert "No entendí la nota" in negocio.convertir_desde_argumentos(["11", "2"])
    assert "No entendí el grado" in negocio.convertir_desde_argumentos(["8", "9"])
    assert negocio.convertir_desde_argumentos([]) == negocio.USO_CONVERTIR


# ----------------------------------------------------------------------
# Interpretacion de texto libre
# ----------------------------------------------------------------------
@pytest.mark.parametrize(("mensaje", "tipo", "campos"), [
    ("¿qué escala es un 8 en 2° grado?", "convertir", {"nota": 8.0, "grado": "2°"}),
    ("un 8 en 2do", "convertir", {"nota": 8.0, "grado": "2°"}),
    ("cuánto equivale un 9,5 en 4to grado en lectura", "convertir", {"nota": 9.5, "grado": "4°", "area": "Lectura"}),
    ("que nota es un 6 en segundo grado", "convertir", {"nota": 6.0, "grado": "2°"}),
    ("alumnos de 3°A", "alumnos", {"curso": ("3°", "A")}),
    ("01967", "libreta", {"legajo": "01967"}),
    ("libreta de quiroga", "buscar", {"texto": "quiroga"}),
    ("qué cursos hay", "cursos", {}),
])
def test_interpretar_consultas_de_negocio(mensaje, tipo, campos):
    intencion = negocio.interpretar(mensaje)
    assert intencion is not None and intencion.tipo == tipo
    for campo, valor in campos.items():
        assert getattr(intencion, campo) == valor


@pytest.mark.parametrize("mensaje", [
    "¿por qué migraron?", "qué escalas hay", "cómo se generan las libretas", "sqlalchemy vs eloquent", "hola",
])
def test_preguntas_de_migracion_no_se_interpretan_como_negocio(mensaje):
    assert negocio.interpretar(mensaje) is None


# ----------------------------------------------------------------------
# Consultas a la base
# ----------------------------------------------------------------------
def test_listar_cursos_cuenta_alumnos(db):
    resultado = [(f"{c.grado}{c.seccion}", n) for c, n in negocio.listar_cursos(db)]
    assert resultado == [("1°A", 2), ("4°B", 1)]


def test_alumnos_de_curso_ordenados_por_apellido(db):
    curso = negocio.buscar_curso(db, "1°", "A")
    assert [a.apellido for a in negocio.alumnos_de_curso(db, curso.id)] == ["Méndez", "Quiroga"]


def test_buscar_alumnos_sin_tildes_ni_mayusculas(db):
    assert [a.legajo for a in negocio.buscar_alumnos(db, "MENDEZ")] == ["01583"]
    assert len(negocio.buscar_alumnos(db, "sofia quiroga")) == 2
    assert negocio.buscar_alumnos(db, "inexistente") == []


def test_alumnos_por_legajo(db):
    assert [a.nombre for a in negocio.alumnos_por_legajo(db, "01967")] == ["Sofía"]
    assert negocio.alumnos_por_legajo(db, "99999") == []


def test_hay_datos():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    vacia = sessionmaker(bind=engine)()
    assert negocio.hay_datos(vacia) is False


# ----------------------------------------------------------------------
# Libreta (misma construccion que la vista web)
# ----------------------------------------------------------------------
def test_libreta_primer_ciclo_final(db):
    alumno = negocio.alumnos_por_legajo(db, "01967")[0]
    texto = negocio.texto_libreta(alumno)
    assert "Primer Ciclo (DUE)" in texto
    assert "• Lengua:" in texto and "→ <b>" in texto
    assert "Inasistencias" in texto
    assert_html_valido(texto)


def test_libreta_segundo_ciclo_llenado_progresivo(db):
    alumno = negocio.alumnos_por_legajo(db, "08111")[0]
    texto = negocio.texto_libreta(alumno, "Primer trimestre")
    assert "Segundo Ciclo (Informe)" in texto
    assert "• Lectura:" in texto
    assert "→ <b>" not in texto  # sin columna final fuera de "Calificación final"
    assert "se muestran los 1 trimestre(s)" in texto
    assert_html_valido(texto)


def test_integracion_grupal_usa_escala_de_convivencia(db):
    alumno = negocio.alumnos_por_legajo(db, "08111")[0]
    linea = next(l for l in negocio.texto_libreta(alumno).splitlines() if l.startswith("• Integración grupal"))
    valores = linea.split(": ")[1].split(" · ")
    assert all(v in {"S", "MB", "B", "R"} for v in valores)


def test_textos_de_negocio_son_html_valido(db):
    curso = negocio.buscar_curso(db, "1°", "A")
    assert_html_valido(negocio.texto_curso(curso, negocio.alumnos_de_curso(db, curso.id)))
    assert_html_valido(negocio.USO_CONVERTIR)
    assert_html_valido(negocio.texto_conversion(7, "3°"))
    assert_html_valido(negocio.convertir_desde_argumentos(["<b>", "2"]))
