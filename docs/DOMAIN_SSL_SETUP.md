# 🌐 Configuração de Domínio e SSL - PMCELL

## 🚀 Deploy para Produção

### 1. Railway Deploy

**Configuração Automática**:
1. Conecte o repositório GitHub ao Railway
2. Railway detectará automaticamente o projeto Django
3. Configure as variáveis de ambiente

**Variáveis de Ambiente Obrigatórias**:
```env
SECRET_KEY=sua-secret-key-super-segura-aqui
DEBUG=False
DATABASE_URL=postgresql://user:pass@hostname:port/database
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name
ALLOWED_HOSTS=.railway.app,seudominio.com
```

**Opcional**:
```env
# Para domínio customizado
DOMAIN_NAME=catalogo.pmcell.com

# Para analytics
GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
```

---

### 2. Configuração de Domínio Customizado

#### No Railway
1. Acesse projeto no Railway Dashboard
2. Vá em **Settings** → **Domains**
3. Clique em **Custom Domain**
4. Adicione seu domínio: `catalogo.pmcell.com`

#### No seu Provedor de DNS
Configure os registros DNS:

**Opção A - CNAME (Subdomínio)**:
```
Tipo: CNAME
Nome: catalogo
Valor: seu-projeto.railway.app
TTL: 300
```

**Opção B - A Record (Domínio raiz)**:
```
Tipo: A
Nome: @
Valor: [IP fornecido pelo Railway]
TTL: 300
```

**Para www (opcional)**:
```
Tipo: CNAME  
Nome: www
Valor: catalogo.pmcell.com
TTL: 300
```

#### Verificação
```bash
# Verificar propagação DNS
nslookup catalogo.pmcell.com

# Testar conectividade
curl -I https://catalogo.pmcell.com
```

---

### 3. SSL/HTTPS Automático

**Railway SSL**:
- ✅ SSL automático para domínios .railway.app
- ✅ SSL automático para domínios customizados
- ✅ Renovação automática
- ✅ Redirecionamento HTTP → HTTPS

**Verificação SSL**:
```bash
# Verificar certificado
openssl s_client -connect catalogo.pmcell.com:443 -servername catalogo.pmcell.com

# Testar redirecionamento  
curl -I http://catalogo.pmcell.com
# Deve retornar 301/302 para https://
```

---

### 4. Configuração Django para Produção

#### settings.py Otimizado

```python
# SECURITY
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 ano
SECURE_HSTS_INCLUDE_SUBDOMAINS = True  
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# COOKIES
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# ALLOWED HOSTS
ALLOWED_HOSTS = [
    '.railway.app',
    'catalogo.pmcell.com',
    'www.catalogo.pmcell.com'
]

# TRUSTED ORIGINS
CSRF_TRUSTED_ORIGINS = [
    'https://catalogo.pmcell.com',
    'https://www.catalogo.pmcell.com'
]
```

#### Headers de Segurança Customizados

Já implementado em `catalog/middleware.py`:
```python
response['X-Content-Type-Options'] = 'nosniff'
response['X-Frame-Options'] = 'DENY'  
response['X-XSS-Protection'] = '1; mode=block'
response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
```

---

### 5. Performance e CDN

#### Cloudinary Otimizações
```python
# settings.py
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'seu-cloud-name',
    'API_KEY': 'sua-api-key', 
    'API_SECRET': 'seu-api-secret',
    'SECURE': True,  # HTTPS
    'QUALITY': 'auto',  # Otimização automática
    'FORMAT': 'auto',   # Formato automático
    'PROGRESSIVE': True  # JPEG progressivo
}
```

#### Compressão de Assets
```bash
# Coletar e comprimir static files
python manage.py collectstatic --noinput
python manage.py compress --force
```

#### Cache Headers
```python
# URLs com cache para static files
urlpatterns = [
    # ...
    path('static/', static, {'cache_control': 'max-age=31536000'}),
]
```

---

### 6. Monitoramento e Logs

#### Railway Logs
```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Ver logs em tempo real
railway logs --follow
```

#### Health Check Endpoint
Adicionar em `catalog/urls.py`:
```python
path('health/', views.health_check, name='health_check'),
```

Em `catalog/views.py`:
```python
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    try:
        # Testar conexão com banco
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'connected'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy', 
            'error': str(e)
        }, status=500)
```

#### Uptime Monitoring
Serviços recomendados:
- **UptimeRobot** (gratuito)
- **Pingdom**
- **StatusCake**

Configurar:
- URL: `https://catalogo.pmcell.com/health/`
- Intervalo: 5 minutos
- Alertas: Email/SMS/Slack

---

### 7. SEO e Meta Tags

#### Configuração Completa
Já implementado em `templates/base.html`:

```html
<!-- Canonical URL -->
<link rel="canonical" href="https://catalogo.pmcell.com{{ request.path }}">

<!-- Open Graph -->
<meta property="og:site_name" content="PMCELL">
<meta property="og:url" content="https://catalogo.pmcell.com{{ request.path }}">

<!-- Schema.org -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "PMCELL",
  "url": "https://catalogo.pmcell.com"
}
</script>
```

#### Sitemap Dinâmico
Já configurado em `catalog/urls.py`:
```python
path('sitemap.xml', views.sitemap, name='sitemap'),
```

#### robots.txt
```
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/

Sitemap: https://catalogo.pmcell.com/sitemap.xml
```

---

### 8. Google Analytics (Opcional)

#### Configuração
1. Criar propriedade GA4
2. Obter código de rastreamento (G-XXXXXXXXXX)
3. Adicionar em variáveis de ambiente: `GOOGLE_ANALYTICS_ID`

#### Template
Adicionar em `templates/base.html`:
```html
{% if GOOGLE_ANALYTICS_ID %}
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id={{ GOOGLE_ANALYTICS_ID }}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', '{{ GOOGLE_ANALYTICS_ID }}');
</script>
{% endif %}
```

---

### 9. Backup e Disaster Recovery

#### Backup Automático (Railway)
- ✅ Backup automático do banco PostgreSQL
- ✅ Point-in-time recovery
- ✅ Retenção de 7 dias (plano gratuito)

#### Backup Manual
```bash
# Backup completo
python manage.py dumpdata > backup_$(date +%Y%m%d).json

# Backup apenas catalog
python manage.py dumpdata catalog > catalog_backup.json

# Upload para cloud storage (S3, Google Drive, etc)
```

#### Restauração
```bash
# Restaurar backup completo
python manage.py loaddata backup_20250817.json

# Restaurar apenas catalog
python manage.py loaddata catalog_backup.json
```

---

### 10. Checklist de Go-Live

#### Pré-Deploy
- [ ] Testar em ambiente de staging
- [ ] Verificar todas as URLs de webhook
- [ ] Confirmar dados de teste vs produção
- [ ] Backup do estado atual

#### DNS e SSL
- [ ] Domínio apontando corretamente
- [ ] SSL funcionando (https://)
- [ ] Redirecionamento HTTP → HTTPS
- [ ] Certificado válido e não expirado

#### Funcionalidades
- [ ] Liberação de preços funcionando
- [ ] Carrinho e checkout completos
- [ ] Webhooks ativos e testados
- [ ] Admin acessível
- [ ] Rate limiting ativo

#### Performance
- [ ] Tempo de carregamento < 3s
- [ ] Imagens otimizadas (Cloudinary)
- [ ] Cache funcionando
- [ ] Compressão ativa

#### SEO
- [ ] Meta tags completas
- [ ] Sitemap acessível (/sitemap.xml)
- [ ] robots.txt configurado
- [ ] Google Analytics (se configurado)

#### Monitoramento
- [ ] Health check endpoint ativo
- [ ] Uptime monitoring configurado
- [ ] Logs sendo capturados
- [ ] Alertas configurados

#### Segurança
- [ ] HTTPS enforçado
- [ ] Headers de segurança ativos
- [ ] Rate limiting testado
- [ ] Admin com senhas fortes

---

## 🎯 URLs Finais

**Produção**:
- Site: `https://catalogo.pmcell.com`
- Admin: `https://catalogo.pmcell.com/admin/`
- API: `https://catalogo.pmcell.com/api/`
- Health: `https://catalogo.pmcell.com/health/`
- Sitemap: `https://catalogo.pmcell.com/sitemap.xml`

**Webhooks para n8n/Zapier**:
- Liberação: `https://catalogo.pmcell.com/api/liberate-prices/`
- Abandono: `https://catalogo.pmcell.com/api/track-abandoned-cart/`
- Pedido: `(configurar URL de destino no admin)`

---

**🚀 Sistema pronto para produção!**