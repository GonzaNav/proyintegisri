# Bot de Telegram — consultas sobre la migración

Desarrollé un bot de Telegram (**@libretasPyBot**) que responde consultas sobre la migración del sistema de libretas original, construido en Laravel/PHP, hacia Libretas.py en Python/FastAPI. La idea es que cualquier persona (docentes de la cátedra, compañeros o la institución) pueda preguntar con sus propias palabras por qué migré, qué tecnologías reemplacé, cómo se resuelve la integración con Moodle o qué falta implementar, sin tener que leer toda la documentación del proyecto.

## Cómo responde

Elegí un motor de **preguntas frecuentes por palabras clave** en lugar de un modelo de IA:

- Es **determinístico**: la misma pregunta siempre recibe la misma respuesta, y todas las respuestas las redacté yo a partir de la documentación del proyecto.
- No tiene costo ni depende de servicios externos más allá de la API de Telegram.
- No expone datos del sistema: el bot no se conecta a la base de datos de la aplicación, solo conoce el texto de su base de conocimiento.

El mensaje del usuario se normaliza (minúsculas, sin tildes ni signos) y se compara contra las palabras clave de cada entrada. Cada clave tiene un peso; las claves funcionan como **raíces** (`migr` reconoce "migración", "migraron", "migrar") y algunas exigen la palabra exacta (`der$` no se activa con "derecho"). Gana la entrada con mayor puntaje. Si ninguna alcanza el mínimo, el bot ofrece botones con los temas más cercanos.

Las respuestas distinguen siempre **lo que tenía el sistema Laravel**, **lo que planifiqué** y **lo que ya está implementado**.

## Estructura

```
bot/
├── __main__.py      # Punto de entrada: python -m bot
├── config.py        # Lee BOT_KEY desde el archivo .env
├── conocimiento.py  # Base de conocimiento: 26 entradas agrupadas en 6 temas
├── motor.py         # Normalización y puntaje (no depende de Telegram)
└── handlers.py      # Comandos, botones y mensajes de Telegram
tests/
└── test_bot_motor.py
```

Separé el **motor** de los **handlers** para poder testear la lógica de respuesta sin conectarme a Telegram. Los tests verifican que cada pregunta de ejemplo reciba la respuesta correcta, que el HTML de las respuestas sea válido para Telegram y que se respeten los límites de la plataforma (largo de mensajes, formato de comandos, tamaño de los datos de los botones).

## Cómo ponerlo en marcha

1. Crear el bot en Telegram con **@BotFather** (`/newbot`), elegir nombre y usuario (debe terminar en `bot`) y copiar el token.
2. En la raíz del repositorio, copiar `.env.example` como `.env` y completar:
   ```
   BOT_KEY=<token de BotFather>
   ```
   El archivo `.env` está en `.gitignore`, así que el token nunca se sube al repositorio.
3. Instalar dependencias y ejecutar:
   ```bash
   pip install -r requirements.txt
   python -m bot
   ```
4. Abrir el bot en Telegram y enviar `/start`.

El bot funciona por **polling**: mientras el proceso está corriendo, consulta a Telegram si hay mensajes nuevos. No necesita IP pública ni HTTPS, por eso puede correr en cualquier PC. Se detiene con `Ctrl+C`. Al iniciar, el propio bot carga el menú de comandos en Telegram, así que no hace falta configurarlo a mano en BotFather.

Para correr los tests:

```bash
python -m pytest tests/
```

## Comandos

| Comando | Responde |
|---|---|
| `/start` | Bienvenida y menú de temas |
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
| `/libretas` | Generación de libretas |
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

Además de los comandos, se puede escribir cualquier pregunta, por ejemplo: "¿por qué se migró?", "¿qué escalas usa 2° grado?" o "¿cómo se conecta con Moodle?".

## Cómo agregar una pregunta

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

- Reconoce palabras, no entiende el significado: una pregunta formulada sin ninguna de las palabras clave cae en las sugerencias.
- Las respuestas son fijas. Cuando avance el proyecto (por ejemplo, al conectar Moodle de verdad) tengo que actualizar `/migrado`, `/pendiente` y las entradas afectadas.
- Por polling, responde solo mientras el proceso está corriendo. Para tenerlo disponible todo el tiempo habría que desplegarlo en un servidor.
