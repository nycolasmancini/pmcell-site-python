# 🚀 Deploy PMCELL - Desenvolvimento Direto no Servidor

## 📋 Pré-requisitos

1. **Conta Railway**: [railway.app](https://railway.app)
2. **Conta Vercel**: [vercel.com](https://vercel.com)
3. **Conta GitHub**: Para repositório do código

## 🎯 Estratégia de Deploy

### Backend → Railway (Django + PostgreSQL)
### Frontend → Vercel (Next.js)

---

## 🔧 Passo 1: Preparar Repositório Git

```bash
# Inicializar Git
cd /Users/nycolasmancini/Desktop/ecommerce-pmcell
git init
git add .
git commit -m "🎉 Initial commit - PMCELL Catálogo structure"

# Conectar ao GitHub (criar repositório primeiro)
git remote add origin https://github.com/SEU-USUARIO/pmcell-catalogo.git
git branch -M main
git push -u origin main
```

---

## 🚂 Passo 2: Deploy Backend no Railway

### 1. Criar Projeto Railway
- Acesse [railway.app](https://railway.app)
- Clique em "New Project"
- Selecione "Deploy from GitHub repo"
- Escolha seu repositório

### 2. Configurar Variáveis de Ambiente
No painel Railway, adicione estas variáveis:

```env
# Django Settings
DEBUG=False
SECRET_KEY=seu-secret-key-super-seguro-aqui
DJANGO_SETTINGS_MODULE=config.settings_prod

# CORS (será atualizado após deploy do frontend)
CORS_ALLOWED_ORIGINS=https://seu-frontend.vercel.app

# WhatsApp API (opcional no início)
WHATSAPP_API_URL=sua-url-whatsapp-api
WHATSAPP_API_TOKEN=seu-token-whatsapp
```

### 3. Adicionar PostgreSQL
- No Railway, clique em "Add Service"
- Selecione "Database" → "PostgreSQL"
- Railway criará automaticamente a variável `DATABASE_URL`

### 4. Configurar Deploy
- Diretório root: `/backend`
- Build command: `pip install -r requirements.txt`
- Start command: `python manage.py migrate && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`

---

## ▲ Passo 3: Deploy Frontend no Vercel

### 1. Conectar Repositório
- Acesse [vercel.com](https://vercel.com)
- Clique em "New Project"
- Import do GitHub
- Selecione seu repositório

### 2. Configurar Build
- Framework Preset: **Next.js**
- Root Directory: `/frontend`
- Build Command: `npm run build`
- Output Directory: `.next`

### 3. Configurar Variáveis de Ambiente
```env
NEXT_PUBLIC_API_URL=https://seu-backend-railway.railway.app/api
NEXT_PUBLIC_APP_NAME=PMCELL Catálogo
NEXT_PUBLIC_COMPANY_NAME=PMCELL
NODE_ENV=production
```

---

## 🔄 Passo 4: Conectar Backend e Frontend

### 1. Atualizar CORS no Railway
Após deploy do Vercel, atualize no Railway:
```env
CORS_ALLOWED_ORIGINS=https://seu-frontend.vercel.app,https://www.seu-dominio.com
```

### 2. Testar Conexão
- Backend: `https://seu-backend.railway.app/admin/`
- Frontend: `https://seu-frontend.vercel.app`
- API: `https://seu-backend.railway.app/api/`

---

## 🛠️ Desenvolvimento Direto no Servidor

### Fluxo de Trabalho
1. **Desenvolver localmente** (opcional para teste rápido)
2. **Commit & Push** para GitHub
3. **Deploy automático** Railway + Vercel
4. **Testar no servidor**
5. **Iterar rapidamente**

### Comandos Úteis
```bash
# Deploy rápido
git add .
git commit -m "feat: nova funcionalidade"
git push

# Logs Railway (via CLI)
railway login
railway logs

# Logs Vercel (via CLI)
npx vercel login
npx vercel logs
```

---

## 🗄️ Configuração do Banco de Dados

### 1. Migrar no Railway
```bash
# Conexão via Railway CLI
railway login
railway shell

# Ou usar Railway dashboard → service → shell
python manage.py migrate
python manage.py createsuperuser
```

### 2. Dados Iniciais
```python
# Criar via Django Admin ou shell
python manage.py shell

# Exemplo: criar categorias básicas
from produtos.models import Categoria
Categoria.objects.create(nome="Acessórios", ativa=True)
Categoria.objects.create(nome="Capas", ativa=True)
Categoria.objects.create(nome="Películas", ativa=True)
```

---

## 📊 Monitoramento

### Railway (Backend)
- **Logs**: Railway Dashboard → Logs
- **Métricas**: CPU, RAM, Network
- **Database**: Connections, Queries

### Vercel (Frontend)
- **Analytics**: Vercel Dashboard → Analytics
- **Performance**: Core Web Vitals
- **Functions**: Edge functions metrics

---

## 🔒 Segurança Produção

### 1. Secrets Management
- **Never commit** secrets to Git
- Use Railway/Vercel environment variables
- Rotate keys periodically

### 2. Domain Security
```env
# Railway
ALLOWED_HOSTS=seu-dominio.com,*.railway.app

# SSL/HTTPS enforcement
SECURE_SSL_REDIRECT=True
```

### 3. Database Backup
- Railway PostgreSQL backup automático
- Configure backup retention
- Test restore procedures

---

## 🚀 URLs Finais

Após deploy, você terá:

- **Backend API**: `https://pmcell-backend-xyz.railway.app/api/`
- **Django Admin**: `https://pmcell-backend-xyz.railway.app/admin/`
- **Frontend**: `https://pmcell-frontend.vercel.app/`
- **PostgreSQL**: Managed by Railway

---

## 🔧 Comandos de Deploy Rápido

```bash
# 1. Fazer alterações
# 2. Commit e push
git add .
git commit -m "🎯 nova feature: sistema de carrinho"
git push

# 3. Verificar deploy
echo "✅ Backend: Railway deploy automático"
echo "✅ Frontend: Vercel deploy automático"
echo "🌐 Acessar: https://seu-frontend.vercel.app"
```

---

## 🆘 Troubleshooting

### Erro de CORS
```python
# settings_prod.py
CORS_ALLOWED_ORIGINS = [
    "https://seu-frontend.vercel.app",
    "https://preview-branch.vercel.app",  # Para previews
]
```

### Erro de Static Files
```bash
# Railway shell
python manage.py collectstatic --noinput
```

### Erro de Database
```bash
# Railway shell
python manage.py migrate
python manage.py showmigrations
```

---

**🎯 Pronto para desenvolver direto no servidor!**

Com essa configuração, você edita o código localmente, faz push para Git, e em ~2 minutos está rodando em produção. Zero problemas de "funcionava local" 🚀