"""Initialisation CLI privée ; ne réinitialise jamais un compte existant."""
import asyncio
import os
import sys

from alembic import command
from alembic.config import Config
from sqlalchemy import select, text

import app.db  # Enregistrer tous les modèles et relations SQLAlchemy.
from app.api.v1.user.models import Roles, Users, UserRole
from app.core.database import engine, sessionlocal
from app.core.security import Hash
from app.core.seed_role import DEFAULT_ROLES


async def bootstrap():
    email = os.environ['BOOTSTRAP_ADMIN_EMAIL']
    password = os.environ['BOOTSTRAP_ADMIN_PASSWORD']
    if len(password) < 20:
        raise ValueError('Mot de passe initial insuffisant')
    async with sessionlocal() as db:
        async with db.begin():
            await db.execute(text("SELECT pg_advisory_xact_lock(hashtext('dakafarm-bootstrap'))"))
            for item in DEFAULT_ROLES:
                if not await db.scalar(select(Roles).where(Roles.name == item['name'])):
                    db.add(Roles(**item))
            await db.flush()
            admin_role = await db.scalar(select(Roles).where(Roles.name == 'admin'))
            user = await db.scalar(select(Users).where(Users.email == email))
            if user:
                assigned = await db.scalar(select(UserRole).where(
                    UserRole.user_id == user.id, UserRole.role_id == admin_role.id))
                if not assigned:
                    raise RuntimeError('Compte existant sans rôle administrateur : intervention requise')
            else:
                if await db.scalar(select(Users.id).limit(1)):
                    raise RuntimeError('Base déjà utilisée : création initiale refusée')
                user = Users(first_name='Administrateur', last_name='DAKAFARM',
                             email=email, phone='', password_hash=Hash.hash(password), is_active=True)
                db.add(user)
                await db.flush()
                db.add(UserRole(user_id=user.id, role_id=admin_role.id))
    await engine.dispose()


if __name__ == '__main__':
    try:
        command.upgrade(Config('alembic.ini'), 'head')
        asyncio.run(bootstrap())
        print('Initialisation DAKAFARM vérifiée ; aucun identifiant affiché.')
    except Exception:
        # Les exceptions SQLAlchemy peuvent contenir des paramètres privés.
        print('Initialisation DAKAFARM interrompue ; diagnostic privé requis.', file=sys.stderr)
        sys.exit(1)
