from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Institucion(Base):
    __tablename__ = "instituciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(150))
    cue: Mapped[str] = mapped_column(String(20), default="")
    cuit: Mapped[str] = mapped_column(String(20), default="")
    director: Mapped[str] = mapped_column(String(120), default="")
    vicedirector: Mapped[str] = mapped_column(String(120), default="")
    secretario: Mapped[str] = mapped_column(String(120), default="")
    calle: Mapped[str] = mapped_column(String(150), default="")
    numero: Mapped[str] = mapped_column(String(10), default="")
    localidad: Mapped[str] = mapped_column(String(80), default="")
    provincia: Mapped[str] = mapped_column(String(80), default="")
