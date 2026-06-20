"""Mapeo de notas numericas a las escalas cualitativas usadas en San Juan.

Reglas tomadas del sistema antiguo (Laravel) en helpers.php.
"""


def es_primer_ciclo(grado: str) -> bool:
    return grado in ("1°", "2°")


def cualitativa_primer_ciclo(nota: float | None) -> str:
    """LA / L / EP / NL para 1° y 2° grado y para items de integracion."""
    if nota is None:
        return "S/C"
    if nota >= 10:
        return "LA"
    if nota >= 8:
        return "L"
    if nota >= 6:
        return "EP"
    if nota >= 1:
        return "NL"
    return "S/C"


def cualitativa_segundo_ciclo(nota: float | None) -> str:
    """S / MB / B / R para Lectura, Convivencia, Esfuerzo, Respeto en 3°-6°."""
    if nota is None:
        return "S/C"
    if nota >= 10:
        return "S"
    if nota >= 8:
        return "MB"
    if nota >= 6:
        return "B"
    if nota >= 1:
        return "R"
    return "S/C"


def formato_numerica(nota: float | None) -> str:
    if nota is None:
        return "S/C"
    if nota == int(nota):
        return str(int(nota))
    return f"{nota:.2f}".replace(".", ",")


def calificar_area(nota: float | None, grado: str, materia: str) -> str:
    """Devuelve la calificacion mostrada para un espacio curricular."""
    if es_primer_ciclo(grado):
        return cualitativa_primer_ciclo(nota)
    if materia == "Lectura":
        return cualitativa_segundo_ciclo(nota)
    return formato_numerica(nota)


def calificar_convivencia(nota: float | None, grado: str) -> str:
    """Para items de Convivencia (C, E, R)."""
    if es_primer_ciclo(grado):
        return cualitativa_primer_ciclo(nota)
    return cualitativa_segundo_ciclo(nota)


def calificar_inasistencia(nota: float | None) -> str:
    """Para items de inasistencias / tardanzas: si es 0 muestra '-', sino el numero."""
    if nota is None or nota == 0:
        return "-"
    if nota == int(nota):
        return str(int(nota))
    return f"{nota:.1f}".replace(".", ",")


def color(valor: str) -> str:
    return {
        "LA": "bg-emerald-100 text-emerald-800",
        "L":  "bg-blue-100 text-blue-800",
        "EP": "bg-amber-100 text-amber-800",
        "NL": "bg-rose-100 text-rose-800",
        "S":  "bg-emerald-100 text-emerald-800",
        "MB": "bg-blue-100 text-blue-800",
        "B":  "bg-amber-100 text-amber-800",
        "R":  "bg-rose-100 text-rose-800",
        "S/C": "bg-slate-100 text-slate-500",
        "-":  "bg-slate-50 text-slate-400",
    }.get(valor, "bg-slate-100 text-slate-700")
