"""Handlers de Telegram: traducen comandos, botones y mensajes al motor de respuestas."""

import html
import logging

from telegram.error import BadRequest
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

from app.database import SessionLocal
from bot import negocio
from bot.conocimiento import ENTRADAS, TEMAS, Entrada, por_id, por_tema
from bot.motor import responder

log = logging.getLogger(__name__)

BIENVENIDA = (
    "👋 <b>Hola, soy el asistente de Libretas.py.</b>\n\n"
    "<b>Consultas del sistema</b> (datos ficticios de ejemplo):\n"
    "• /cursos — cursos, alumnos y sus libretas\n"
    "• /convertir 8 2 — pasar una nota a la escala de la libreta\n"
    "• /buscar quiroga — buscar un alumno\n"
    "• /libreta 01967 — libreta de un alumno por legajo\n\n"
    "<b>Consultas sobre la migración</b> de Laravel/PHP a Python/FastAPI: escribí tu pregunta, por ejemplo "
    "<i>¿por qué se migró?</i> o <i>¿cómo se conecta con Moodle?</i>\n\n"
    "O elegí una opción:"
)

# Comandos de negocio (se publican en el menu de Telegram antes que los de la FAQ).
COMANDOS_NEGOCIO = [
    ("cursos", "Cursos, alumnos y libretas"),
    ("convertir", "Convertir una nota a la escala"),
    ("buscar", "Buscar un alumno"),
    ("libreta", "Libreta de un alumno por legajo"),
    ("alumnos", "Alumnos de un curso (ej: /alumnos 3A)"),
]

PERIODO_BOTON = {"1": "1°T", "2": "2°T", "3": "3°T", "f": "Final"}


# ----------------------------------------------------------------------
# Teclados
# ----------------------------------------------------------------------
def teclado_temas() -> InlineKeyboardMarkup:
    botones = [InlineKeyboardButton(nombre, callback_data=f"tema:{slug}") for slug, nombre in TEMAS.items()]
    filas = [
        [InlineKeyboardButton("📚 Cursos y libretas", callback_data="cursos"),
         InlineKeyboardButton("🔢 Convertir nota", callback_data="convertir")],
    ]
    filas += [botones[i:i + 2] for i in range(0, len(botones), 2)]
    return InlineKeyboardMarkup(filas)


def teclado_cursos(cursos) -> InlineKeyboardMarkup:
    botones = [
        InlineKeyboardButton(f"{c.grado}{c.seccion} ({n})", callback_data=f"curso:{c.id}") for c, n in cursos
    ]
    return InlineKeyboardMarkup([botones[i:i + 3] for i in range(0, len(botones), 3)])


def teclado_alumnos(alumnos, volver_a_cursos: bool = False) -> InlineKeyboardMarkup:
    botones = [
        InlineKeyboardButton(f"{a.apellido}, {a.nombre}", callback_data=f"lib:{a.id}:f") for a in alumnos
    ]
    filas = [botones[i:i + 2] for i in range(0, len(botones), 2)]
    if volver_a_cursos:
        filas.append([InlineKeyboardButton("« Volver a cursos", callback_data="cursos")])
    return InlineKeyboardMarkup(filas)


def teclado_periodos(alumno_id: int, actual: str) -> InlineKeyboardMarkup:
    fila = [
        InlineKeyboardButton(("• " if codigo == actual else "") + texto, callback_data=f"lib:{alumno_id}:{codigo}")
        for codigo, texto in PERIODO_BOTON.items()
    ]
    return InlineKeyboardMarkup([fila])


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
    lineas = ["<b>Consultas del sistema</b>"]
    lineas += [f"/{c} — {d}" for c, d in COMANDOS_NEGOCIO]
    lineas += ["\n<b>Consultas sobre la migración</b>", "/temas — menú de temas", "/ayuda — esta ayuda"]
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
# Logica de negocio: cursos, alumnos, libretas y escalas
# ----------------------------------------------------------------------
async def enviar_html(mensaje: Message, texto: str, teclado: InlineKeyboardMarkup | None = None) -> None:
    await mensaje.reply_text(texto, parse_mode=ParseMode.HTML, reply_markup=teclado)


def codigo_periodo(texto: str | None) -> str:
    t = negocio.simplificar(texto or "").strip()
    if t in ("1", "1t", "primero", "primer"):
        return "1"
    if t in ("2", "2t", "segundo"):
        return "2"
    if t in ("3", "3t", "tercero", "tercer"):
        return "3"
    return "f"


async def mostrar_cursos(mensaje: Message) -> None:
    with SessionLocal() as db:
        if not negocio.hay_datos(db):
            await enviar_html(mensaje, negocio.SIN_DATOS)
            return
        cursos = negocio.listar_cursos(db)
    await enviar_html(mensaje, "<b>Cursos</b> (entre paréntesis, cantidad de alumnos). Elegí uno:", teclado_cursos(cursos))


async def mostrar_curso(mensaje: Message, grado: str, seccion: str) -> None:
    with SessionLocal() as db:
        curso = negocio.buscar_curso(db, grado, seccion)
        if curso is None:
            await enviar_html(mensaje, f"No existe el curso {grado}{seccion}. Mirá la lista con /cursos.")
            return
        alumnos = negocio.alumnos_de_curso(db, curso.id)
        await enviar_html(mensaje, negocio.texto_curso(curso, alumnos), teclado_alumnos(alumnos))


async def mostrar_libreta(mensaje: Message, alumnos: list, periodo: str = "f", sin_resultados: str = "") -> bool:
    """Muestra la libreta si hay un solo alumno; si hay varios, ofrece elegir. Devuelve False si no hay ninguno."""
    if not alumnos:
        if sin_resultados:
            await enviar_html(mensaje, sin_resultados)
        return False
    if len(alumnos) == 1:
        alumno = alumnos[0]
        await enviar_html(
            mensaje,
            negocio.texto_libreta(alumno, negocio.PERIODOS_CORTOS[periodo]),
            teclado_periodos(alumno.id, periodo),
        )
        return True
    botones = [[InlineKeyboardButton(negocio.etiqueta_alumno(a), callback_data=f"lib:{a.id}:{periodo}")] for a in alumnos]
    await enviar_html(mensaje, "Encontré varios alumnos. Elegí uno:", InlineKeyboardMarkup(botones))
    return True


async def cmd_cursos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await mostrar_cursos(update.effective_message)


async def cmd_alumnos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    curso = negocio.leer_curso(" ".join(context.args))
    if curso is None:
        await enviar_html(update.effective_message, "Uso: <code>/alumnos 3A</code> (grado de 1 a 6 y sección A o B).")
        return
    await mostrar_curso(update.effective_message, *curso)


async def cmd_convertir(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await enviar_html(update.effective_message, negocio.convertir_desde_argumentos(context.args))


async def cmd_buscar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    texto = " ".join(context.args)
    if not texto:
        await enviar_html(update.effective_message, "Uso: <code>/buscar &lt;apellido o nombre&gt;</code>, por ejemplo <code>/buscar quiroga</code>.")
        return
    with SessionLocal() as db:
        if not negocio.hay_datos(db):
            await enviar_html(update.effective_message, negocio.SIN_DATOS)
            return
        await mostrar_libreta(
            update.effective_message,
            negocio.buscar_alumnos(db, texto),
            sin_resultados=f"No encontré alumnos con \"{html.escape(texto)}\".",
        )


async def cmd_libreta(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await enviar_html(
            update.effective_message,
            "Uso: <code>/libreta &lt;legajo&gt; [1|2|3|final]</code>, por ejemplo <code>/libreta 01967</code>.\n"
            "Los legajos aparecen en /cursos o con /buscar.",
        )
        return
    legajo = context.args[0]
    periodo = codigo_periodo(context.args[1] if len(context.args) > 1 else None)
    with SessionLocal() as db:
        if not negocio.hay_datos(db):
            await enviar_html(update.effective_message, negocio.SIN_DATOS)
            return
        await mostrar_libreta(
            update.effective_message,
            negocio.alumnos_por_legajo(db, legajo),
            periodo,
            sin_resultados=f"No encontré el legajo <code>{html.escape(legajo)}</code>.",
        )


async def atender_intencion(mensaje: Message, intencion: negocio.Intencion) -> bool:
    """Resuelve una consulta de negocio escrita en texto libre. Devuelve False si no pudo."""
    if intencion.tipo == "convertir":
        await enviar_html(mensaje, negocio.texto_conversion(intencion.nota, intencion.grado, intencion.area))
        return True
    if intencion.tipo == "cursos":
        await mostrar_cursos(mensaje)
        return True
    if intencion.tipo == "alumnos" and intencion.curso:
        await mostrar_curso(mensaje, *intencion.curso)
        return True
    with SessionLocal() as db:
        if not negocio.hay_datos(db):
            return False
        if intencion.tipo == "libreta":
            return await mostrar_libreta(
                mensaje,
                negocio.alumnos_por_legajo(db, intencion.legajo),
                sin_resultados=f"No encontré el legajo <code>{intencion.legajo}</code>.",
            )
        if intencion.tipo == "buscar":
            return await mostrar_libreta(mensaje, negocio.buscar_alumnos(db, intencion.texto))
    return False


# ----------------------------------------------------------------------
# Mensajes libres y botones
# ----------------------------------------------------------------------
async def texto_libre(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    mensaje = update.effective_message

    intencion = negocio.interpretar(mensaje.text or "")
    if intencion and await atender_intencion(mensaje, intencion):
        log.info("Consulta %r -> negocio:%s", mensaje.text, intencion.tipo)
        return

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
    elif datos == "convertir":
        await enviar_html(consulta.message, negocio.USO_CONVERTIR)
    elif datos == "cursos":
        with SessionLocal() as db:
            if not negocio.hay_datos(db):
                await enviar_html(consulta.message, negocio.SIN_DATOS)
                return
            cursos = negocio.listar_cursos(db)
        await editar_o_enviar(consulta, "<b>Cursos</b> (entre paréntesis, cantidad de alumnos). Elegí uno:", teclado_cursos(cursos))
    elif datos.startswith("curso:"):
        with SessionLocal() as db:
            curso = db.get(negocio.Curso, int(datos.removeprefix("curso:")))
            if curso:
                alumnos = negocio.alumnos_de_curso(db, curso.id)
                await editar_o_enviar(consulta, negocio.texto_curso(curso, alumnos), teclado_alumnos(alumnos, volver_a_cursos=True))
    elif datos.startswith("lib:"):
        _, alumno_id, periodo = datos.split(":")
        with SessionLocal() as db:
            alumno = negocio.alumno_por_id(db, int(alumno_id))
            if alumno is None:
                return
            texto = negocio.texto_libreta(alumno, negocio.PERIODOS_CORTOS.get(periodo, "Calificación final"))
            teclado = teclado_periodos(alumno.id, periodo)
        if (consulta.message.text or "").startswith("📘"):
            # Cambio de periodo sobre la misma libreta: se actualiza el mensaje.
            await editar_o_enviar(consulta, texto, teclado)
        else:
            await enviar_html(consulta.message, texto, teclado)


async def editar_o_enviar(consulta, texto: str, teclado: InlineKeyboardMarkup | None) -> None:
    try:
        await consulta.edit_message_text(texto, parse_mode=ParseMode.HTML, reply_markup=teclado)
    except BadRequest as error:
        # Telegram rechaza la edicion si el contenido no cambio (por ejemplo, el mismo periodo).
        if "not modified" not in str(error).lower():
            raise


async def manejar_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.exception("Error procesando una actualizacion", exc_info=context.error)


# ----------------------------------------------------------------------
# Registro
# ----------------------------------------------------------------------
def comandos_del_menu() -> list[BotCommand]:
    comandos = [BotCommand(c, d) for c, d in COMANDOS_NEGOCIO]
    comandos += [BotCommand("temas", "Menú de temas"), BotCommand("ayuda", "Lista de comandos")]
    comandos += [BotCommand(e.comando, e.titulo.strip("¿?")) for e in ENTRADAS if e.comando]
    return comandos


async def publicar_comandos(app: Application) -> None:
    """Carga el menu de comandos en Telegram (evita configurarlo a mano en @BotFather)."""
    await app.bot.set_my_commands(comandos_del_menu())


def registrar(app: Application) -> None:
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("temas", cmd_temas))
    app.add_handler(CommandHandler(["ayuda", "help"], cmd_ayuda))
    app.add_handler(CommandHandler("cursos", cmd_cursos))
    app.add_handler(CommandHandler("alumnos", cmd_alumnos))
    app.add_handler(CommandHandler("convertir", cmd_convertir))
    app.add_handler(CommandHandler("buscar", cmd_buscar))
    app.add_handler(CommandHandler("libreta", cmd_libreta))
    for entrada in ENTRADAS:
        if entrada.comando:
            app.add_handler(CommandHandler(entrada.comando, crear_cmd_entrada(entrada)))
    app.add_handler(CallbackQueryHandler(boton))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, texto_libre))
    app.add_handler(MessageHandler(filters.COMMAND, cmd_desconocido))
    app.add_error_handler(manejar_error)
