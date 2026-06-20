"""Mapeo de notas numericas a la escala cualitativa de San Juan."""


def es_primer_ciclo(grado: str) -> bool:
    return grado in ("1°", "2°")


def a_cualitativa(nota: float, grado: str) -> str:
    if nota is None:
        return "S/C"

    if es_primer_ciclo(grado):
        if nota >= 10:
            return "LA"
        if nota >= 8:
            return "L"
        if nota >= 6:
            return "EP"
        return "NL"

    if nota >= 10:
        return "S"
    if nota >= 8:
        return "MB"
    if nota >= 6:
        return "B"
    return "R"


def color_cualitativa(valor: str) -> str:
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
    }.get(valor, "bg-slate-100 text-slate-500")
