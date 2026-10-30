"""Recette locale sur base jetable ; aucune donnée du cluster, aucun secret affiché."""
from pathlib import Path
import json, os, secrets, shutil, subprocess, tempfile, time, sys

root = Path(__file__).resolve().parents[1]
private = Path(tempfile.mkdtemp(prefix='dakafarm-data-test-', dir='/tmp'))
os.chmod(private, 0o700)
suffix=secrets.token_hex(4)
net, db, api, web = [f'dakafarm-data-test-{suffix}-{kind}' for kind in ['net','db','api','web']]
app_password, admin_password = secrets.token_hex(24), secrets.token_urlsafe(32)
email = 'admin@dakafarm.qual.dgsynthex.online'
env = {'DATABASE_URL': f'postgresql+asyncpg://dakafarm:{app_password}@{db}:5432/dakafarm',
       'SECRET_KEY': secrets.token_hex(48), 'ALGORITHM': 'HS256', 'CORS_ORIGINS': 'https://dakafarm.qual.dgsynthex.online'}

def envfile(name, values):
    p = private / name
    p.write_text(''.join(f'{k}={v}\n' for k, v in values.items())); os.chmod(p, 0o600)
    return str(p)

def run(*args, input=None):
    r = subprocess.run(['docker', *args], input=input, text=True, capture_output=True)
    if r.returncode:
        (private / 'last-error.log').write_text(r.stderr + r.stdout)
        if args[0] == 'exec':
            print(r.stdout, end='')  # Le script n'émet que des noms de contrôles.
            lines = r.stderr.strip().splitlines()
            if lines and 'HTTP Error' in lines[-1]:
                print(lines[-1])
        print(r.stderr if 'unittest' in args else 'Échec Docker ; aucun identifiant affiché.'); raise RuntimeError('Recette interrompue')
    return r.stdout + r.stderr

try:
    run('network', 'create', *([] if '--browser' in sys.argv else ['--internal']), net)
    run('run', '-d', '--name', db, '--network', net, '--user', '70:70', '--read-only',
        '--tmpfs', '/tmp', '--tmpfs', '/var/run/postgresql:uid=70,gid=70', '--tmpfs', '/var/lib/postgresql/data:uid=70,gid=70,mode=0700',
        '--env-file', envfile('db.env', {'POSTGRES_USER': 'postgres', 'POSTGRES_PASSWORD': secrets.token_hex(24), 'DAKAFARM_DB_PASSWORD': app_password}),
        '-v', f'{root}/deploy/postgres-init.sh:/docker-entrypoint-initdb.d/10-app.sh:ro',
        'postgres:15-alpine@sha256:54e0dd8e8cddcdbb9156c2486eed5a43eccb7214d7c6828097d41ce049fb3984')
    for _ in range(60):
        r = subprocess.run(['docker','exec',db,'pg_isready','-U','postgres'],capture_output=True)
        if r.returncode == 0: break
        time.sleep(1)
    else: raise RuntimeError('PostgreSQL indisponible')
    boot_env = envfile('bootstrap.env', {**env,'BOOTSTRAP_ADMIN_EMAIL':email,'BOOTSTRAP_ADMIN_PASSWORD':admin_password})
    run('run','--rm','--network',net,'--read-only','--tmpfs','/tmp','--env-file',boot_env,
        'dakafarm-api:data','alembic','upgrade','2ac63eddf7a8')
    seed = """
import asyncio
from sqlalchemy import text
from app.core.database import engine
async def main():
    async with engine.begin() as db:
        category=(await db.execute(text("INSERT INTO product_categories(name,is_active) VALUES ('MIGRATION_LEGACY',true) RETURNING id"))).scalar()
        await db.execute(text("INSERT INTO products(category_id,name,unit_of_measure,current_stock,unit_price) VALUES (:id,'MIGRATION_LEGACY','kg',12.345,123.45)"),{'id':category})
    await engine.dispose()
asyncio.run(main())
"""
    run('run','--rm','--network',net,'--read-only','--tmpfs','/tmp','--env-file',boot_env,
        'dakafarm-api:data','python','-c',seed)
    for _ in range(2):
        run('run','--rm','--network',net,'--read-only','--tmpfs','/tmp','--env-file',boot_env,
            'dakafarm-api:data','python','-m','app.bootstrap')
    run('run','-d','--name',api,'--network',net,'--network-alias','dakafarm-api','--read-only','--tmpfs','/tmp',
        '--env-file',envfile('api.env',env),'dakafarm-api:data')
    if '--browser' in sys.argv:
        run('run','-d','--name',web,'--network',net,'--read-only','--tmpfs','/tmp',
            '-p','127.0.0.1::8080','dakafarm-web:data')
        address=run('port',web,'8080/tcp').strip()
        browser_env={**os.environ,'TEST_ADMIN_EMAIL':email,'TEST_ADMIN_PASSWORD':admin_password,
                     'TEST_WEB_URL':'http://'+address}
        subprocess.run(['node',str(root/'deploy/check-data-browser.cjs')],env=browser_env,check=True)
    test_env = envfile('tests.env', {**env, 'TEST_ADMIN_EMAIL':email, 'TEST_ADMIN_PASSWORD':admin_password,
                                    'TEST_API_URL':f'http://{api}:8000'})
    print(run('run','--rm','--network',net,'--read-only','--tmpfs','/tmp','--env-file',test_env,
              '-v',f'{root}/backend/tests:/tests:ro','dakafarm-api:data',
              'python','-m','unittest','discover','-s','/tests','-v').strip())
    if '--browser' in sys.argv:
        subprocess.run(['node',str(root/'deploy/check-coexistence-browser.cjs')],env=browser_env,check=True)

finally:
    for name in [web,api,db]: subprocess.run(['docker','rm','-f','-v',name],capture_output=True)
    subprocess.run(['docker','network','rm',net],capture_output=True)
    # Ne conserver aucun identifiant de la fixture après les contrôles.
    shutil.rmtree(private)
