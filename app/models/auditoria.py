from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class EventoAuditoria(Base):
    __tablename__ = "auditoria"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    usuario_nombre: Mapped[str] = mapped_column(String(120))
    accion: Mapped[str] = mapped_column(String(80))
    detalle: Mapped[str] = mapped_column(String(255), default="")
    ip: Mapped[str] = mapped_column(String(45), default="")
    fecha: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    usuario = relationship("Usuario")

    def color_clase(self):
        colores = {
            "Login": "bg-slate-100 text-slate-700",
            "Logout": "bg-slate-100 text-slate-700",
            "Libreta": "bg-blue-100 text-blue-700",
            "Usuario": "bg-violet-100 text-violet-700",
            "Institucion": "bg-amber-100 text-amber-700",
        }
        for prefix, css in colores.items():
            if self.accion.startswith(prefix):
                return css
        return "bg-slate-100 text-slate-700"
