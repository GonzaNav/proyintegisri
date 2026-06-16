from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


COLORES = {
    "1°": "bg-rose-100 text-rose-700",
    "2°": "bg-amber-100 text-amber-700",
    "3°": "bg-emerald-100 text-emerald-700",
    "4°": "bg-cyan-100 text-cyan-700",
    "5°": "bg-blue-100 text-blue-700",
    "6°": "bg-violet-100 text-violet-700",
}


class Curso(Base):
    __tablename__ = "cursos"

    id: Mapped[int] = mapped_column(primary_key=True)
    grado: Mapped[str] = mapped_column(String(4))
    seccion: Mapped[str] = mapped_column(String(2))
    cantidad_alumnos: Mapped[int] = mapped_column(Integer)
    docente: Mapped[str] = mapped_column(String(120))
    estado: Mapped[str] = mapped_column(String(20), default="abierto")

    def color_clase(self):
        return COLORES.get(self.grado, "bg-slate-100 text-slate-700")
