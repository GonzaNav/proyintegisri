from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

DATABASE_URL = f"sqlite:///{BASE_DIR.parent / 'libretas.db'}"

SECRET_KEY = "cambiar-en-produccion-9f3a8b2c4d5e6f7a1b0c9d8e7f6a5b4c"

AUTOR = {
    "nombre": "Gonzalo Naveda",
    "carrera": "Tecnicatura Superior en Desarrollo de Software",
    "institucion": "Instituto Superior en Redes e Informatica (ISRI)",
    "materia": "Practica Profesionalizante II",
    "docente": "Prof. Emir Zatta",
    "anio": 2026,
    "github": "https://github.com/GonzaNav",
}

INSTITUCION = {
    "nombre": "Escuela Primaria San Jose",
    "cue": "6603457",
    "provincia": "San Juan",
    "localidad": "San Juan",
}
