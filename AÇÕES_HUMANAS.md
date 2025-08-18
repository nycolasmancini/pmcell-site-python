# 🚨 AÇÕES QUE VOCÊ PRECISA FAZER

Preparei tudo automaticamente. Agora você precisa fazer apenas 3 ações:

---

## 📋 PASSO 1: Criar Repositório GitHub (5 min)

### 1.1 Acessar GitHub
- Vá em [github.com](https://github.com)
- Clique em "New repository" (botão verde)

### 1.2 Configurar Repositório
- **Nome**: `pmcell-catalogo`
- **Descrição**: `Catálogo online PMCELL - Acessórios para celular`
- **Público** ou **Privado** (sua escolha)
- ❌ **NÃO** marque "Add a README file"
- ❌ **NÃO** marque "Add .gitignore"
- ❌ **NÃO** marque "Choose a license"

### 1.3 Conectar Repositório Local
```bash
# Copie a URL do seu repositório criado e execute:
cd /Users/nycolasmancini/Desktop/ecommerce-pmcell
git remote add origin https://github.com/SEU-USUARIO/pmcell-catalogo.git
git branch -M main
git push -u origin main
```

**✅ PRONTO:** Seu código estará no GitHub!

---

## 🚂 PASSO 2: Deploy Backend no Railway (10 min)

### 2.1 Criar Conta Railway
- Acesse [railway.app](https://railway.app)
- Clique "Login" → "Login with GitHub"
- Autorize a conexão

### 2.2 Criar Projeto
- Clique "New Project"
- Selecione "Deploy from GitHub repo"
- Selecione `pmcell-catalogo`
- ✅ Railway detectará automaticamente o Django

### 2.3 Configurar Backend Service
- Clique no service criado
- Vá em "Settings"
- **Root Directory**: `/backend`
- **Build Command**: (deixe vazio - usará nixpacks.toml)
- **Start Command**: (deixe vazio - usará nixpacks.toml)

### 2.4 Adicionar PostgreSQL
- No dashboard do projeto, clique "Add Service"
- Selecione "Database"
- Clique "PostgreSQL"
- ✅ Railway criará automaticamente e conectará

### 2.5 Configurar Variáveis
- Clique no backend service → "Variables"
- Adicione estas variáveis:

```
DEBUG=False
SECRET_KEY=pmcell-secret-key-production-2024-muito-seguro
DJANGO_SETTINGS_MODULE=config.settings_prod
CORS_ALLOWED_ORIGINS=https://pmcell-catalogo.vercel.app
```

### 2.6 Deploy!
- Clique "Deploy"
- Aguarde 3-5 minutos
- ✅ Anote a URL: `https://seu-projeto.railway.app`

---

## ▲ PASSO 3: Deploy Frontend no Vercel (5 min)

### 3.1 Criar Conta Vercel
- Acesse [vercel.com](https://vercel.com)
- Clique "Login" → "Continue with GitHub"
- Autorize a conexão

### 3.2 Criar Projeto
- Clique "New Project"
- Encontre `pmcell-catalogo` na lista
- Clique "Import"

### 3.3 Configurar Build
- **Framework Preset**: Next.js (auto-detectado)
- **Root Directory**: `frontend`
- **Build Command**: `npm run build` (auto)
- **Output Directory**: `.next` (auto)
- **Install Command**: `npm install` (auto)

### 3.4 Configurar Variáveis
Adicione estas variáveis de ambiente:

```
NEXT_PUBLIC_API_URL=https://SEU-BACKEND.railway.app/api
NEXT_PUBLIC_APP_NAME=PMCELL Catálogo
NEXT_PUBLIC_COMPANY_NAME=PMCELL
NODE_ENV=production
```

⚠️ **Substitua** `SEU-BACKEND.railway.app` pela URL real do seu Railway!

### 3.5 Deploy!
- Clique "Deploy"
- Aguarde 2-3 minutos
- ✅ Anote a URL: `https://pmcell-catalogo.vercel.app`

---

## 🔗 PASSO 4: Conectar Backend ↔ Frontend (2 min)

### 4.1 Atualizar CORS no Railway
- Vá no Railway → Seu projeto → Backend service
- Clique "Variables"
- Edite `CORS_ALLOWED_ORIGINS`:

```
CORS_ALLOWED_ORIGINS=https://pmcell-catalogo.vercel.app,https://SEU-DOMINIO-VERCEL.vercel.app
```

### 4.2 Testar URLs
- **Frontend**: Sua URL Vercel
- **Backend API**: Sua URL Railway + `/api/`
- **Django Admin**: Sua URL Railway + `/admin/`
- **Health Check**: Sua URL Railway + `/health/`

---

## 🛠️ PASSO 5: Configurar Database (5 min)

### 5.1 Criar Superusuário
No Railway → Seu projeto → Backend service:
- Clique nos 3 pontinhos → "Shell"
- Execute:
```bash
python manage.py createsuperuser
```
- Digite username, email e senha

### 5.2 Acessar Django Admin
- Vá em: `https://seu-backend.railway.app/admin/`
- Login com o superusuário criado
- ✅ Você verá o painel administrativo!

---

## 🎯 RESULTADO FINAL

Após completar todos os passos:

- 🎨 **Frontend**: `https://pmcell-catalogo.vercel.app`
- 🔧 **API**: `https://seu-backend.railway.app/api/`
- ⚙️ **Admin**: `https://seu-backend.railway.app/admin/`
- 🗄️ **Database**: PostgreSQL no Railway

---

## 🚀 DESENVOLVIMENTO CONTÍNUO

A partir de agora:

1. **Edite código localmente**
2. **Commit & Push**:
   ```bash
   git add .
   git commit -m "nova funcionalidade"
   git push
   ```
3. **Deploy automático** em ~2 minutos
4. **Testar no servidor**

---

## 🆘 PROBLEMAS?

### Script de Deploy Rápido
```bash
cd /Users/nycolasmancini/Desktop/ecommerce-pmcell
./deploy.sh
```

### URLs para Testar
- Health check: `https://seu-backend.railway.app/health/`
- API root: `https://seu-backend.railway.app/api/`
- Admin: `https://seu-backend.railway.app/admin/`

### Comandos Úteis
```bash
# Ver logs Railway
railway login
railway logs

# Ver logs Vercel  
npx vercel logs
```

---

**🎯 Total: ~25 minutos e você terá o PMCELL 100% rodando na nuvem!**

Qualquer dúvida, me avise! 🚀