import random

from app.database import Base, SessionLocal, engine
from app.models import Alumno, Curso, Institucion, Usuario
from app.security import hash_password


CURSOS = [
    ("1°", "A", 28, "María García",     "abierto"),
    ("1°", "B", 26, "Juan Pérez",       "abierto"),
    ("2°", "A", 30, "Ana Rodríguez",    "abierto"),
    ("2°", "B", 28, "Luis Sosa",        "abierto"),
    ("3°", "A", 29, "Carla Méndez",     "abierto"),
    ("3°", "B", 27, "Pedro Vega",       "abierto"),
    ("4°", "A", 30, "Lucía Fernández",  "abierto"),
    ("4°", "B", 28, "Mario Suárez",     "abierto"),
    ("5°", "A", 26, "Romina Acosta",    "abierto"),
    ("5°", "B", 25, "Diego Romero",     "abierto"),
    ("6°", "A", 24, "Sofía Castro",     "abierto"),
    ("6°", "B", 23, "Andrés Quiroga",   "abierto"),
]


NOMBRES = ["Lucía", "Martina", "Camila", "Valentina", "Sofía", "Mateo", "Benjamín", "Joaquín", "Felipe", "Tomás",
           "Emma", "Isabella", "Mía", "Olivia", "Pilar", "Bruno", "Ciro", "Lautaro", "Thiago", "Bautista"]

APELLIDOS = ["Pérez", "García", "Rodríguez", "Martínez", "López", "Sánchez", "Romero", "Fernández", "Gómez", "Díaz",
             "Torres", "Acosta", "Castro", "Vega", "Méndez", "Suárez", "Sosa", "Molina", "Quiroga", "Lucero"]


def alumnos_para_curso(curso: Curso, db) -> list[Alumno]:
    random.seed(curso.id)
    alumnos = []
    for _ in range(curso.cantidad_alumnos):
        nombre = random.choice(NOMBRES)
        apellido = random.choice(APELLIDOS)
        legajo = f"{curso.id:02d}{random.randint(100, 999):03d}"
        alumnos.append(Alumno(nombre=nombre, apellido=apellido, legajo=legajo, curso_id=curso.id))
    return alumnos


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(Curso).count() == 0:
        for grado, seccion, cantidad, docente, estado in CURSOS:
            db.add(Curso(
                grado=grado,
                seccion=seccion,
                cantidad_alumnos=cantidad,
                docente=docente,
                estado=estado,
            ))
        db.commit()
        print(f"Cargados {len(CURSOS)} cursos.")
    else:
        print("Ya hay cursos cargados.")

    if db.query(Alumno).count() == 0:
        total = 0
        for curso in db.query(Curso).all():
            alumnos = alumnos_para_curso(curso, db)
            db.add_all(alumnos)
            total += len(alumnos)
        db.commit()
        print(f"Cargados {total} alumnos.")
    else:
        print("Ya hay alumnos cargados.")

    if db.query(Usuario).count() == 0:
        db.add(Usuario(
            email="gnaveda@novalido.com",
            password_hash=hash_password("admin123"),
            nombre="Gonzalo Naveda",
            rol="Directivo",
        ))
        db.commit()
        print("Usuario admin creado.")
    else:
        print("Ya hay usuarios cargados.")

    if db.query(Institucion).count() == 0:
        db.add(Institucion(
            nombre="Escuela Primaria San José",
            cue="6603457",
            cuit="30-12345678-9",
            director="Lic. Marta Romero",
            vicedirector="Prof. Luis Pérez",
            secretario="Sra. Carla Sosa",
            calle="Av. Belgrano",
            numero="1234",
            localidad="San Juan",
            provincia="San Juan",
        ))
        db.commit()
        print("Institucion cargada.")
    else:
        print("Ya hay institucion cargada.")

    db.close()


if __name__ == "__main__":
    seed()
