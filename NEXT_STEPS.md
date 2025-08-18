# 🚀 PRÓXIMOS PASSOS - Deploy PMCELL

## ✅ PRONTO PARA DEPLOY!

Seu projeto está **100% configurado** para desenvolvimento direto no servidor. Siga os passos abaixo:

---

## 📋 Passo 1: Criar Repositório GitHub

1. Acesse [github.com](https://github.com) e crie um novo repositório
2. Nome sugerido: `pmcell-catalogo`
3. **NÃO** inicialize com README (já temos)
4. Copie a URL do repositório

```bash
# Conectar ao GitHub (substitua pela sua URL)
git remote add origin https://github.com/SEU-USUARIO/pmcell-catalogo.git
git branch -M main
git push -u origin main
```

---

## 🚂 Passo 2: Deploy Backend (Railway)

### 1. Criar Conta Railway
- Acesse [railway.app](https://railway.app)
- Faça login com GitHub

### 2. Novo Projeto
- Clique "New Project"
- "Deploy from GitHub repo"
- Selecione `pmcell-catalogo`

### 3. Configurar Backend Service
- **Root Directory**: `/backend`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python manage.py migrate && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`

### 4. Adicionar PostgreSQL
- No projeto Railway, clique "Add Service"
- Selecione "Database" → "PostgreSQL"
- ✅ Railway criará automaticamente `DATABASE_URL`

### 5. Configurar Variáveis de Ambiente
```env
DEBUG=False
SECRET_KEY=pmcell-secret-key-production-2024-secure
DJANGO_SETTINGS_MODULE=config.settings_prod
```

### 6. Deploy!
- Clique "Deploy"
- Aguarde ~3-5 minutos
- ✅ Backend estará em: `https://seu-projeto.railway.app`

---

## ▲ Passo 3: Deploy Frontend (Vercel)

### 1. Criar Conta Vercel
- Acesse [vercel.com](https://vercel.com)
- Faça login com GitHub

### 2. Novo Projeto
- Clique "New Project"
- Import `pmcell-catalogo`

### 3. Configurar Build
- **Framework**: Next.js (auto-detectado)
- **Root Directory**: `/frontend`
- **Build Command**: `npm run build` (auto)
- **Output Directory**: `.next` (auto)

### 4. Configurar Variáveis de Ambiente
```env
NEXT_PUBLIC_API_URL=https://SEU-BACKEND.railway.app/api
NEXT_PUBLIC_APP_NAME=PMCELL Catálogo
NEXT_PUBLIC_COMPANY_NAME=PMCELL
NODE_ENV=production
```

### 5. Deploy!
- Clique "Deploy"
- Aguarde ~2-3 minutos
- ✅ Frontend estará em: `https://seu-projeto.vercel.app`

---

## 🔄 Passo 4: Conectar Backend ↔ Frontend

### 1. Atualizar CORS no Railway
Vá em Railway → Variáveis de Ambiente → Adicione:
```env
CORS_ALLOWED_ORIGINS=https://seu-frontend.vercel.app
```

### 2. Testar Conexão
- **API**: `https://seu-backend.railway.app/api/`
- **Admin**: `https://seu-backend.railway.app/admin/`
- **Frontend**: `https://seu-frontend.vercel.app`

---

## 🛠️ Passo 5: Configurar Database

### 1. Criar Superusuário
No Railway → Backend Service → Shell:
```bash
python manage.py createsuperuser
```

### 2. Acessar Django Admin
- URL: `https://seu-backend.railway.app/admin/`
- Login com superusuário criado

### 3. Criar Dados Iniciais
```python
# Via Django Admin ou Shell
# Categorias
- Acessórios
- Capas 
- Películas

# Fabricantes
- PMCELL
- Samsung
- Apple
- Xiaomi

# Marcas de Celular
- Samsung
- Apple
- Xiaomi
- Motorola
```

---

## 🎯 Desenvolvimento Workflow

### Agora você pode desenvolver direto no servidor:

1. **Fazer alterações localmente**
2. **Commit & Push**:
   ```bash
   git add .
   git commit -m "feat: nova funcionalidade"
   git push
   ```
3. **Deploy automático** em ~2 minutos
4. **Testar no servidor**
5. **Iterar rapidamente**

---

## 📊 URLs Finais

Após deploy completo:

- 🎨 **Frontend**: `https://pmcell-catalogo.vercel.app`
- 🔧 **Backend API**: `https://pmcell-backend.railway.app/api/`
- ⚙️ **Django Admin**: `https://pmcell-backend.railway.app/admin/`
- 🗄️ **PostgreSQL**: Gerenciado pelo Railway

---

## 🚀 Próximas Funcionalidades

Com a infraestrutura pronta, você pode implementar:

### 1. API REST (1-2 dias)
- Serializers DRF
- ViewSets para CRUD
- Endpoints de busca
- Sistema de autenticação

### 2. Frontend (2-3 dias)
- Cards de produtos
- Modal WhatsApp
- Sistema de busca
- Carrinho de compras

### 3. Integrações (1-2 dias)
- Webhook WhatsApp
- Analytics em tempo real
- Notificações

---

## 🆘 Suporte Deploy

### Comandos Úteis
```bash
# Ver logs Railway
railway login
railway logs

# Ver logs Vercel
npx vercel logs

# Deploy rápido
git add . && git commit -m "update" && git push
```

### Troubleshooting
- **CORS Error**: Verificar `CORS_ALLOWED_ORIGINS`
- **Database Error**: Verificar `DATABASE_URL`
- **Static Files**: Rodar `collectstatic`

---

## ✅ CHECKLIST DEPLOY

- [ ] Repositório GitHub criado
- [ ] Railway backend deployed
- [ ] PostgreSQL adicionado
- [ ] Vercel frontend deployed
- [ ] CORS configurado
- [ ] Superusuário criado
- [ ] URLs testadas
- [ ] Primeira alteração e deploy

---

**🎯 Tudo pronto! Em ~30 minutos você terá o PMCELL rodando 100% na nuvem!**

Zero problemas de "funcionava no meu local" - direto no servidor desde o primeiro dia! 🚀