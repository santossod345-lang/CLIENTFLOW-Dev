#!/usr/bin/env python
"""Complete diagnostic of ClientFlow system"""
import sys, os
sys.path.insert(0, '.')

# Load .env
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, val = line.partition('=')
                os.environ.setdefault(key.strip(), val.strip())

print("=" * 70)
print("DIAGNOSTICO COMPLETO - ClientFlow")
print("=" * 70)

errors = []

# ====== TEST 1: Imports ======
print("\n[1] Importando app FastAPI...")
try:
    from backend.main import app
    print("  OK: App importado")
except Exception as e:
    print(f"  ERRO: {e}")
    errors.append(f"Import app: {e}")

# ====== TEST 2: Routes ======
print("\n[2] Rotas registradas:")
try:
    routes = []
    for route in app.routes:
        methods = getattr(route, 'methods', None)
        path = getattr(route, 'path', None)
        if path and methods:
            routes.append((sorted(methods), path))
    routes.sort(key=lambda x: x[1])
    for methods, path in routes:
        print(f"  {','.join(methods):20s} {path}")
    print(f"  Total: {len(routes)} rotas")
except Exception as e:
    print(f"  ERRO: {e}")
    errors.append(f"Routes: {e}")

# ====== TEST 3: Database ======
print("\n[3] Banco de dados:")
try:
    from backend.database import engine, SessionLocal, SQLALCHEMY_DATABASE_URL
    print(f"  URL: {SQLALCHEMY_DATABASE_URL}")
    from backend import models
    from sqlalchemy import inspect
    
    # Ensure tables exist
    models.Base.metadata.create_all(bind=engine)
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"  Tabelas: {tables}")
    
    # Check data
    db = SessionLocal()
    emp_count = db.query(models.Empresa).count()
    cl_count = db.query(models.Cliente).count()
    at_count = db.query(models.Atendimento).count()
    rt_count = db.query(models.RefreshToken).count()
    print(f"  Empresas: {emp_count}")
    print(f"  Clientes: {cl_count}")
    print(f"  Atendimentos: {at_count}")
    print(f"  RefreshTokens: {rt_count}")
    
    if emp_count > 0:
        emps = db.query(models.Empresa).all()
        for emp in emps:
            print(f"    -> id={emp.id}, email={emp.email_login}, nome={emp.nome_empresa}, plano={emp.plano_empresa}")
    
    db.close()
except Exception as e:
    import traceback
    traceback.print_exc()
    errors.append(f"Database: {e}")

# ====== TEST 4: Auth ======
print("\n[4] Autenticacao JWT:")
try:
    from backend import auth
    print(f"  SECRET_KEY (20 chars): {auth.SECRET_KEY[:20]}...")
    print(f"  SECRET_KEY length: {len(auth.SECRET_KEY)}")
    print(f"  ALGORITHM: {auth.ALGORITHM}")
    print(f"  TOKEN_EXPIRE: {auth.ACCESS_TOKEN_EXPIRE_MINUTES} min")
    print(f"  REFRESH_EXPIRE: {auth.REFRESH_TOKEN_EXPIRE_DAYS} days")
    
    # Create and decode token
    token = auth.create_access_token({"sub": 1})
    print(f"  Token criado: {token[:60]}...")
    
    payload = auth.decode_access_token(token)
    print(f"  Token decodificado: sub={payload.get('sub')}, exp={payload.get('exp')}")
    
    # Test password
    hashed = auth.get_password_hash("Test1234")
    verified = auth.verify_password("Test1234", hashed)
    print(f"  Password hash/verify: {'OK' if verified else 'FALHOU'}")
    
    # Test with DB
    db = SessionLocal()
    emp_count = db.query(models.Empresa).count()
    if emp_count > 0:
        emp = db.query(models.Empresa).first()
        try:
            result = auth.get_current_empresa_jwt(token, db)
            print(f"  Auth lookup empresa ID=1: {result.nome_empresa}")
        except Exception as e:
            print(f"  Auth lookup empresa ID=1: ERRO - {e}")
            # Try with correct empresa id
            token2 = auth.create_access_token({"sub": emp.id})
            try:
                result = auth.get_current_empresa_jwt(token2, db)
                print(f"  Auth lookup empresa ID={emp.id}: {result.nome_empresa}")
            except Exception as e2:
                print(f"  Auth lookup empresa ID={emp.id}: ERRO - {e2}")
                errors.append(f"Auth lookup: {e2}")
    db.close()
except Exception as e:
    import traceback
    traceback.print_exc()
    errors.append(f"Auth: {e}")

# ====== TEST 5: CORS ======
print("\n[5] CORS:")
try:
    from backend.main import allowed_origins, _vercel_regex
    print(f"  Allowed origins: {allowed_origins}")
    print(f"  Vercel regex: {_vercel_regex}")
    print(f"  Middleware count: {len(app.user_middleware)}")
    for mw in app.user_middleware:
        cls_name = mw.cls.__name__ if hasattr(mw, 'cls') else str(mw)
        print(f"    -> {cls_name}: {mw.kwargs if hasattr(mw, 'kwargs') else ''}")
except Exception as e:
    print(f"  ERRO: {e}")
    errors.append(f"CORS: {e}")

# ====== TEST 6: Environment ======
print("\n[6] Variaveis de ambiente:")
env_vars = [
    'JWT_SECRET_KEY', 'SECRET_KEY', 'JWT_ALGORITHM',
    'ACCESS_TOKEN_EXPIRE_MINUTES', 'DATABASE_URL',
    'ENVIRONMENT', 'ALLOWED_ORIGINS', 'CORS_ALLOW_CREDENTIALS',
    'REDIS_URL', 'VITE_API_URL', 'AUTO_CREATE_TABLES',
    'RUN_MIGRATIONS_ON_STARTUP'
]
for var in env_vars:
    val = os.getenv(var)
    if val and ('KEY' in var or 'SECRET' in var or 'PASSWORD' in var):
        print(f"  {var} = {val[:10]}... (set)")
    elif val:
        print(f"  {var} = {val}")
    else:
        print(f"  {var} = (not set)")

# ====== TEST 7: Frontend config ======
print("\n[7] Frontend config:")
frontend_files = {
    'vite.config.js': 'clientflow-frontend/vite.config.js',
    '.env.production': 'clientflow-frontend/.env.production',
    '.env': 'clientflow-frontend/.env',
    '.env.local': 'clientflow-frontend/.env.local',
    '.env.development': 'clientflow-frontend/.env.development',
}
for name, path in frontend_files.items():
    full_path = os.path.join(os.path.dirname(__file__), path)
    if os.path.exists(full_path):
        with open(full_path, encoding='utf-8') as f:
            content = f.read().strip()
        print(f"  {name}: EXISTS")
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('//'):
                print(f"    {line}")
    else:
        print(f"  {name}: NOT FOUND")

# ====== TEST 8: Simulate full login ======
print("\n[8] Simulando fluxo completo de login:")
try:
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    # Health check
    r = client.get("/api/health")
    print(f"  GET /api/health: {r.status_code} -> {r.json()}")
    
    # Try register
    register_data = {
        "nome_empresa": "Diagnostico Test",
        "nicho": "Teste",
        "telefone": "(11) 99999-9999",
        "email_login": "diag@test.com",
        "senha": "Teste1234"
    }
    r = client.post("/api/empresas/cadastrar", json=register_data)
    print(f"  POST /api/empresas/cadastrar: {r.status_code}")
    if r.status_code == 201:
        print(f"    Empresa criada: {r.json().get('id')}")
    elif r.status_code == 400:
        print(f"    Ja existe: {r.json().get('detail')}")
    else:
        print(f"    Resposta: {r.json()}")
        errors.append(f"Register failed: {r.status_code} {r.text}")
    
    # Try login
    login_data = {
        "email_login": "diag@test.com",
        "senha": "Teste1234"
    }
    r = client.post("/api/empresas/login", json=login_data)
    print(f"  POST /api/empresas/login: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        access_token = data.get('access_token')
        refresh_token = data.get('refresh_token')
        print(f"    access_token: {access_token[:50] if access_token else 'MISSING'}...")
        print(f"    refresh_token: {refresh_token[:50] if refresh_token else 'MISSING'}...")
        
        # Test authenticated endpoints
        headers = {"Authorization": f"Bearer {access_token}"}
        
        r = client.get("/api/empresas/me", headers=headers)
        print(f"  GET /api/empresas/me: {r.status_code} -> {r.json() if r.status_code == 200 else r.text}")
        
        r = client.get("/api/dashboard", headers=headers)
        print(f"  GET /api/dashboard: {r.status_code}")
        if r.status_code == 200:
            print(f"    Data: {r.json()}")
        else:
            print(f"    ERRO: {r.text}")
            errors.append(f"Dashboard: {r.status_code} {r.text}")
        
        r = client.get("/api/dashboard/analytics?period=30d", headers=headers)
        print(f"  GET /api/dashboard/analytics: {r.status_code}")
        if r.status_code == 200:
            print(f"    Metrics OK")
        else:
            print(f"    ERRO: {r.text}")
            errors.append(f"Analytics: {r.status_code} {r.text}")
        
        r = client.get("/api/clientes", headers=headers)
        print(f"  GET /api/clientes: {r.status_code} -> {len(r.json()) if r.status_code == 200 else r.text} clientes")
        
        r = client.get("/api/atendimentos", headers=headers)
        print(f"  GET /api/atendimentos: {r.status_code} -> {len(r.json()) if r.status_code == 200 else r.text} atendimentos")
        
        # Test refresh
        r = client.post("/api/empresas/refresh", json={"refresh_token": refresh_token})
        print(f"  POST /api/empresas/refresh: {r.status_code}")
        if r.status_code == 200:
            print(f"    New tokens received OK")
        else:
            print(f"    ERRO: {r.text}")
            errors.append(f"Refresh: {r.status_code} {r.text}")
    else:
        print(f"    ERRO: {r.json()}")
        errors.append(f"Login failed: {r.status_code} {r.text}")

except Exception as e:
    import traceback
    traceback.print_exc()
    errors.append(f"TestClient: {e}")

# ====== TEST 9: Check frontend code for issues ======
print("\n[9] Analise do frontend:")

# Check api.js
api_js = os.path.join(os.path.dirname(__file__), 'clientflow-frontend/src/services/api.js')
with open(api_js, encoding='utf-8') as f:
    content = f.read()
print(f"  api.js baseURL strategy:")
if "VITE_API_URL" in content:
    print(f"    Uses VITE_API_URL env var")
if "'/api'" in content:
    print(f"    Fallback to '/api'")

# Check AuthContext
auth_ctx = os.path.join(os.path.dirname(__file__), 'clientflow-frontend/src/context/AuthContext.jsx')
with open(auth_ctx, encoding='utf-8') as f:
    content = f.read()
if 'isLoading' in content:
    print(f"  AuthContext has isLoading: YES")
else:
    print(f"  AuthContext has isLoading: NO (BUG!)")

# Check PrivateRoute
pr = os.path.join(os.path.dirname(__file__), 'clientflow-frontend/src/routes/PrivateRoute.jsx')
with open(pr, encoding='utf-8') as f:
    content = f.read()
if 'isLoading' in content:
    print(f"  PrivateRoute checks isLoading: YES")
else:
    print(f"  PrivateRoute checks isLoading: NO (MAY REDIRECT TO LOGIN PREMATURELY)")

if 'Outlet' in content:
    print(f"  PrivateRoute uses Outlet: YES")
else:
    print(f"  PrivateRoute uses Outlet: NO (BUG - nested routes won't render)")

# Check App.jsx routing
app_jsx = os.path.join(os.path.dirname(__file__), 'clientflow-frontend/src/App.jsx')
with open(app_jsx, encoding='utf-8') as f:
    content = f.read()
if 'HashRouter' in content:
    print(f"  Router: HashRouter")
elif 'BrowserRouter' in content:
    print(f"  Router: BrowserRouter")
if 'PrivateRoute' in content:
    print(f"  Uses PrivateRoute: YES")
if 'DashboardLayout' in content:
    print(f"  Uses DashboardLayout: YES")

# Check Painel.jsx
painel = os.path.join(os.path.dirname(__file__), 'clientflow-frontend/src/pages/Painel.jsx')
with open(painel, encoding='utf-8') as f:
    content = f.read()
if "from '../services/api'" in content or "from \"../services/api\"" in content:
    print(f"  Painel.jsx uses api service: YES")
else:
    print(f"  Painel.jsx uses api service: NO (BUG!)")
if 'axios' in content and "from 'axios'" in content:
    print(f"  Painel.jsx imports raw axios: YES (BUG!)")
else:
    print(f"  Painel.jsx imports raw axios: NO (OK)")

# ====== TEST 10: Check package.json dependencies ======
print("\n[10] Dependencias frontend:")
pkg = os.path.join(os.path.dirname(__file__), 'clientflow-frontend/package.json')
with open(pkg, encoding='utf-8') as f:
    import json
    pkg_data = json.load(f)
deps = {**pkg_data.get('dependencies', {}), **pkg_data.get('devDependencies', {})}
key_deps = ['react', 'react-dom', 'react-router-dom', 'axios', 'chart.js', 'react-chartjs-2', 'vite']
for dep in key_deps:
    ver = deps.get(dep, 'NOT INSTALLED')
    print(f"  {dep}: {ver}")

# Check if node_modules exists
nm = os.path.join(os.path.dirname(__file__), 'clientflow-frontend/node_modules')
print(f"\n  node_modules exists: {os.path.exists(nm)}")
if not os.path.exists(nm):
    errors.append("node_modules not found - run 'npm install' in clientflow-frontend/")

# Check if dist exists (built frontend)
dist = os.path.join(os.path.dirname(__file__), 'clientflow-frontend/dist')
print(f"  dist/ (build output) exists: {os.path.exists(dist)}")

# ====== SUMMARY ======
print("\n" + "=" * 70)
if errors:
    print(f"ERROS ENCONTRADOS ({len(errors)}):")
    for i, e in enumerate(errors, 1):
        print(f"  {i}. {e}")
else:
    print("NENHUM ERRO ENCONTRADO NO BACKEND")
print("=" * 70)
