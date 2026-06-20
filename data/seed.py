from app.database import Base, SessionLocal, engine
from app.models import Curso, Usuario
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

    db.close()


if __name__ == "__main__":
    seed()
