from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Alumno(Base):
    __tablename__ = "alumnos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(80))
    apellido: Mapped[str] = mapped_column(String(80))
    legajo: Mapped[str] = mapped_column(String(20))
    curso_id: Mapped[int] = mapped_column(ForeignKey("cursos.id"))

    curso = relationship("Curso")

    def nombre_completo(self):
        return f"{self.apellido}, {self.nombre}"
