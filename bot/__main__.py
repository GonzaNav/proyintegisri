"""Punto de entrada: python -m bot"""

import logging

from telegram import Update
from telegram.ext import Application

from bot.config import obtener_token
from bot.handlers import publicar_comandos, registrar


def main() -> None:
    logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.INFO)
    # httpx registra cada URL a nivel INFO, y la URL de la API de Telegram incluye el token.
    logging.getLogger("httpx").setLevel(logging.WARNING)

    app = Application.builder().token(obtener_token()).post_init(publicar_comandos).build()
    registrar(app)

    logging.getLogger(__name__).info("Bot iniciado. Ctrl+C para detenerlo.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
