"""Frontière transactionnelle des services qui orchestrent plusieurs écritures."""
from functools import wraps
from fastapi import HTTPException


def atomic(function):
    @wraps(function)
    async def wrapped(db,*args,**kwargs):
        try:
            result=await function(db,*args,**kwargs)
            await db.commit()
            if result is not None:await db.refresh(result)
            return result
        except HTTPException:
            await db.rollback();raise
        except Exception:
            await db.rollback()
            # Une exception SQL brute peut contenir des paramètres confidentiels.
            raise HTTPException(500,'Échec de l’opération ; aucune écriture partielle conservée.') from None
    return wrapped
