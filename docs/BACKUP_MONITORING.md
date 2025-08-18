# 🔒 Backup e Monitoramento - PMCELL

## 💾 Sistema de Backup

### 1. Backup Automático (Railway)

**PostgreSQL Backup**:
- ✅ Backup automático diário
- ✅ Point-in-time recovery até 7 dias
- ✅ Snapshots automáticos
- ✅ Recuperação via Railway Dashboard

**Acessar Backups**:
1. Railway Dashboard → Seu Projeto
2. Database → PostgreSQL
3. Backups → Ver snapshots disponíveis
4. Restore → Selecionar ponto no tempo

---

### 2. Backup Manual

#### Script de Backup Completo
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups"
BACKUP_FILE="pmcell_backup_$DATE.json"

# Criar diretório se não existir
mkdir -p $BACKUP_DIR

# Backup completo dos dados
echo "🔄 Iniciando backup..."
python manage.py dumpdata > $BACKUP_DIR/$BACKUP_FILE

# Backup apenas do catálogo (sem users/sessions)
python manage.py dumpdata catalog > $BACKUP_DIR/catalog_$DATE.json

# Compactar
gzip $BACKUP_DIR/catalog_$DATE.json

echo "✅ Backup concluído: $BACKUP_FILE"
echo "📁 Localização: $BACKUP_DIR/"

# Manter apenas últimos 7 backups
ls -t $BACKUP_DIR/pmcell_backup_*.json | tail -n +8 | xargs -r rm
```

#### Tornar Executável
```bash
chmod +x backup.sh
```

#### Backup por Categoria
```bash
# Apenas produtos
python manage.py dumpdata catalog.ProdutoNormal catalog.ProdutoCapaPelicula > produtos_backup.json

# Apenas configurações
python manage.py dumpdata catalog.ConfiguracaoWebhook catalog.ConfiguracaoGeral > config_backup.json

# Apenas pedidos
python manage.py dumpdata catalog.Pedido catalog.ItemPedido > pedidos_backup.json
```

---

### 3. Backup para Cloud Storage

#### AWS S3
```python
# backup_to_s3.py
import boto3
import os
from datetime import datetime

def backup_to_s3():
    s3 = boto3.client('s3', 
        aws_access_key_id='YOUR_ACCESS_KEY',
        aws_secret_access_key='YOUR_SECRET_KEY'
    )
    
    date = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Upload backup
    s3.upload_file(
        f'backups/pmcell_backup_{date}.json',
        'pmcell-backups',
        f'daily/backup_{date}.json'
    )
    
    print(f"✅ Backup enviado para S3: backup_{date}.json")

if __name__ == "__main__":
    backup_to_s3()
```

#### Google Drive
```python
# backup_to_drive.py
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import pickle

def backup_to_drive(file_path):
    service = build('drive', 'v3', credentials=creds)
    
    file_metadata = {
        'name': f'pmcell_backup_{datetime.now().strftime("%Y%m%d")}.json',
        'parents': ['FOLDER_ID']  # ID da pasta no Drive
    }
    
    media = MediaFileUpload(file_path, mimetype='application/json')
    
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    
    print(f"✅ Backup enviado para Google Drive: {file.get('id')}")
```

---

### 4. Restauração de Backup

#### Restauração Completa
```bash
# Restaurar backup completo
python manage.py loaddata backups/pmcell_backup_20250817.json
```

#### Restauração Seletiva
```bash
# Restaurar apenas produtos
python manage.py loaddata produtos_backup.json

# Restaurar apenas configurações
python manage.py loaddata config_backup.json
```

#### Restauração com Limpeza
```bash
# CUIDADO: Remove dados existentes
python manage.py flush --noinput
python manage.py loaddata backups/pmcell_backup_20250817.json
```

---

## 📊 Sistema de Monitoramento

### 1. Health Check Endpoint

#### Implementação (já incluída)
```python
# catalog/views.py
def health_check(request):
    try:
        # Testar banco de dados
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Testar cache
        from django.core.cache import cache
        cache.set('health_test', 'ok', 60)
        cache_status = cache.get('health_test')
        
        # Verificar produtos ativos
        produtos_count = ProdutoNormal.objects.filter(em_estoque=True).count()
        
        return JsonResponse({
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'database': 'connected',
            'cache': 'working' if cache_status == 'ok' else 'error',
            'produtos_ativos': produtos_count,
            'version': '1.0'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=500)
```

#### Teste do Health Check
```bash
curl https://catalogo.pmcell.com/health/
```

---

### 2. Uptime Monitoring

#### UptimeRobot (Gratuito)
1. Criar conta em uptimerobot.com
2. Add New Monitor:
   - **Type**: HTTP(s)
   - **URL**: `https://catalogo.pmcell.com/health/`
   - **Interval**: 5 minutos
   - **Alert Contacts**: Email, SMS, Slack

#### Configuração de Alertas
```
Monitor Name: PMCELL Catalog
URL: https://catalogo.pmcell.com/health/
Keyword: "healthy"
Alert When: Keyword not found OR HTTP error
```

#### StatusCake (Alternativa)
```
Test Name: PMCELL Health
Website URL: https://catalogo.pmcell.com/health/
Check Rate: 5 minutes
Test Type: HTTP
Expected Status Code: 200
```

---

### 3. Logs e Debugging

#### Railway Logs
```bash
# Ver logs em tempo real
railway logs --follow

# Ver logs históricos
railway logs --tail 100

# Filtrar por level
railway logs --level error
```

#### Django Logging
```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'catalog.webhook_utils': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

---

### 4. Métricas de Performance

#### Comando de Status
```python
# management/commands/system_status.py
from django.core.management.base import BaseCommand
from catalog.models import *
from django.core.cache import cache

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Contadores
        produtos_total = ProdutoNormal.objects.count()
        produtos_ativo = ProdutoNormal.objects.filter(em_estoque=True).count()
        pedidos_total = Pedido.objects.count()
        pedidos_hoje = Pedido.objects.filter(criado_em__date=timezone.now().date()).count()
        
        # Cache status
        cache_keys = len(cache._cache.keys()) if hasattr(cache._cache, 'keys') else 'N/A'
        
        self.stdout.write("📊 PMCELL System Status")
        self.stdout.write(f"Produtos: {produtos_ativo}/{produtos_total} ativos")
        self.stdout.write(f"Pedidos: {pedidos_hoje} hoje / {pedidos_total} total")
        self.stdout.write(f"Cache: {cache_keys} chaves ativas")
```

```bash
# Executar
python manage.py system_status
```

---

### 5. Monitoramento de Webhooks

#### Log de Webhooks
```python
# webhook_monitor.py
import json
from datetime import datetime, timedelta
from catalog.models import ConfiguracaoWebhook

def webhook_status_report():
    """Gerar relatório de status dos webhooks"""
    webhooks = ConfiguracaoWebhook.objects.all()
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'webhooks': []
    }
    
    for webhook in webhooks:
        status = {
            'evento': webhook.evento,
            'url': webhook.url,
            'ativo': webhook.ativo,
            'timeout': webhook.timeout,
            'retry_ativo': webhook.retry_ativo,
            'last_updated': webhook.updated_at.isoformat()
        }
        report['webhooks'].append(status)
    
    return report

# Uso
report = webhook_status_report()
print(json.dumps(report, indent=2))
```

---

### 6. Alertas Automáticos

#### Script de Monitoramento
```python
# monitor.py
import requests
import smtplib
from email.mime.text import MIMEText

def check_site_health():
    try:
        response = requests.get('https://catalogo.pmcell.com/health/', timeout=10)
        data = response.json()
        
        if response.status_code != 200 or data.get('status') != 'healthy':
            send_alert(f"❌ Site unhealthy: {data}")
            return False
        
        print("✅ Site healthy")
        return True
        
    except Exception as e:
        send_alert(f"🚨 Site monitoring error: {str(e)}")
        return False

def send_alert(message):
    # Email alert
    msg = MIMEText(message)
    msg['Subject'] = 'PMCELL Alert'
    msg['From'] = 'monitoring@pmcell.com'
    msg['To'] = 'admin@pmcell.com'
    
    # Configurar SMTP
    # server = smtplib.SMTP('smtp.gmail.com', 587)
    # server.send_message(msg)
    
    print(f"🚨 ALERT: {message}")

if __name__ == "__main__":
    check_site_health()
```

#### Cron Job para Monitoramento
```bash
# Adicionar ao crontab
# crontab -e

# Verificar a cada 5 minutos
*/5 * * * * /usr/bin/python3 /path/to/monitor.py

# Backup diário às 3h
0 3 * * * /path/to/backup.sh

# Relatório semanal domingo às 9h
0 9 * * 0 /usr/bin/python3 /path/to/weekly_report.py
```

---

### 7. Dashboard de Monitoramento

#### Métricas Simples
```python
# dashboard_metrics.py
def get_dashboard_metrics():
    return {
        'produtos': {
            'total': ProdutoNormal.objects.count(),
            'ativos': ProdutoNormal.objects.filter(em_estoque=True).count(),
            'inativos': ProdutoNormal.objects.filter(em_estoque=False).count()
        },
        'pedidos': {
            'hoje': Pedido.objects.filter(criado_em__date=timezone.now().date()).count(),
            'semana': Pedido.objects.filter(criado_em__gte=timezone.now() - timedelta(days=7)).count(),
            'mes': Pedido.objects.filter(criado_em__gte=timezone.now() - timedelta(days=30)).count()
        },
        'carrinhos_abandonados': {
            'hoje': CarrinhoAbandonado.objects.filter(created_at__date=timezone.now().date()).count(),
            'pendentes': CarrinhoAbandonado.objects.filter(webhook_enviado=False).count()
        },
        'jornadas': {
            'liberacoes_hoje': JornadaCliente.objects.filter(
                evento='liberacao_preco',
                timestamp__date=timezone.now().date()
            ).count()
        }
    }
```

---

### 8. Checklist de Monitoramento

#### Diário
- [ ] Verificar health check
- [ ] Revisar logs de erro
- [ ] Conferir pedidos do dia
- [ ] Verificar webhooks funcionando

#### Semanal  
- [ ] Backup manual de segurança
- [ ] Revisar carrinhos abandonados
- [ ] Análise de métricas de conversão
- [ ] Verificar espaço em disco

#### Mensal
- [ ] Review completo de logs
- [ ] Análise de performance
- [ ] Update de dependências
- [ ] Teste de disaster recovery

---

## 🚨 Plano de Disaster Recovery

### Cenários de Falha

**1. Banco de Dados Corrompido**:
- Restaurar último backup Railway
- Se necessário, usar backup manual
- Tempo estimado: 5-15 minutos

**2. Aplicação não responde**:
- Restart via Railway Dashboard
- Verificar logs para root cause
- Redeploy se necessário

**3. Domínio/DNS indisponível**:
- Usar URL Railway temporária
- Corrigir configuração DNS
- Comunicar stakeholders

**4. Perda total do projeto Railway**:
- Deploy fresh do código GitHub
- Restaurar backup mais recente
- Reconfigurar variáveis de ambiente
- Tempo estimado: 30-60 minutos

### Contatos de Emergência
```
Admin Principal: admin@pmcell.com
Railway Support: help@railway.app
DNS Provider: [seu provedor]
Cloudinary: support@cloudinary.com
```

---

**🔒 Sistema monitorado e protegido!**