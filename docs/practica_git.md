# Práctica de los 10 comandos de Git — Parte VII

> Registro de los 10 comandos básicos de Git aplicados durante el desarrollo del proyecto integrador **Libretas.py**, alojado en este repositorio.
>
> Referencia: [freeCodeCamp — 10 comandos de Git que todo desarrollador debería saber](https://www.freecodecamp.org/espanol/news/10-comandos-de-git-que-todo-desarrollador-deberia-saber/).

A continuación documento cada comando indicando qué hace, en qué punto del proyecto lo usé y un ejemplo concreto extraído de mi flujo real de trabajo.

---

## 1. `git init`

**Qué hace:** crea un nuevo repositorio Git vacío en la carpeta actual, inicializando el directorio `.git` que contiene toda la información de versionado.

**Uso en el proyecto:** este repositorio fue creado directamente desde GitHub con la opción *"Initialize this repository with a README"*, lo que ejecuta `git init` del lado del servidor. Como demostración local, también lo probé en una carpeta temporal:

```bash
mkdir prueba-git && cd prueba-git
git init
# Initialized empty Git repository in C:/Users/TLA-SRL/prueba-git/.git/
```

---

## 2. `git clone`

**Qué hace:** descarga un repositorio remoto a la computadora local creando una copia completa con todo su historial.

**Uso en el proyecto:** clonado del repositorio una vez creado en GitHub, para empezar a trabajar localmente.

```bash
git clone https://github.com/GonzaNav/proyintegisri.git
cd proyintegisri
```

---

## 3. `git status`

**Qué hace:** muestra el estado actual del directorio de trabajo: archivos modificados, archivos nuevos sin trackear y cambios listos para commitear.

**Uso en el proyecto:** lo uso antes de cada commit para confirmar qué se va a versionar.

```bash
git status
# On branch feat/dynamic-templates
# Changes not staged for commit:
#   modified:   app/routers/libretas.py
#   modified:   app/templates/libretas_preview.html
# Untracked files:
#   app/templates/alumnos_curso.html
```

---

## 4. `git add`

**Qué hace:** mueve archivos del directorio de trabajo al área de preparación (staging), marcándolos como parte del próximo commit.

**Uso en el proyecto:** al agregar la nueva vista de alumnos por curso, junto con sus dependencias en el router y el template de selección de libreta.

```bash
git add app/templates/alumnos_curso.html app/routers/cursos.py
# Para incluir todos los cambios pendientes:
git add -A
```

---

## 5. `git commit`

**Qué hace:** registra los cambios preparados como un commit con un mensaje descriptivo.

**Uso en el proyecto:** cada bloque significativo de trabajo terminó en un commit con un mensaje en imperativo y claro. Ejemplos reales de este repositorio:

```bash
git commit -m "Agregar persistencia con SQLite y pantalla de cursos dinamica"
git commit -m "Agregar autenticacion y dashboard"
git commit -m "Ampliar sistema: auditoria, admin (usuarios+institucion), libretas con vista imprimible"
git commit -m "Adaptar libretas al modelo real del sistema antiguo (DUE 1-2 e Informe 3-6)"
```

---

## 6. `git log`

**Qué hace:** muestra el historial de commits con sus autores, fechas y mensajes.

**Uso en el proyecto:** lo uso para revisar el avance y verificar que cada día de trabajo tenga su commit correspondiente.

```bash
git log --oneline
# 2ce11eb Finalizar entrega: vista de alumnos por curso, libretas progresivas, home segun wireframe y proteccion de rutas
# c91d720 Adaptar libretas al modelo real del sistema antiguo (DUE 1-2 e Informe 3-6)
# 983ce21 Ampliar sistema: auditoria, admin (usuarios+institucion), libretas con vista imprimible
# ea3694b Agregar autenticacion y dashboard
# 30c96b0 Agregar persistencia con SQLite y pantalla de cursos dinamica
# 9afc13b Estructura inicial de FastAPI con pagina de inicio y layout base
# 5d0d949 Carga inicial: documentacion del proyecto y pantallas
```

---

## 7. `git branch`

**Qué hace:** lista, crea o elimina ramas. Permite trabajar en líneas paralelas sin afectar `main`.

**Uso en el proyecto:** creé una rama dedicada para la GUI dinámica del Parcial 2, de manera que `main` quede como una versión estable cuando llegue el momento del merge.

```bash
git branch                    # lista las ramas locales
# * feat/dynamic-templates
#   main

git branch feat/dynamic-templates    # crea la rama
```

---

## 8. `git checkout`

**Qué hace:** cambia de rama (o restaura un archivo a su versión versionada). En Git moderno también se usa `git switch` para cambiar de rama.

**Uso en el proyecto:** lo uso para moverme entre la rama de trabajo y `main` al momento de mergear.

```bash
git checkout feat/dynamic-templates     # voy a trabajar a la rama de la GUI dinámica
git checkout main                       # vuelvo a main para hacer el merge final
```

---

## 9. `git push`

**Qué hace:** envía los commits locales al repositorio remoto.

**Uso en el proyecto:** después de cada commit relevante, sincronizo el trabajo con GitHub para tener respaldo y permitir al docente revisar el avance.

```bash
git push origin feat/dynamic-templates
# Si la rama todavía no existe en el remoto, la primera vez:
git push -u origin feat/dynamic-templates
```

---

## 10. `git pull`

**Qué hace:** trae los cambios del repositorio remoto y los integra a la rama local. Equivale a `git fetch` + `git merge`.

**Uso en el proyecto:** lo aplico al volver a trabajar al día siguiente, para asegurarme de tener la última versión antes de seguir.

```bash
git pull origin feat/dynamic-templates
# Already up to date.
```

---

## Comandos adicionales utilizados

Aunque no forman parte estricta del listado de 10, durante el desarrollo apliqué también:

| Comando | Para qué |
|---|---|
| `git diff` | Ver línea por línea qué cambió antes de stagear. |
| `git merge feat/dynamic-templates` | Integrar la rama de la GUI dinámica en `main` al final del trabajo. |
| `git tag v0.1.0` | Marcar la versión entregada del Parcial 2. |
| `git stash` | Guardar trabajo pendiente cuando necesité cambiar de rama momentáneamente. |
| `git remote -v` | Verificar que el repositorio apunta al GitHub correcto. |

---

## Historial completo del repositorio

| # | Commit | Día | Descripción |
|---|---|---|---|
| 1 | `5d0d949` | 1 | Carga inicial de documentación del proyecto y pantallas |
| 2 | `9afc13b` | 2 | Estructura inicial de FastAPI con página de inicio y layout base |
| 3 | `30c96b0` | 3 | Persistencia con SQLite y pantalla de cursos dinámica |
| 4 | `ea3694b` | 4 | Autenticación y dashboard |
| 5 | `983ce21` | 4 | Auditoría, administración (usuarios e institución) y libretas imprimibles |
| 6 | `c91d720` | 5 | Adaptación de libretas al modelo real (DUE 1°-2°, Informe 3°-6°) |
| 7 | `2ce11eb` | 5 | Vista de alumnos por curso, libretas progresivas, home según wireframe y protección de rutas |

El trabajo se desarrolló sobre la rama `feat/dynamic-templates` y se mergeó a `main` al cierre del Parcial 2, etiquetando esa versión como `v0.1.0`.
