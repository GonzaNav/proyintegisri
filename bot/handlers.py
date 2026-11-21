"""Handlers de Telegram: traducen comandos, botones y mensajes al motor de respuestas."""

import logging

from telegram import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, Message, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from bot.conocimiento import ENTRADAS, TEMAS, Entrada, por_id, por_tema
from bot.motor import responder

log = logging.getLogger(__name__)

BIENVENIDA = (
    "👋 <b>Hola, soy el asistente de Libretas.py.</b>\n\n"
    "Respondo consultas sobre la <b>migración</b> del sistema de libretas de primaria "
    "de <b>Laravel/PHP</b> a <b>Python/FastAPI</b>.\n\n"
    "Podés escribirme una pregunta, por ejemplo:\n"
    "• <i>¿Por qué se migró?</i>\n"
    "• <i>¿Qué escalas usa 2° grado?</i>\n"
    "• <i>¿Cómo se conecta con Moodle?</i>\n\n"
    "O elegir un tema:"
)


# ----------------------------------------------------------------------
# Teclados
# ----------------------------------------------------------------------
def teclado_temas() -> InlineKeyboardMarkup:
    botones = [InlineKeyboardButton(nombre, callback_data=f"tema:{slug}") for slug, nombre in TEMAS.items()]
    filas = [botones[i:i + 2] for i in range(0, len(botones), 2)]
    return InlineKeyboardMarkup(filas)


def teclado_entradas(entradas: list[Entrada], volver: bool = False) -> InlineKeyboardMarkup | None:
    filas = [[InlineKeyboardButton(e.titulo, callback_data=f"faq:{e.id}")] for e in entradas]
    if volver:
        filas.append([InlineKeyboardButton("« Volver a temas", callback_data="temas")])
    return InlineKeyboardMarkup(filas) if filas else None


async def enviar_entrada(mensaje: Message, entrada: Entrada, relacionadas: list[Entrada] | None = None) -> None:
    texto = entrada.respuesta
    if relacionadas:
        texto += "\n\n<i>También te puede interesar:</i>"
    await mensaje.reply_text(
        texto,
        parse_mode=ParseMode.HTML,
        reply_markup=teclado_entradas(relacionadas or []),
    )


# ----------------------------------------------------------------------
# Comandos
# ----------------------------------------------------------------------
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(BIENVENIDA, parse_mode=ParseMode.HTML, reply_markup=teclado_temas())


async def cmd_temas(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text("Elegí un tema:", reply_markup=teclado_temas())


async def cmd_ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lineas = ["<b>Comandos disponibles</b>\n", "/temas — menú de temas", "/ayuda — esta ayuda"]
    lineas += [f"/{e.comando} — {e.titulo}" for e in ENTRADAS if e.comando]
    lineas.append("\nTambién podés escribir tu pregunta con tus palabras.")
    await update.effective_message.reply_text("\n".join(lineas), parse_mode=ParseMode.HTML)


def crear_cmd_entrada(entrada: Entrada):
    async def _cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await enviar_entrada(update.effective_message, entrada)

    return _cmd


async def cmd_desconocido(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text("No conozco ese comando. Probá con /ayuda o /temas.")


# ----------------------------------------------------------------------
# Mensajes libres y botones
# ----------------------------------------------------------------------
async def texto_libre(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    mensaje = update.effective_message
    resultado = responder(mensaje.text or "")
    log.info("Consulta %r -> %s (%d)", mensaje.text, resultado.entrada.id if resultado.entrada else "-", resultado.puntaje)

    if resultado.entrada:
        await enviar_entrada(mensaje, resultado.entrada, resultado.sugerencias)
        return

    await mensaje.reply_text(
        "🤔 No encontré una respuesta para eso. Quizás te sirva alguno de estos temas, "
        "o mirá el menú completo con /temas:",
        reply_markup=teclado_entradas(resultado.sugerencias),
    )


async def boton(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    consulta = update.callback_query
    await consulta.answer()
    datos = consulta.data or ""

    if datos == "temas":
        await consulta.edit_message_text("Elegí un tema:", reply_markup=teclado_temas())
    elif datos.startswith("tema:"):
        slug = datos.removeprefix("tema:")
        await consulta.edit_message_text(
            f"<b>{TEMAS.get(slug, 'Tema')}</b> — elegí una consulta:",
            parse_mode=ParseMode.HTML,
            reply_markup=teclado_entradas(por_tema(slug), volver=True),
        )
    elif datos.startswith("faq:"):
        entrada = por_id(datos.removeprefix("faq:"))
        if entrada:
            await enviar_entrada(consulta.message, entrada)


async def manejar_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.exception("Error procesando una actualizacion", exc_info=context.error)


# ----------------------------------------------------------------------
# Registro
# ----------------------------------------------------------------------
def comandos_del_menu() -> list[BotCommand]:
    comandos = [BotCommand("temas", "Menú de temas"), BotCommand("ayuda", "Lista de comandos")]
    comandos += [BotCommand(e.comando, e.titulo.strip("¿?")) for e in ENTRADAS if e.comando]
    return comandos


async def publicar_comandos(app: Application) -> None:
    """Carga el menu de comandos en Telegram (evita configurarlo a mano en @BotFather)."""
    await app.bot.set_my_commands(comandos_del_menu())


def registrar(app: Application) -> None:
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("temas", cmd_temas))
    app.add_handler(CommandHandler(["ayuda", "help"], cmd_ayuda))
    for entrada in ENTRADAS:
        if entrada.comando:
            app.add_handler(CommandHandler(entrada.comando, crear_cmd_entrada(entrada)))
    app.add_handler(CallbackQueryHandler(boton))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, texto_libre))
    app.add_handler(MessageHandler(filters.COMMAND, cmd_desconocido))
    app.add_error_handler(manejar_error)
