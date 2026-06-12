# Proyecto Integrador — Libretas.py

Sistema web de gestión de **libretas de calificaciones para Nivel Primario**, integrado con una instalación Moodle modificada.

> **Materia:** Práctica Profesionalizante II
> **Docente a cargo:** Prof. Emir Zatta
> **Carrera:** Tecnicatura Superior en Desarrollo de Software — Instituto Superior en Redes e Informática (ISRI)
> **Año académico:** 2026
> **Autor:** Gonzalo Naveda

---

## Sobre el proyecto

En las escuelas de la provincia de San Juan de Nivel Primario la generación de libretas de calificaciones sigue siendo, en muchas instituciones, una tarea manual o semi-asistida por planillas de cálculo. Esto produce demoras, riesgo de error humano en el traslado de notas, falta de auditoría sobre quién modifica qué y exposición innecesaria de datos personales de niñas, niños y adolescentes.

Algunas de estas instituciones ya utilizan Moodle como aula virtual y allí los docentes cargan las calificaciones reales del trimestre. Sin embargo, Moodle no produce por sí mismo libretas con el formato oficial exigido por la provincia (escalas cualitativas `LA / L / EP / NL` para primer ciclo, `S / MB / B / R` para segundo y tercer ciclo, encabezados institucionales, espacios para firmas).

Este proyecto no parte de cero. Hace algunos años, como favor a una institución educativa de Nivel Primario, construí una primera versión funcional del sistema en **Laravel 8.75** que todavía hoy se utiliza en producción. Aquella experiencia me permitió relevar los requisitos reales del flujo del docente, identificar puntos de fricción con la plataforma Moodle y entregar una solución funcional; al mismo tiempo, dejó expuestas limitaciones técnicas (PHP 7.4 fuera de soporte, alto acoplamiento al schema de Moodle, ausencia de tests) que **Libretas.py** viene a corregir, re-implementando el sistema en Python con una arquitectura más limpia y mantenible.

## Stack técnico

- **Backend:** Python 3.12 · FastAPI · SQLAlchemy 2.x · Pydantic v2
- **Frontend:** Jinja2 + Tailwind CSS
- **Base de datos:** SQLite (desarrollo)
- **Generación de PDF:** WeasyPrint
- **Autenticación:** sesiones server-side con cookies firmadas + `passlib[bcrypt]`

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
│   ├── pantallas/         # Pantallas del Parcial 1 (Google Sites)
│   └── practica_git.md    # Ejercicios de los 10 comandos Git (Parte VII)
├── app/                   # Código fuente de la aplicación FastAPI
│   ├── main.py
│   ├── routers/
│   ├── models/
│   ├── templates/         # Plantillas Jinja2
│   └── static/
├── data/
│   └── seed.py            # Datos semilla (1°–6° grado, 12 cursos)
├── tests/                 # Tests con pytest
├── requirements.txt
├── LICENSE                # Todos los derechos reservados — Ley 11.723
└── README.md
```

## Cómo correr el proyecto localmente

> **Estado actual:** el código de la aplicación se incorpora en commits posteriores a esta versión inicial del repositorio.

```bash
# 1. Clonar el repositorio
git clone https://github.com/GonzaNav/proyintegisri.git
cd proyintegisri

# 2. Crear y activar un entorno virtual
python -m venv .venv
.venv\Scripts\activate    # Windows
# source .venv/bin/activate    # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Inicializar la base de datos con datos de ejemplo
python -m data.seed

# 5. Levantar el servidor de desarrollo
uvicorn app.main:app --reload
```

Una vez levantado, abrir [http://127.0.0.1:8000](http://127.0.0.1:8000) en el navegador.

## Avance por entregables del cursado

| Parte | Descripción | Estado |
|---|---|---|
| Parte I | Problemática a resolver | ✅ Entregado |
| Parte II | Perfil de LinkedIn profesional | ✅ Entregado |
| Parte III | Requerimientos del sistema | ✅ Entregado |
| Parte IV | Diagrama UML de Casos de Uso | ✅ Entregado |
| Parte V | Diagrama UML de Clases + DER | ✅ Entregado |
| Parte VI | Repositorio en GitHub | ✅ Este repositorio |
| Parte VII | Ejercicios de los 10 comandos Git | ✅ Ver `docs/practica_git.md` |
| Parcial 1 | GUI estática en Google Sites | ✅ Entregado (ver `docs/pantallas/`) |
| Parcial 2 | GUI dinámica con templates | 🚧 En curso |

## Marco normativo aplicable

El sistema se diseña respetando:

- **Ley 11.723** — Régimen Legal de la Propiedad Intelectual (software como obra protegida).
- **Ley 25.326** — Protección de los Datos Personales.
- **Ley 26.061** — Protección Integral de los Derechos de Niñas, Niños y Adolescentes.
- **Ley 26.206** — Ley de Educación Nacional.
- **Ley 26.388** — Delitos Informáticos.
- **Régimen Académico jurisdiccional** de Nivel Primario (provincia de San Juan).

## Licencia

Todos los derechos reservados. Ver el archivo [`LICENSE`](./LICENSE) para los términos completos. Publico este código con fines exclusivamente académicos para la corrección del Parcial N° 2 por parte del docente.

## Contacto

- **Autor:** Gonzalo Naveda
- **GitHub:** [@GonzaNav](https://github.com/GonzaNav)
