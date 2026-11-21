"""Base de conocimiento del bot: preguntas frecuentes sobre la migracion.

Cada entrada tiene:
- id: identificador unico (se usa en los botones de Telegram).
- tema: agrupador para el menu /temas.
- titulo: texto corto que se muestra en botones y sugerencias.
- comando: comando de Telegram que devuelve la entrada directamente (opcional).
- palabras_clave: raices normalizadas (sin tildes, en minuscula) con su peso.
  Una raiz coincide con cualquier palabra que empiece igual ("migr" -> "migracion").
  Las frases con espacios se buscan textuales dentro del mensaje normalizado.
- respuesta: texto en HTML de Telegram (<b>, <i>, <code>).

Fuentes: inventario del sistema Laravel, Plan de Trabajo, Partes I y III del
proyecto y el estado real del codigo de este repositorio.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Entrada:
    id: str
    tema: str
    titulo: str
    palabras_clave: dict[str, int]
    respuesta: str
    comando: str | None = None


TEMAS: dict[str, str] = {
    "motivos": "Motivos y contexto",
    "tecnologia": "Tecnologías",
    "datos": "Datos y Moodle",
    "funcional": "Funcionalidades",
    "estado": "Estado del proyecto",
    "legal": "Marco legal",
}


ENTRADAS: list[Entrada] = [
    # ------------------------------------------------------------------
    # Motivos y contexto
    # ------------------------------------------------------------------
    Entrada(
        id="porque",
        tema="motivos",
        titulo="¿Por qué se migró?",
        comando="porque",
        palabras_clave={
            "por que": 3, "porque": 3, "motivo": 3, "razon": 3, "justific": 3,
            "objetivo": 2, "para que": 2, "migr": 1, "reimplement": 2, "reescrib": 2, "cambi": 2,
        },
        respuesta=(
            "<b>¿Por qué migrar de Laravel a Python?</b>\n\n"
            "La versión original funciona en producción, pero envejeció técnicamente:\n"
            "• <b>PHP 7.4 fuera de soporte</b> (EOL desde noviembre de 2022) y Inertia.js cambió de versión mayor.\n"
            "• <b>Alto acoplamiento al schema de Moodle</b>: el dominio dependía directamente de las tablas <code>mdl_*</code>.\n"
            "• <b>Sin tests automatizados</b>: cualquier cambio en el mapeo de notas era riesgoso.\n\n"
            "Libretas.py reimplementa el sistema en Python con una arquitectura más limpia y mantenible, "
            "aprovechando los requisitos reales relevados en producción."
        ),
    ),
    Entrada(
        id="antecedente",
        tema="motivos",
        titulo="El sistema original (Laravel)",
        comando="original",
        palabras_clave={
            "original": 3, "antecedente": 3, "anterior": 2, "viejo": 2, "legado": 3,
            "fanzolato": 3, "version previa": 3, "laravel": 1,
        },
        respuesta=(
            "<b>El sistema original</b>\n\n"
            "Se construyó como favor a una escuela primaria, sin contrato de cesión:\n"
            "• <b>Laravel 8.75 / PHP 7.4</b> con MySQL.\n"
            "• ~<b>4.000 líneas</b> de código propio.\n"
            "• <b>20 modelos</b> Eloquent (16 sobre tablas de Moodle + 4 propios), <b>9 controllers</b>, "
            "<b>11 migraciones</b>, <b>24 vistas</b> Blade.\n"
            "• Lectura directa de la BD de Moodle (sin Web Services).\n"
            "• RBAC con 5 roles y 18 permisos; PDFs con DomPDF.\n\n"
            "Sigue siendo el código de referencia: los requisitos de Libretas.py se reconstruyeron por ingeniería inversa."
        ),
    ),
    Entrada(
        id="deuda",
        tema="motivos",
        titulo="Deuda técnica del original",
        comando="deuda",
        palabras_clave={
            "deuda": 3, "limitacion": 3, "problema": 3, "falla": 2, "defecto": 2,
            "mal$": 1, "debilidad": 3, "error": 1,
        },
        respuesta=(
            "<b>Deuda técnica detectada en el sistema Laravel</b>\n\n"
            "• Versión de PHP sin soporte de seguridad.\n"
            "• Dominio atado al schema interno de Moodle (16 modelos apuntando a <code>mdl_*</code>).\n"
            "• Cobertura de tests nula.\n"
            "• Restos de depuración (<code>dd()</code> comentados en los middlewares, comentarios sueltos).\n"
            "• Consultas SQL crudas en el reporte de actividades sin validar los parámetros <code>minimo</code>/<code>maximo</code>.\n"
            "• <code>InformeController</code> de ~1000 líneas concentrando casi toda la lógica de informes.\n\n"
            "Libretas.py ataca esto separando responsabilidades (routers por dominio, <code>utils/escala.py</code> aislado) "
            "y planificando un adaptador para Moodle."
        ),
    ),
    Entrada(
        id="desafios",
        tema="motivos",
        titulo="Desafíos de la migración",
        comando="desafios",
        palabras_clave={
            "desafio": 3, "riesgo": 3, "dificultad": 3, "dificil": 3, "reto": 3,
            "mitig": 3, "complicad": 2, "obstaculo": 3,
        },
        respuesta=(
            "<b>Principales desafíos y cómo se mitigan</b>\n\n"
            "• <b>Acoplamiento a Moodle</b> → patrón Repository/Adapter que aísla las tablas <code>mdl_*</code>.\n"
            "• <b>Alcance excesivo</b> (20 modelos, 24 vistas) → MVP acotado con priorización MoSCoW.\n"
            "• <b>Datos sensibles de menores</b> → mínimo privilegio, bcrypt, auditoría y nunca datos reales en el repo.\n"
            "• <b>Defensa sin acceso al Moodle de producción</b> → datos semilla ficticios (y dump anonimizado a futuro).\n"
            "• <b>Escala oficial exacta</b> → mapeo aislado en un módulo propio para poder testearlo.\n"
            "• <b>Tiempo limitado</b> → sprints semanales y backlog priorizado."
        ),
    ),
    # ------------------------------------------------------------------
    # Tecnologias
    # ------------------------------------------------------------------
    Entrada(
        id="stack",
        tema="tecnologia",
        titulo="Stack: antes y después",
        comando="stack",
        palabras_clave={
            "stack": 3, "tecnolog": 3, "framework": 3, "lenguaje": 3, "herramient": 2,
            "fastapi": 2, "php": 2, "python": 2, "laravel": 2, "libreria": 2, "uvicorn": 2,
        },
        respuesta=(
            "<b>Stack: Laravel → Python</b>\n\n"
            "• Lenguaje: PHP 7.4 → <b>Python 3.13</b>\n"
            "• Framework: Laravel 8.75 → <b>FastAPI</b> (servido con Uvicorn)\n"
            "• ORM: Eloquent → <b>SQLAlchemy 2.x</b>\n"
            "• Plantillas: Blade + Inertia.js → <b>Jinja2 + Tailwind CSS</b>\n"
            "• BD: MySQL (propia + Moodle) → <b>SQLite</b> en el MVP actual\n"
            "• PDF: DomPDF → <b>impresión nativa del navegador</b> (<code>@media print</code>)\n"
            "• Contraseñas: bcrypt en ambos\n\n"
            "Más detalle: /orm, /plantillas, /bd, /pdf."
        ),
    ),
    Entrada(
        id="orm",
        tema="tecnologia",
        titulo="Eloquent vs SQLAlchemy",
        comando="orm",
        palabras_clave={
            "orm$": 3, "eloquent": 3, "sqlalchemy": 3, "mapped": 2, "relacion": 1,
            "belongsto": 3, "hasmany": 3, "query": 1, "consulta": 1,
        },
        respuesta=(
            "<b>Eloquent → SQLAlchemy 2.x</b>\n\n"
            "• Eloquent es Active Record: el modelo se guarda solo (<code>$user-&gt;save()</code>).\n"
            "• SQLAlchemy usa <b>Unit of Work</b>: los cambios se confirman con una <code>Session</code> "
            "(<code>db.add(obj)</code> + <code>db.commit()</code>).\n"
            "• Las columnas se declaran tipadas con <code>Mapped[...]</code> y <code>mapped_column()</code>.\n"
            "• <code>belongsTo</code>/<code>hasMany</code> pasan a <code>relationship()</code> + <code>ForeignKey</code>.\n"
            "• La sesión de BD se inyecta en cada endpoint con <code>Depends(get_db)</code> "
            "(ver <code>app/dependencies.py</code>)."
        ),
    ),
    Entrada(
        id="plantillas",
        tema="tecnologia",
        titulo="Blade vs Jinja2",
        comando="plantillas",
        palabras_clave={
            "blade": 3, "jinja": 3, "plantilla": 3, "template": 3, "vista": 2,
            "frontend": 3, "tailwind": 3, "inertia": 3, "html": 2, "interfaz": 2, "pantalla": 1,
        },
        respuesta=(
            "<b>Blade (+ Inertia) → Jinja2 + Tailwind</b>\n\n"
            "• La sintaxis es muy parecida: <code>{{ variable }}</code>, <code>{% if %}</code>, <code>{% for %}</code>.\n"
            "• <code>@extends</code>/<code>@section</code> de Blade equivalen a <code>{% extends %}</code>/<code>{% block %}</code>.\n"
            "• Se eliminó Inertia.js: todo se renderiza en el servidor, sin SPA.\n"
            "• Tailwind CSS se carga por CDN.\n"
            "• De 24 vistas Blade (23 eran PDFs de informes) se pasó a 14 plantillas Jinja2 "
            "en <code>app/templates/</code>."
        ),
    ),
    Entrada(
        id="arquitectura",
        tema="tecnologia",
        titulo="Arquitectura y estructura",
        comando="arquitectura",
        palabras_clave={
            "arquitectura": 3, "estructura": 3, "carpeta": 2, "organiz": 2, "capa": 2,
            "controller": 3, "controlador": 3, "router": 3, "ruta": 2, "endpoint": 3, "mvc": 3,
        },
        respuesta=(
            "<b>Arquitectura: de controllers a routers</b>\n\n"
            "• Los <b>9 controllers</b> de Laravel pasan a <b>6 routers</b> de FastAPI agrupados por dominio: "
            "<code>auth</code>, <code>cursos</code>, <code>libretas</code>, <code>admin</code>, "
            "<code>auditoria</code>, <code>public</code>.\n"
            "• Los middlewares de ruta se reemplazan por <b>dependencias</b> (<code>Depends(requiere_login)</code>).\n"
            "• La lógica de negocio sale de los controllers: el mapeo de notas vive en <code>app/utils/escala.py</code> "
            "y la auditoría en <code>app/utils/auditoria.py</code>.\n"
            "• Configuración central en <code>app/config.py</code>.\n"
            "• Diseño previsto: patrón <b>Repository/Adapter</b> para aislar la lectura de Moodle (/moodle)."
        ),
    ),
    # ------------------------------------------------------------------
    # Datos y Moodle
    # ------------------------------------------------------------------
    Entrada(
        id="moodle",
        tema="datos",
        titulo="Integración con Moodle",
        comando="moodle",
        palabras_clave={
            "moodle": 3, "mdl": 3, "adapter": 3, "adaptador": 3, "repository": 3,
            "repositorio": 1, "integra": 2, "web service": 3, "aula virtual": 3,
        },
        respuesta=(
            "<b>Integración con Moodle</b>\n\n"
            "<b>Antes (Laravel):</b> segunda conexión MySQL a la BD de Moodle y 16 modelos Eloquent "
            "apuntando directo a tablas como <code>mdl_course</code>, <code>mdl_grade_items</code>, "
            "<code>mdl_grade_grades</code> y <code>mdl_user</code>.\n\n"
            "<b>Diseño en Python:</b>\n"
            "• Lectura <b>solo lectura</b>: el sistema <b>nunca escribe</b> en Moodle (supuesto S-03).\n"
            "• El estado activado/desactivado de las evaluaciones va a una tabla espejo propia (S-04).\n"
            "• Un <b>adaptador</b> aísla el schema <code>mdl_*</code> y puede reemplazarse por un mock en tests.\n\n"
            "<b>Estado actual:</b> el MVP todavía usa datos semilla en SQLite en lugar de la conexión real "
            "(ver /pendiente)."
        ),
    ),
    Entrada(
        id="bd",
        tema="datos",
        titulo="Bases de datos",
        comando="bd",
        palabras_clave={
            "base de datos": 3, "bd$": 3, "mysql": 3, "sqlite": 3, "conexion": 2,
            "schema": 2, "esquema": 2, "alembic": 3, "seed": 3, "semilla": 3, "persist": 2,
        },
        respuesta=(
            "<b>Bases de datos</b>\n\n"
            "<b>Laravel:</b> MySQL doble — <code>tla_gestion</code> (usuarios, roles, permisos, institución) "
            "y la BD de Moodle; 11 migraciones de Laravel.\n\n"
            "<b>Libretas.py hoy:</b>\n"
            "• <b>SQLite</b> local (<code>libretas.db</code>) con SQLAlchemy 2.x.\n"
            "• Tablas propias: <code>usuarios</code>, <code>cursos</code>, <code>alumnos</code>, "
            "<code>institucion</code>, <code>auditoria</code>.\n"
            "• Las tablas se crean al iniciar (<code>create_all</code>) y se cargan con "
            "<code>python -m data.seed</code> (1° a 6° grado, 12 cursos, alumnos ficticios).\n\n"
            "<b>Planificado:</b> migraciones versionadas con Alembic y esquema Moodle separado de solo lectura."
        ),
    ),
    Entrada(
        id="modelos",
        tema="datos",
        titulo="Modelos y entidades",
        comando="modelos",
        palabras_clave={
            "modelo": 3, "entidad": 3, "tabla": 2, "clase": 2, "der$": 2, "diagrama": 1,
        },
        respuesta=(
            "<b>Modelos: 20 → 5</b>\n\n"
            "<b>Laravel (20):</b> 4 propios (User, Rol, Permiso, Institucion) + 16 sobre Moodle "
            "(Curso, Categoria, Evaluacion, Calificacion, Periodo, UserMoodle, Assign, Data, etc.).\n\n"
            "<b>Libretas.py (5, en <code>app/models/</code>):</b>\n"
            "• <code>Usuario</code> — email, hash de contraseña, nombre, rol.\n"
            "• <code>Curso</code> y <code>Alumno</code> — reemplazan por ahora a las tablas de Moodle.\n"
            "• <code>Institucion</code> — datos del establecimiento (nombre, CUE, etc.).\n"
            "• <code>EventoAuditoria</code> — nuevo, no existía en el original.\n\n"
            "Los modelos de actividades y del módulo Data de Moodle quedaron fuera del MVP (/descartado)."
        ),
    ),
    # ------------------------------------------------------------------
    # Funcionalidades
    # ------------------------------------------------------------------
    Entrada(
        id="escalas",
        tema="funcional",
        titulo="Escalas de calificación",
        comando="escalas",
        palabras_clave={
            "escala": 3, "nota": 2, "calificacion": 2, "cualitativ": 3, "literal": 3,
            "mapeo": 3, "helpers": 3, "convivencia": 3, "lectura": 2, "grado": 1, "ciclo": 2,
            "nl$": 2, "mb$": 2, "epp": 2, "s/c": 3,
        },
        respuesta=(
            "<b>Escalas de calificación</b>\n\n"
            "La regla venía de <code>helpers.php::calificaciones()</code> y ahora vive en "
            "<code>app/utils/escala.py</code>.\n\n"
            "<b>1° y 2° grado:</b> 10 → <b>LA</b> · 8–9 → <b>L</b> · 6–7 → <b>EP</b> · 1–5 → <b>NL</b>\n"
            "<b>3° grado en adelante:</b>\n"
            "• Lectura y Convivencia: 10 → <b>S</b> · 8–9 → <b>MB</b> · 6–7 → <b>B</b> · 1–5 → <b>R</b>\n"
            "• Otras áreas: nota numérica con coma decimal (8,50).\n\n"
            "<b>Casos especiales:</b> sin nota → <b>S/C</b>; inasistencias en 0 → <b>-</b>.\n"
            "<i>Nota:</i> el original tenía variantes por año (por ejemplo, EPPA en algunos ciclos lectivos).\n\n"
            "Para convertir una nota: <code>/convertir 8 2</code> (nota 8 en 2° grado)."
        ),
    ),
    Entrada(
        id="libretas",
        tema="funcional",
        titulo="Generación de libretas",
        comando="generacion",
        palabras_clave={
            "libreta": 3, "boletin": 3, "due$": 3, "informe": 2, "trimestre": 2,
            "periodo": 2, "progresiv": 3, "alumno": 1,
        },
        respuesta=(
            "<b>Generación de libretas</b>\n\n"
            "• Se elige curso + alumno + período y se ve una <b>vista previa imprimible</b>.\n"
            "• Reproduce los dos formatos del sistema original: <b>DUE</b> para 1°–2° e <b>Informe</b> para 3°–6°.\n"
            "• <b>Llenado progresivo</b>: solo muestra los trimestres ya cursados; "
            "\"Calificación final\" agrega el promedio anual.\n"
            "• Cada generación queda registrada en la auditoría.\n\n"
            "Pendiente: libreta de curso completo en un único PDF (RF-14).\n\n"
            "Para ver la libreta de un alumno desde acá: /cursos o <code>/libreta &lt;legajo&gt;</code>."
        ),
    ),
    Entrada(
        id="pdf",
        tema="funcional",
        titulo="PDF e impresión",
        comando="pdf",
        palabras_clave={
            "pdf": 3, "imprim": 3, "impresion": 3, "dompdf": 3, "weasyprint": 3,
            "print": 3, "descarg": 2, "apaisad": 3,
        },
        respuesta=(
            "<b>PDF: DomPDF → navegador</b>\n\n"
            "• <b>Laravel:</b> DomPDF generaba los PDFs en el servidor (23 plantillas de exportación).\n"
            "• <b>Plan original:</b> WeasyPrint.\n"
            "• <b>Implementado:</b> impresión nativa del navegador con <code>window.print()</code> y "
            "estilos <code>@media print</code>, en hoja legal apaisada. "
            "Evita dependencias nativas pesadas en Windows y el resultado se guarda como PDF desde el diálogo de impresión."
        ),
    ),
    Entrada(
        id="roles",
        tema="funcional",
        titulo="Roles y permisos",
        comando="roles",
        palabras_clave={
            "rol": 3, "permiso": 3, "rbac": 3, "middleware": 3, "autoriz": 3,
            "acceso": 2, "directivo": 2, "administrador": 2, "preceptor": 2,
        },
        respuesta=(
            "<b>Roles y permisos</b>\n\n"
            "<b>Laravel:</b> RBAC completo — 5 roles (Administrador, Directivo, Secretario, Preceptor, Usuario), "
            "18 permisos, relaciones M:N rol-permiso y usuario-permiso, y middlewares <code>TieneRol</code>/<code>TienePermiso</code>.\n\n"
            "<b>Libretas.py hoy:</b> cada usuario tiene un <b>rol</b> como campo, se administra desde el ABM de usuarios "
            "y todas las rutas internas exigen sesión activa.\n\n"
            "<b>Pendiente:</b> permisos granulares por rol (RF-06) con dependencias de FastAPI."
        ),
    ),
    Entrada(
        id="seguridad",
        tema="funcional",
        titulo="Login y seguridad",
        comando="seguridad",
        palabras_clave={
            "login": 3, "sesion": 3, "autentic": 3, "contrasen": 3, "password": 3,
            "bcrypt": 3, "seguridad": 3, "cookie": 3, "hash": 3,
        },
        respuesta=(
            "<b>Login y seguridad</b>\n\n"
            "• Login con email y contraseña; contraseñas con hash <b>bcrypt</b>.\n"
            "• Sesión server-side con cookie firmada (<code>SessionMiddleware</code> de Starlette + itsdangerous), "
            "en lugar del sistema de auth de Laravel.\n"
            "• Logout invalida la sesión.\n"
            "• Login y logout quedan en la auditoría.\n\n"
            "Previsto en requerimientos: HTTPS forzado, cookies <code>Secure</code>/<code>SameSite</code> y rate limiting en el login."
        ),
    ),
    Entrada(
        id="auditoria",
        tema="funcional",
        titulo="Auditoría (nueva)",
        comando="auditoria",
        palabras_clave={
            "auditor": 3, "registro": 2, "log$": 2, "logs$": 2, "trazab": 3, "historial": 3, "quien": 1,
        },
        respuesta=(
            "<b>Auditoría — funcionalidad nueva</b>\n\n"
            "El sistema Laravel no registraba quién hacía qué. Libretas.py agrega la tabla <code>auditoria</code> "
            "(<code>EventoAuditoria</code>) con usuario, acción, detalle, IP y fecha.\n\n"
            "Se registran: login/logout, alta/baja/modificación de usuarios, cambios en la institución y cada libreta generada. "
            "Se consulta desde la sección \"Auditoría\".\n\n"
            "Responde a la Ley 25.326 y a la Ley 26.061 (trazabilidad del acceso a datos de menores)."
        ),
    ),
    Entrada(
        id="evaluaciones",
        tema="funcional",
        titulo="Activar/desactivar evaluaciones",
        comando="evaluaciones",
        palabras_clave={
            "evaluacion": 3, "activar": 3, "desactivar": 3, "locked": 3, "bloque": 2,
            "e1$": 2, "e18$": 2, "cerrar": 1,
        },
        respuesta=(
            "<b>Activar/desactivar evaluaciones</b>\n\n"
            "<b>Laravel:</b> <code>EvaluacionesController</code> cambiaba el campo <code>locked</code> directamente en "
            "<code>mdl_grade_items</code>, por evaluación, por sección o por trimestre (E1–E6, E7–E12, E13–E18).\n\n"
            "<b>Rediseño:</b> como Libretas.py <b>no escribe en Moodle</b>, ese estado se guardará en una tabla espejo propia "
            "(supuesto S-04; RF-10 a RF-12).\n\n"
            "<b>Estado:</b> pendiente; depende de la conexión real con Moodle."
        ),
    ),
    # ------------------------------------------------------------------
    # Estado del proyecto
    # ------------------------------------------------------------------
    Entrada(
        id="migrado",
        tema="estado",
        titulo="Qué ya se migró",
        comando="migrado",
        palabras_clave={
            "migrado": 3, "implementad": 3, "hecho": 3, "listo": 3, "funcionalidad": 2,
            "avance": 3, "tiene": 1, "terminad": 3, "funciona": 1, "ya$": 1,
        },
        respuesta=(
            "<b>Qué ya está implementado</b>\n\n"
            "• Portada pública y login con bcrypt.\n"
            "• Dashboard con indicadores (cursos, alumnos, grados).\n"
            "• Listado de cursos y de alumnos por curso.\n"
            "• Libreta individual con vista imprimible (DUE 1°–2°, Informe 3°–6°) y llenado progresivo.\n"
            "• Mapeo de notas a escala (<code>utils/escala.py</code>).\n"
            "• ABM de usuarios y datos institucionales.\n"
            "• Auditoría de acciones.\n"
            "• Protección de rutas internas.\n"
            "• Este bot: consulta de cursos, alumnos y libretas, y conversión de notas a escala 🙂"
        ),
    ),
    Entrada(
        id="descartado",
        tema="estado",
        titulo="Qué quedó fuera (Won't)",
        comando="descartado",
        palabras_clave={
            "descart": 3, "fuera": 3, "afuera": 3, "excluid": 3, "won$": 3,
            "no se migr": 3, "sacad": 2, "elimin": 1, "dejo": 2, "quedo": 1,
        },
        respuesta=(
            "<b>Fuera del MVP (Won't)</b>\n\n"
            "Funcionalidades del original que no se migran este año:\n"
            "• RF-W1 Reportes de actividades de Moodle (foros, cuestionarios, tareas).\n"
            "• RF-W2 Módulo Data custom de Moodle.\n"
            "• RF-W3 Libro de promedios y reportes de faltantes/depuración.\n"
            "• RF-W4 Dashboard analítico.\n\n"
            "Ideas nuevas también postergadas: firma digital (W5), portal para familias (W6) y "
            "notificaciones por email/WhatsApp (W7).\n\n"
            "Motivo: priorizar el núcleo (de notas de Moodle a libreta oficial)."
        ),
    ),
    Entrada(
        id="pendiente",
        tema="estado",
        titulo="Qué falta",
        comando="pendiente",
        palabras_clave={
            "pendiente": 3, "falta": 3, "futuro": 3, "proximo": 3, "todavia": 2,
            "roadmap": 3, "siguiente": 2, "resta": 2, "queda": 1,
        },
        respuesta=(
            "<b>Pendiente</b>\n\n"
            "• Adaptador de lectura real a Moodle (hoy se usan datos semilla).\n"
            "• Activar/desactivar evaluaciones con tabla espejo.\n"
            "• Libreta de curso completo en un único PDF.\n"
            "• Permisos granulares por rol.\n"
            "• Migraciones con Alembic.\n"
            "• Tests automatizados del mapeo de escalas (meta: ≥ 95% de cobertura).\n"
            "• Dump SQL anonimizado y despliegue de demo en VPS."
        ),
    ),
    Entrada(
        id="numeros",
        tema="estado",
        titulo="Comparación en números",
        comando="numeros",
        palabras_clave={
            "numero": 3, "cuant": 3, "linea": 3, "loc$": 3, "tamano": 3, "metric": 3,
            "comparac": 2, "diferencia": 2, "versus": 1, "vs$": 1,
        },
        respuesta=(
            "<b>Laravel vs Libretas.py en números</b>\n\n"
            "• Código propio: ~4.000 líneas → ~1.100 líneas de Python en la app.\n"
            "• Modelos: 20 → 5.\n"
            "• Controllers/routers: 9 → 6.\n"
            "• Vistas/plantillas: 24 Blade → 14 Jinja2.\n"
            "• Migraciones: 11 → 0 (tablas por <code>create_all</code>; Alembic pendiente).\n\n"
            "La reducción se explica por el alcance acotado del MVP y por haber dejado afuera los reportes de Moodle."
        ),
    ),
    # ------------------------------------------------------------------
    # Marco legal
    # ------------------------------------------------------------------
    Entrada(
        id="legal",
        tema="legal",
        titulo="Marco legal y licencia",
        comando="legal",
        palabras_clave={
            "ley": 3, "legal": 3, "licencia": 3, "derecho": 2, "propiedad": 3,
            "datos personales": 3, "normativa": 3, "menor": 2, "privacidad": 3,
        },
        respuesta=(
            "<b>Marco legal</b>\n\n"
            "• <b>Ley 11.723</b> (propiedad intelectual): el código original se hizo sin contrato de cesión, "
            "así que la titularidad permite reimplementarlo. Libretas.py tiene licencia propietaria, "
            "\"Todos los derechos reservados\".\n"
            "• <b>Ley 25.326</b> (datos personales): bcrypt, control de acceso, auditoría.\n"
            "• <b>Ley 26.061</b> (protección de NNyA): privacidad de los datos de menores.\n"
            "• <b>Ley 26.206</b> y Régimen Académico de San Juan: definen el formato y las escalas de la libreta.\n"
            "• <b>Ley 26.388</b> (delitos informáticos): justifica no exponer la BD de Moodle.\n\n"
            "En el repositorio nunca se usan datos reales de alumnos."
        ),
    ),
    # ------------------------------------------------------------------
    # Conversacion general (no aparecen en /temas)
    # ------------------------------------------------------------------
    Entrada(
        id="saludo",
        tema="general",
        titulo="Saludo",
        palabras_clave={"hola": 3, "buenas": 3, "buen dia": 3, "buenos dias": 3, "hey$": 2, "que tal": 2},
        respuesta=(
            "¡Hola! 👋 Respondo consultas sobre la migración de las libretas de Laravel a Python.\n"
            "Escribí tu pregunta o usá /temas para ver las opciones."
        ),
    ),
    Entrada(
        id="identidad",
        tema="general",
        titulo="¿Qué hace este bot?",
        palabras_clave={
            "quien sos": 3, "que sos": 3, "que podes": 3, "que haces": 3, "ayuda": 3,
            "ayudame": 3, "como te uso": 3, "como funcionas": 3,
        },
        respuesta=(
            "Soy el asistente de <b>Libretas.py</b>. Puedo:\n"
            "• Mostrar cursos, alumnos y la libreta de cada alumno (/cursos, /buscar, /libreta).\n"
            "• Convertir una nota a la escala de la libreta (/convertir 8 2).\n"
            "• Responder sobre la migración del sistema de Laravel a Python (/temas).\n\n"
            "Usá /ayuda para ver todos los comandos."
        ),
    ),
    Entrada(
        id="gracias",
        tema="general",
        titulo="Agradecimiento",
        palabras_clave={"gracias": 3, "genial": 2, "joya": 2, "perfecto": 2, "chau": 3, "adios": 3},
        respuesta="¡De nada! Si tenés otra consulta, escribila o usá /temas.",
    ),
]


def por_id(entrada_id: str) -> Entrada | None:
    return next((e for e in ENTRADAS if e.id == entrada_id), None)


def por_comando(comando: str) -> Entrada | None:
    return next((e for e in ENTRADAS if e.comando == comando), None)


def por_tema(tema: str) -> list[Entrada]:
    return [e for e in ENTRADAS if e.tema == tema]
