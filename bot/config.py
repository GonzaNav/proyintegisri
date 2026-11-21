"""Configuracion del bot: lee el token desde el archivo .env de la raiz del repo."""

import os
from pathlib import Path

from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent
ARCHIVO_ENV = RAIZ / ".env"

load_dotenv(ARCHIVO_ENV)


def obtener_token() -> str:
    token = os.getenv("BOT_KEY", "").strip().strip('"').strip("'")
    if not token:
        raise SystemExit(
            "No encontre el token del bot.\n"
            f"Crea el archivo {ARCHIVO_ENV} con la linea:\n"
            "    BOT_KEY=<token que te dio @BotFather>\n"
            "(podes copiar .env.example como punto de partida)."
        )
    return token
