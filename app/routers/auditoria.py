from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.dependencies import get_db, requiere_login
from app.models import EventoAuditoria, Usuario


router = APIRouter()
templates = None


@router.get("/auditoria", response_class=HTMLResponse)
def listar_eventos(
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requiere_login),
):
    eventos = db.query(EventoAuditoria).order_by(EventoAuditoria.fecha.desc()).limit(100).all()
    total = db.query(EventoAuditoria).count()

    return templates.TemplateResponse(
        request=request,
        name="auditoria.html",
        context={
            "titulo": "Auditoría",
            "ruta_activa": "auditoria",
            "usuario": usuario,
            "eventos": eventos,
            "total": total,
        },
    )
