"""Recette locale sur base jetable ; aucune donnée du cluster, aucun secret affiché."""
from pathlib import Path
import json, os, secrets, shutil, subprocess, tempfile, time

root = Path(__file__).resolve().parents[1]
private = Path(tempfile.mkdtemp(prefix='dakafarm-fixture-', dir='/tmp'))
os.chmod(private, 0o700)
net, db, api = 'dakafarm-fixture-net', 'dakafarm-fixture-db', 'dakafarm-fixture-api'
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
        raise RuntimeError('Échec du contrôle Docker ; diagnostic privé')
    return r.stdout

try:
    run('network', 'create', '--internal', net)
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
    for _ in range(2):
        run('run','--rm','--network',net,'--read-only','--tmpfs','/tmp','--env-file',boot_env,
            'dakafarm-api:qualification','python','-m','app.bootstrap')
    run('run','-d','--name',api,'--network',net,'--read-only','--tmpfs','/tmp',
        '--env-file',envfile('api.env',env),'dakafarm-api:qualification')
    script = r'''
import json,sys,time,urllib.request,urllib.parse,urllib.error,asyncio
from sqlalchemy import text
from app.core.database import engine
c=json.load(sys.stdin)
def req(path,data=None,token=None,method=None):
    print('Contrôle '+path, flush=True)
    headers={'Content-Type':'application/json'}
    if token: headers['Authorization']='Bearer '+token
    if path=='/login':
        data=urllib.parse.urlencode(data).encode();headers['Content-Type']='application/x-www-form-urlencoded'
    elif data is not None: data=json.dumps(data).encode()
    with urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8000'+path,data=data,headers=headers,method=method),timeout=10) as r:
        body=r.read();return r.status,json.loads(body) if body and not path=='/healthz' else body
for _ in range(30):
    try:
        assert req('/healthz')[0]==200;break
    except Exception: time.sleep(1)
else: raise RuntimeError('API indisponible')
try: req('/api/v1/user/me')
except urllib.error.HTTPError as e: assert e.code in (401,403)
else: raise AssertionError('Accès anonyme autorisé')
token=req('/login',{'username':c['email'],'password':c['password']})[1]['access_token']
me=req('/api/v1/user/me',token=token)[1];assert me['role_name']=='admin'
for path in ['/api/v1/farm/houses/','/api/v1/farm/flocks/','/api/v1/inventory/products/','/api/v1/finance/accounts/']:
    assert req(path,token=token)[0]==200
house=req('/api/v1/farm/houses/',{'name':'Recette jetable','capacity':100},token)[1]
assert req('/api/v1/farm/houses/'+str(house['id']),token=token,method='DELETE')[0]==204
async def verify_db():
    async with engine.connect() as db:
        assert (await db.execute(text('SELECT COUNT(*) FROM users'))).scalar()==1
        flags=(await db.execute(text('SELECT rolsuper,rolcreatedb,rolcreaterole FROM pg_roles WHERE rolname=current_user'))).one()
        assert not any(flags)
    await engine.dispose()
asyncio.run(verify_db())
print('Migrations, bootstrap répété sans réinitialisation, connexion admin, accès anonyme refusé, listes métier, CRUD bâtiment et privilèges PostgreSQL vérifiés.')
'''
    print(run('exec','-i',api,'python','-c',script,input=json.dumps({'email':email,'password':admin_password})).strip())
finally:
    for name in [api,db]: subprocess.run(['docker','rm','-f','-v',name],capture_output=True)
    subprocess.run(['docker','network','rm',net],capture_output=True)
    # Ne conserver aucun identifiant de la fixture après les contrôles.
    shutil.rmtree(private)
