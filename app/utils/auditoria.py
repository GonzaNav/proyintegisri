from fastapi import Request
from sqlalchemy.orm import Session

from app.models import EventoAuditoria, Usuario


def registrar(db: Session, request: Request, usuario: Usuario | None, accion: str, detalle: str = ""):
    ip = ""
    if request.client:
        ip = request.client.host

    db.add(EventoAuditoria(
        usuario_id=usuario.id if usuario else None,
        usuario_nombre=usuario.nombre if usuario else "anonimo",
        accion=accion,
        detalle=detalle,
        ip=ip,
    ))
    db.commit()
