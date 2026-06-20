from fastapi import Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Usuario


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def usuario_actual(request: Request, db: Session = Depends(get_db)) -> Usuario | None:
    uid = request.session.get("usuario_id")
    if not uid:
        return None
    return db.query(Usuario).filter(Usuario.id == uid).first()


def requiere_login(request: Request, db: Session = Depends(get_db)) -> Usuario:
    uid = request.session.get("usuario_id")
    if not uid:
        raise RedirectException("/login")
    usuario = db.query(Usuario).filter(Usuario.id == uid).first()
    if not usuario:
        raise RedirectException("/login")
    return usuario


class RedirectException(Exception):
    def __init__(self, url: str):
        self.url = url
