import bcrypt


def hash_password(plano: str) -> str:
    return bcrypt.hashpw(plano.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_password(plano: str, hash_guardado: str) -> bool:
    return bcrypt.checkpw(plano.encode("utf-8"), hash_guardado.encode("utf-8"))
