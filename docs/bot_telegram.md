# Bot de Telegram — Libretas.py

Desarrollé un bot de Telegram (**@libretasPyBot**) que se apoya en la lógica de negocio de Libretas.py y cumple dos funciones:

1. **Consultas del sistema:** muestra los cursos, sus alumnos y la libreta de cada alumno por período, y convierte notas numéricas a la escala cualitativa de la libreta (`LA / L / EP / NL` para el primer ciclo, `S / MB / B / R` para el segundo).
2. **Consultas sobre la migración:** responde preguntas sobre la reimplementación del sistema original, construido en Laravel/PHP, hacia Python/FastAPI: por qué migré, qué tecnologías reemplacé, cómo se resuelve la integración con Moodle y qué falta implementar.

## Consultas del sistema (lógica de negocio)

El bot no duplica reglas: usa las mismas piezas que la aplicación web, así que el bot y la web muestran siempre lo mismo.

| Pieza reutilizada | Uso en el bot |
|---|---|
| `app/utils/escala.py` | Conversión de una nota a la escala según el grado y el área |
| `app/models` (`Curso`, `Alumno`) y `libretas.db` | Listado de cursos, alumnos, búsqueda y legajos |
| `construir_datos_libreta()` de `app/routers/libretas.py` | Libreta del alumno por período, con llenado progresivo y formato DUE (1°–2°) o Informe (3°–6°) |

Se puede consultar con comandos, con botones o escribiendo en lenguaje libre:

| Consulta | Comando | También entiende |
|---|---|---|
| Cursos y cantidad de alumnos | `/cursos` | "¿qué cursos hay?" |
| Alumnos de un curso | `/alumnos 3A` | "alumnos de 3°A" |
| Buscar un alumno | `/buscar quiroga` | "libreta de Quiroga" |
| Libreta de un alumno | `/libreta 01967 [1\|2\|3\|final]` | Un legajo suelto: "01967" |
| Convertir una nota | `/convertir 8 2 [lectura]` | "¿qué escala es un 8 en 2° grado?", "un 9 en 5° grado en lectura" |

Con botones se navega curso → alumno → libreta, y la libreta trae botones para cambiar de período (1°T, 2°T, 3°T, final). Si un legajo o una búsqueda coincide con varios alumnos, el bot ofrece elegir.

Los cursos y alumnos son los **datos ficticios de ejemplo** que carga `python -m data.seed`; el repositorio no contiene datos reales.

## Consultas sobre la migración

Para estas preguntas usé un motor de **preguntas frecuentes por palabras clave**, el mismo enfoque del bot visto en clase:

- Es **determinístico**: la misma pregunta siempre recibe la misma respuesta, y todas las respuestas las redacté a partir de la documentación del proyecto.
- No tiene costo ni depende de servicios externos más allá de la API de Telegram.

El mensaje del usuario se normaliza (minúsculas, sin tildes ni signos) y se compara contra las palabras clave de cada entrada. Cada clave tiene un peso; las claves funcionan como **raíces** (`migr` reconoce "migración", "migraron", "migrar") y algunas exigen la palabra exacta (`der$` no se activa con "derecho"). Gana la entrada con mayor puntaje. Si ninguna alcanza el mínimo, el bot ofrece botones con los temas más cercanos.

Cuando llega un mensaje de texto, el bot primero intenta reconocerlo como consulta del sistema (nota y grado, legajo, curso, nombre de alumno); si no lo es, lo responde con la base de preguntas frecuentes.

## Estructura

```
bot/
├── __main__.py      # Punto de entrada: python -m bot
├── config.py        # Lee BOT_KEY desde el archivo .env
├── negocio.py       # Consultas del sistema: escalas, cursos, alumnos y libretas
├── conocimiento.py  # Preguntas frecuentes sobre la migración: 26 entradas en 6 temas
├── motor.py         # Normalización y puntaje de la FAQ
└── handlers.py      # Comandos, botones y mensajes de Telegram
tests/
├── test_bot_negocio.py
└── test_bot_motor.py
```

Separé la lógica (`negocio.py`, `motor.py`) de los handlers de Telegram para poder testearla sin conectarme a la plataforma. Las pruebas de negocio usan una base SQLite en memoria, así que no dependen de `libretas.db`.

## Cómo ponerlo en marcha

1. Crear el bot en Telegram con **@BotFather** (`/newbot`), elegir nombre y usuario (debe terminar en `bot`) y copiar el token.
2. En la raíz del repositorio, copiar `.env.example` como `.env` y completar:
   ```
   BOT_KEY=<token de BotFather>
   ```
   El archivo `.env` está en `.gitignore`, así que el token nunca se sube al repositorio.
3. Instalar dependencias, cargar los datos de ejemplo (si todavía no se hizo para la aplicación web) y ejecutar:
   ```bash
   pip install -r requirements.txt
   python -m data.seed
   python -m bot
   ```
4. Abrir el bot en Telegram y enviar `/start`.

El bot funciona por **polling**: mientras el proceso está corriendo, consulta a Telegram si hay mensajes nuevos. No necesita IP pública ni HTTPS, por eso puede correr en cualquier PC. Se detiene con `Ctrl+C`. Al iniciar, el propio bot carga el menú de comandos en Telegram.

Para correr los tests:

```bash
python -m pytest tests/
```

## Comandos

**Consultas del sistema**

| Comando | Responde |
|---|---|
| `/cursos` | Cursos con botones para ver alumnos y libretas |
| `/alumnos 3A` | Alumnos de un curso con su legajo |
| `/buscar <apellido o nombre>` | Alumnos que coinciden |
| `/libreta <legajo> [1\|2\|3\|final]` | Libreta del alumno en el período indicado |
| `/convertir <nota> <grado> [área]` | Nota convertida a la escala de la libreta |

**Consultas sobre la migración**

| Comando | Responde |
|---|---|
| `/start` | Bienvenida y menú |
| `/temas` | Menú con botones por tema |
| `/ayuda` | Lista de comandos |
| `/porque` | Motivos de la migración |
| `/original` | Cómo era el sistema Laravel |
| `/deuda` | Deuda técnica del original |
| `/desafios` | Desafíos y cómo los mitigué |
| `/stack` | Tecnologías antes y después |
| `/orm` | Eloquent vs SQLAlchemy |
| `/plantillas` | Blade vs Jinja2 |
| `/arquitectura` | De controllers a routers |
| `/moodle` | Integración con Moodle |
| `/bd` | Bases de datos |
| `/modelos` | Modelos y entidades |
| `/escalas` | Escalas de calificación |
| `/generacion` | Generación de libretas |
| `/pdf` | PDF e impresión |
| `/roles` | Roles y permisos |
| `/seguridad` | Login y seguridad |
| `/auditoria` | Auditoría (funcionalidad nueva) |
| `/evaluaciones` | Activar/desactivar evaluaciones |
| `/migrado` | Qué ya está implementado |
| `/descartado` | Qué quedó fuera del MVP |
| `/pendiente` | Qué falta |
| `/numeros` | Comparación en números |
| `/legal` | Marco legal y licencia |

## Cómo agregar una pregunta frecuente

Cada respuesta es un objeto `Entrada` en `bot/conocimiento.py`:

```python
Entrada(
    id="ejemplo",
    tema="funcional",                       # uno de los temas de TEMAS
    titulo="Título del botón",
    comando="ejemplo",                      # opcional
    palabras_clave={"raiz": 3, "otra": 2, "exacta$": 2},
    respuesta="<b>Título</b>\n\nTexto en HTML de Telegram.",
)
```

Después de agregarla conviene sumar la pregunta de ejemplo a `tests/test_bot_motor.py` y correr los tests para confirmar que no le quita respuestas a otras entradas.

## Limitaciones

- El bot no pide usuario ni contraseña: es adecuado para los datos ficticios de la demo. Con datos reales de alumnos habría que restringir el acceso (por ejemplo, vincular la cuenta de Telegram con un usuario autorizado del sistema), como exigen las Leyes 25.326 y 26.061.
- El texto libre se interpreta por patrones y palabras, no por significado: una pregunta redactada de forma muy distinta deriva en sugerencias.
- Las respuestas sobre la migración son fijas: cuando avance el proyecto (por ejemplo, al conectar Moodle de verdad) tengo que actualizar `/migrado`, `/pendiente` y las entradas afectadas.
- Por polling, responde solo mientras el proceso está corriendo. Para tenerlo disponible todo el tiempo habría que desplegarlo en un servidor.
