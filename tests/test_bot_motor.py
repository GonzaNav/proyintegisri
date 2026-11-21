import re
from html.parser import HTMLParser

import pytest

from bot.conocimiento import ENTRADAS, TEMAS
from bot.motor import normalizar, responder


# ----------------------------------------------------------------------
# Normalizacion
# ----------------------------------------------------------------------
def test_normalizar_quita_tildes_mayusculas_y_signos():
    assert normalizar("¿Por QUÉ migraron?") == "por que migraron"


def test_normalizar_conserva_barra_de_s_c():
    assert normalizar("Qué es S/C") == "que es s/c"


# ----------------------------------------------------------------------
# Coincidencias esperadas
# ----------------------------------------------------------------------
@pytest.mark.parametrize(
    ("pregunta", "esperada"),
    [
        ("¿Por qué migraron?", "porque"),
        ("por que se cambio de laravel a python", "porque"),
        ("qué escalas usa 2do grado", "escalas"),
        ("sqlalchemy vs eloquent", "orm"),
        ("¿Cómo se conecta con Moodle?", "moodle"),
        ("qué base de datos usa", "bd"),
        ("QUÉ FALTA HACER", "pendiente"),
        ("qué quedó afuera de la migración", "descartado"),
        ("qué ya está hecho", "migrado"),
        ("cuántas líneas de código tenía", "numeros"),
        ("cómo se generan los pdf", "pdf"),
        ("qué pasa con los roles y permisos", "roles"),
        ("qué leyes aplican", "legal"),
        ("cómo funciona el login", "seguridad"),
        ("qué problemas tenía el sistema viejo", "deuda"),
        ("cómo se activan las evaluaciones", "evaluaciones"),
        ("jinja o blade", "plantillas"),
        ("hola", "saludo"),
        ("quién sos", "identidad"),
    ],
)
def test_responde_la_entrada_correcta(pregunta, esperada):
    resultado = responder(pregunta)
    assert resultado.entrada is not None
    assert resultado.entrada.id == esperada


def test_tildes_y_mayusculas_no_cambian_el_resultado():
    assert responder("ESCALAS DE CALIFICACIÓN").entrada.id == responder("escalas de calificacion").entrada.id


@pytest.mark.parametrize("texto", ["asdfgh", "", "   ", "ya", "la migración"])
def test_sin_coincidencia_devuelve_sugerencias(texto):
    resultado = responder(texto)
    assert resultado.entrada is None
    assert 1 <= len(resultado.sugerencias) <= 3


def test_palabra_exacta_no_coincide_como_raiz():
    # "der$" (diagrama entidad-relacion) no debe activarse con "derecho".
    resultado = responder("derecho de autor y propiedad intelectual")
    assert resultado.entrada.id == "legal"


def test_sugerencias_relacionadas_excluyen_la_respuesta():
    resultado = responder("por que se cambio de laravel a python")
    assert resultado.entrada.id not in [e.id for e in resultado.sugerencias]


# ----------------------------------------------------------------------
# Integridad de la base de conocimiento
# ----------------------------------------------------------------------
class _ValidadorHTML(HTMLParser):
    PERMITIDAS = {"b", "i", "code", "u", "s", "a", "pre"}

    def __init__(self):
        super().__init__()
        self.pila: list[str] = []
        self.invalidas: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag not in self.PERMITIDAS:
            self.invalidas.append(tag)
        self.pila.append(tag)

    def handle_endtag(self, tag):
        if not self.pila or self.pila.pop() != tag:
            self.invalidas.append(f"/{tag}")


@pytest.mark.parametrize("entrada", ENTRADAS, ids=lambda e: e.id)
def test_respuestas_son_html_valido_para_telegram(entrada):
    validador = _ValidadorHTML()
    validador.feed(entrada.respuesta)
    assert validador.invalidas == []
    assert validador.pila == []
    assert len(entrada.respuesta) < 4096  # limite de un mensaje de Telegram


def test_ids_y_comandos_unicos():
    ids = [e.id for e in ENTRADAS]
    comandos = [e.comando for e in ENTRADAS if e.comando]
    assert len(ids) == len(set(ids))
    assert len(comandos) == len(set(comandos))


@pytest.mark.parametrize("entrada", [e for e in ENTRADAS if e.comando], ids=lambda e: e.comando)
def test_comandos_validos_para_telegram(entrada):
    assert re.fullmatch(r"[a-z0-9_]{1,32}", entrada.comando)
    from bot.handlers import COMANDOS_NEGOCIO

    reservados = {"start", "temas", "ayuda", "help"} | {c for c, _ in COMANDOS_NEGOCIO}
    assert entrada.comando not in reservados


def test_callback_data_dentro_del_limite():
    for entrada in ENTRADAS:
        assert len(f"faq:{entrada.id}".encode()) <= 64
    for slug in TEMAS:
        assert len(f"tema:{slug}".encode()) <= 64


def test_cada_tema_tiene_entradas_y_cada_entrada_un_tema_conocido():
    temas_usados = {e.tema for e in ENTRADAS}
    assert set(TEMAS) <= temas_usados
    assert temas_usados <= set(TEMAS) | {"general"}


def test_menu_de_comandos_se_construye():
    from bot.handlers import comandos_del_menu

    comandos = comandos_del_menu()
    assert all(1 <= len(c.description) <= 256 for c in comandos)
