"""Motor de respuestas por palabras clave.

No depende de Telegram: recibe texto y devuelve la entrada de la base de
conocimiento que mejor coincide, junto con sugerencias relacionadas.
"""

import re
import unicodedata
from dataclasses import dataclass, field

from bot.conocimiento import ENTRADAS, Entrada, por_id

# Puntaje minimo para considerar que una entrada responde la consulta.
PUNTAJE_MINIMO = 2

# Entradas que se sugieren cuando no hay ninguna coincidencia.
SUGERENCIAS_POR_DEFECTO = ("porque", "stack", "migrado")


@dataclass
class Resultado:
    entrada: Entrada | None
    puntaje: int = 0
    sugerencias: list[Entrada] = field(default_factory=list)


def normalizar(texto: str) -> str:
    """Pasa a minusculas, quita tildes y signos; conserva letras, numeros y '/'."""
    texto = unicodedata.normalize("NFD", texto.lower())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    texto = re.sub(r"[^a-z0-9/]+", " ", texto)
    return " ".join(texto.split())


def _coincide(clave: str, texto: str) -> bool:
    """Una clave coincide si aparece al inicio de una palabra del texto.

    - "migr" coincide con "migracion", "migraron", etc. (raiz).
    - "base de datos" se busca como frase.
    - Una clave terminada en "$" exige la palabra exacta ("ya$" no coincide con "yaguar").
    """
    exacta = clave.endswith("$")
    clave = normalizar(clave.rstrip("$"))
    if not clave:
        return False
    fin = r"\b" if exacta else ""
    return re.search(rf"(?<![a-z0-9]){re.escape(clave)}{fin}", texto) is not None


def puntuar(texto_normalizado: str, entrada: Entrada) -> int:
    return sum(peso for clave, peso in entrada.palabras_clave.items() if _coincide(clave, texto_normalizado))


def responder(mensaje: str) -> Resultado:
    texto = normalizar(mensaje)
    if not texto:
        return Resultado(entrada=None, sugerencias=_por_defecto())

    puntajes = [(puntuar(texto, e), i, e) for i, e in enumerate(ENTRADAS)]
    # Mayor puntaje primero; ante empate, el orden de la base de conocimiento.
    puntajes.sort(key=lambda t: (-t[0], t[1]))
    mejor_puntaje, _, mejor = puntajes[0]

    if mejor_puntaje < PUNTAJE_MINIMO:
        cercanas = [e for p, _, e in puntajes if p > 0 and e.tema != "general"][:3]
        return Resultado(entrada=None, puntaje=mejor_puntaje, sugerencias=cercanas or _por_defecto())

    relacionadas = [
        e for p, _, e in puntajes[1:]
        if p >= PUNTAJE_MINIMO and e.tema != "general"
    ][:2]
    if mejor.tema == "general":
        relacionadas = []
    return Resultado(entrada=mejor, puntaje=mejor_puntaje, sugerencias=relacionadas)


def _por_defecto() -> list[Entrada]:
    return [e for e in (por_id(i) for i in SUGERENCIAS_POR_DEFECTO) if e is not None]
