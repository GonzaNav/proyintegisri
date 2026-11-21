# Proyecto Integrador — Libretas.py

Sistema web de gestión de **libretas de calificaciones para Nivel Primario**, integrado con una instalación Moodle modificada.

> **Espacio curricular:** Práctica Profesionalizante II
> **Docente a cargo:** Prof. Emir Zatta
> **Carrera:** Tecnicatura Superior en Desarrollo de Software — Instituto Superior en Redes e Informática (ISRI)
> **Año académico:** 2026
> **Autor:** Gonzalo Naveda

---

## Sobre el proyecto

En las escuelas de Nivel Primario de la provincia de San Juan, la confección de libretas de calificaciones sigue siendo en muchos casos una tarea manual o asistida por planillas de cálculo. Esto produce demoras, riesgo de error humano al trasladar notas, falta de auditoría sobre quién modifica qué información y exposición innecesaria de datos personales de niñas, niños y adolescentes.

Varias de estas instituciones ya utilizan Moodle como aula virtual y allí los docentes cargan las calificaciones reales del trimestre. Sin embargo, Moodle no produce por sí mismo libretas con el formato oficial exigido por la provincia (escalas cualitativas `LA / L / EP / NL` para primer ciclo, `S / MB / B / R` para segundo y tercer ciclo, encabezados institucionales, espacios para firmas).

Este proyecto no parte de cero. Hace algunos años construí una primera versión funcional en **Laravel 8** para una institución de Nivel Primario, que aún hoy se utiliza en producción. Aquella experiencia me permitió relevar los requisitos reales del flujo del docente e identificar puntos de fricción con la plataforma Moodle, y al mismo tiempo dejó expuestas limitaciones técnicas (PHP fuera de soporte, alto acoplamiento al schema de Moodle, ausencia de tests) que **Libretas.py** viene a corregir, reimplementando el sistema en Python con una arquitectura más limpia y mantenible.

## Stack técnico

- **Backend:** Python 3.13 · FastAPI · SQLAlchemy 2.x
- **Frontend:** Jinja2 + Tailwind CSS (vía CDN)
- **Base de datos:** SQLite
- **Autenticación:** sesiones server-side con cookies firmadas (`SessionMiddleware` de Starlette) + `bcrypt` para hashing de contraseñas
- **Generación de PDF:** impresión nativa del navegador (`window.print()` + `@media print`), con formato apaisado legal

## Estructura del repositorio

```
proyintegisri/
├── docs/                  # Documentación del proyecto integrador
│   ├── 01_Plan_de_Trabajo.docx
│   ├── 02_Parte_I_Problematica.docx
│   ├── 03_Parte_II_LinkedIn.docx
│   ├── 04_Parte_III_Requerimientos.docx
│   ├── 05_Parte_IV_Casos_de_Uso.png
│   ├── 06_Parte_V_Diagrama_de_Clases.png
│   ├── 07_Parte_V_DER.png
│   ├── 08_Plan_de_Trabajo_Bot_Telegram.docx / .pdf  # Plan de Trabajo con el bot incorporado
│   ├── pantallas/         # Pantallas mockup del Parcial 1
│   ├── bot_telegram.md    # Documentación del bot de consultas
│   └── practica_git.md    # Registro de los 10 comandos Git (Parte VII)
├── app/                   # Código fuente de la aplicación FastAPI
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   ├── security.py
│   ├── models/            # Modelos SQLAlchemy
│   ├── routers/           # Endpoints HTTP agrupados por dominio
│   ├── templates/         # Plantillas Jinja2
│   ├── static/            # Recursos estáticos
│   └── utils/             # Utilidades (escala de notas, auditoría)
├── bot/                   # Bot de Telegram de consultas sobre la migración
├── data/
│   └── seed.py            # Datos semilla (1°–6° grado, 12 cursos, alumnos)
├── tests/                 # Tests con pytest
├── .env.example           # Plantilla de variables de entorno (token del bot)
├── requirements.txt
├── LICENSE                # Todos los derechos reservados — Ley 11.723
└── README.md
```

## Cómo correr el proyecto localmente

```bash
# 1. Clonar el repositorio
git clone https://github.com/GonzaNav/proyintegisri.git
cd proyintegisri

# 2. Crear y activar un entorno virtual
python -m venv .venv
.venv\Scripts\activate          # Windows (PowerShell)
# source .venv/bin/activate     # Linux / Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Inicializar la base de datos con datos de ejemplo
python -m data.seed

# 5. Levantar el servidor de desarrollo
uvicorn app.main:app --reload
```

Una vez levantado, abrir [http://127.0.0.1:8000](http://127.0.0.1:8000) en el navegador.

### Credenciales de prueba

| Usuario | Contraseña | Rol |
|---|---|---|
| `gnaveda@novalido.com` | `admin123` | Directivo |

### Bot de Telegram

```bash
# 1. Copiar .env.example como .env y completar BOT_KEY con el token de @BotFather
# 2. Iniciar el bot (queda escuchando hasta Ctrl+C)
python -m bot
```

Los tests se ejecutan con `python -m pytest tests/`. El detalle del bot está en [`docs/bot_telegram.md`](./docs/bot_telegram.md).

## Funcionalidades implementadas

- **Portada pública** con descripción del sistema y marco normativo.
- **Login** con sesión por cookie firmada y hashing `bcrypt`.
- **Dashboard** con indicadores generales (cursos, alumnos, grados).
- **Listado de cursos** con tabla dinámica y filtros visuales por grado.
- **Listado de alumnos por curso** con acceso directo a generación de libreta.
- **Generación de libreta**: selección de curso + alumno + período, con vista previa imprimible que reproduce el formato oficial (DUE para 1°–2° grado e Informe para 3°–6° grado).
- **Llenado progresivo**: la libreta refleja solo los trimestres ya cursados; el periodo "Calificación final" suma el promedio anual.
- **Administración**: ABM de usuarios y edición de datos institucionales.
- **Auditoría**: registro automático de login/logout, alta/baja/modificación de usuarios y generación de libretas.
- **Protección de rutas internas**: todas las vistas autenticadas exigen sesión activa.
- **Bot de Telegram** ([@libretasPyBot](https://t.me/libretasPyBot)): responde consultas sobre la migración de Laravel a Python (motivos, tecnologías, Moodle, funcionalidades y estado del proyecto) mediante comandos, menú de temas y preguntas en lenguaje libre.

## Avance por entregables del cursado

| Parte | Descripción | Estado |
|---|---|---|
| Parte I | Problemática a resolver | Entregado |
| Parte II | Perfil de LinkedIn profesional | Entregado |
| Parte III | Requerimientos del sistema | Entregado |
| Parte IV | Diagrama UML de Casos de Uso | Entregado |
| Parte V | Diagrama UML de Clases + DER | Entregado |
| Parte VI | Repositorio en GitHub | Este repositorio |
| Parte VII | Ejercicios de los 10 comandos Git | Ver `docs/practica_git.md` |
| Parcial 1 | GUI estática (Google Sites) | Entregado (mockups en `docs/pantallas/`) |
| Parcial 2 | GUI dinámica con templates | Entregado |

## Marco normativo aplicable

El sistema se diseñó respetando:

- **Ley 11.723** — Régimen Legal de la Propiedad Intelectual (software como obra protegida).
- **Ley 25.326** — Protección de los Datos Personales.
- **Ley 26.061** — Protección Integral de los Derechos de Niñas, Niños y Adolescentes.
- **Ley 26.206** — Ley de Educación Nacional.
- **Ley 26.388** — Delitos Informáticos.
- **Régimen Académico jurisdiccional** de Nivel Primario (provincia de San Juan).

## Licencia

Todos los derechos reservados. Ver el archivo [`LICENSE`](./LICENSE) para los términos completos. Publico este código con fines exclusivamente académicos para la corrección académica del Parcial N° 2.

## Contacto

- **Autor:** Gonzalo Naveda
- **GitHub:** [@GonzaNav](https://github.com/GonzaNav)
