# Documentação de Webhooks - PMCELL Catálogo

## Visão Geral

O sistema envia webhooks para URLs configuráveis no painel admin em 3 momentos chave da jornada do cliente. Todos os webhooks são enviados via POST com payload JSON e têm retry automático em caso de falha.

## Eventos de Webhook

### 1. PREÇO LIBERADO
**Trigger**: Quando o cliente fornece WhatsApp para liberar os preços  
**URL Config**: Admin → Configurações → Webhook Preço Liberado

#### Payload
```json
{
  "evento": "preco_liberado",
  "timestamp": "2024-03-15T10:30:00Z",
  "dados": {
    "whatsapp": "(11) 98765-4321",
    "session_id": "abc123def456",
    "ip": "192.168.1.1",
    "user_agent": "Mozilla/5.0...",
    "origem": {
      "pagina": "/catalogo",
      "categoria_atual": "cabos",
      "produto_visualizando": null
    }
  }
}
```

#### Implementação
```python
# views.py
import requests
from django.utils import timezone
import json

def enviar_webhook_preco_liberado(whatsapp, session_id, request):
    config = ConfiguracaoWebhook.objects.get(evento='preco_liberado')
    
    if not config.ativo or not config.url:
        return
    
    payload = {
        "evento": "preco_liberado",
        "timestamp": timezone.now().isoformat(),
        "dados": {
            "whatsapp": whatsapp,
            "session_id": session_id,
            "ip": get_client_ip(request),
            "user_agent": request.META.get('HTTP_USER_AGENT', ''),
            "origem": {
                "pagina": request.path,
                "categoria_atual": request.GET.get('categoria'),
                "produto_visualizando": request.GET.get('produto_id')
            }
        }
    }
    
    try:
        response = requests.post(
            config.url,
            json=payload,
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )
        config.ultima_execucao = timezone.now()
        config.ultimo_status = f"OK: {response.status_code}"
        config.save()
    except Exception as e:
        # Retry uma vez após 5 segundos
        import time
        time.sleep(5)
        try:
            response = requests.post(config.url, json=payload, timeout=10)
            config.ultimo_status = f"OK após retry: {response.status_code}"
        except:
            config.ultimo_status = f"Erro: {str(e)}"
        config.ultima_execucao = timezone.now()
        config.save()
```

---

### 2. CARRINHO ABANDONADO
**Trigger**: 30 minutos após última atividade com items no carrinho  
**URL Config**: Admin → Configurações → Webhook Carrinho Abandonado

#### Payload
```json
{
  "evento": "carrinho_abandonado",
  "timestamp": "2024-03-15T11:00:00Z",
  "dados": {
    "whatsapp": "(11) 98765-4321",
    "session_id": "abc123def456",
    "tempo_inativo_minutos": 30,
    "carrinho": {
      "valor_total": 245.80,
      "quantidade_items": 3,
      "items": [
        {
          "produto_id": 15,
          "produto_nome": "Cabo USB-C 2m",
          "categoria": "cabos",
          "quantidade": 10,
          "preco_unitario": 12.50,
          "subtotal": 125.00,
          "tipo_preco": "atacado"
        },
        {
          "produto_id": 23,
          "produto_nome": "Capa Silicone",
          "categoria": "capas",
          "modelo": "Samsung Galaxy S23",
          "quantidade": 20,
          "preco_unitario": 6.04,
          "subtotal": 120.80,
          "tipo_preco": "super_atacado"
        }
      ]
    },
    "jornada": {
      "tempo_no_site_minutos": 45,
      "categorias_visitadas": ["cabos", "capas", "fones"],
      "categorias_nao_visitadas": ["peliculas", "powerbanks"],
      "quantidade_pesquisas": 3,
      "ultimas_pesquisas": ["cabo tipo c", "capa samsung", "fone bluetooth"],
      "produtos_visualizados": [
        {"id": 15, "nome": "Cabo USB-C 2m", "tempo_visualizacao": 120},
        {"id": 23, "nome": "Capa Silicone", "tempo_visualizacao": 85}
      ]
    }
  }
}
```

#### Implementação com Celery
```python
# tasks.py
from celery import shared_task
from datetime import datetime, timedelta

@shared_task
def verificar_carrinhos_abandonados():
    """Executar a cada 5 minutos via Celery Beat"""
    
    tempo_abandono = ConfiguracaoGeral.objects.get(
        chave='tempo_carrinho_abandonado'
    ).get_value()  # 30 minutos
    
    limite = timezone.now() - timedelta(minutes=tempo_abandono)
    
    # Buscar sessões com carrinho não vazio e inativas
    sessoes_inativas = JornadaCliente.objects.filter(
        finalizado_em__isnull=True,
        atualizado_em__lt=limite,
        carrinho_atual__isnull=False
    ).exclude(
        carrinho_abandonado__isnull=False  # Não reenviar
    )
    
    for jornada in sessoes_inativas:
        criar_carrinho_abandonado(jornada)
        enviar_webhook_carrinho_abandonado(jornada)

def enviar_webhook_carrinho_abandonado(jornada):
    config = ConfiguracaoWebhook.objects.get(evento='carrinho_abandonado')
    
    if not config.ativo or not config.url:
        return
    
    # Montar payload com dados da jornada
    carrinho = json.loads(jornada.carrinho_atual)
    
    payload = {
        "evento": "carrinho_abandonado",
        "timestamp": timezone.now().isoformat(),
        "dados": {
            "whatsapp": jornada.whatsapp,
            "session_id": jornada.session_id,
            "tempo_inativo_minutos": 30,
            "carrinho": processar_carrinho(carrinho),
            "jornada": processar_jornada(jornada)
        }
    }
    
    enviar_com_retry(config, payload)
```

---

### 3. PEDIDO FINALIZADO
**Trigger**: Quando o cliente confirma o pedido  
**URL Config**: Admin → Configurações → Webhook Pedido Finalizado

#### Payload
```json
{
  "evento": "pedido_finalizado",
  "timestamp": "2024-03-15T11:30:00Z",
  "dados": {
    "pedido": {
      "codigo": "PMC-2024-0042",
      "nome_cliente": "João Silva",
      "whatsapp_inicial": "(11) 98765-4321",
      "whatsapp_confirmado": "(11) 98765-4321",
      "valor_total": 245.80,
      "quantidade_items": 2,
      "items": [
        {
          "produto_id": 15,
          "produto_nome": "Cabo USB-C 2m",
          "categoria": "cabos",
          "quantidade": 10,
          "preco_unitario": 12.50,
          "subtotal": 125.00,
          "tipo_preco": "atacado"
        },
        {
          "produto_id": 23,
          "produto_nome": "Capa Silicone",
          "categoria": "capas",
          "modelo": "Samsung Galaxy S23",
          "quantidade": 20,
          "preco_unitario": 6.04,
          "subtotal": 120.80,
          "tipo_preco": "super_atacado"
        }
      ]
    },
    "jornada_completa": {
      "session_id": "abc123def456",
      "tempo_total_minutos": 52,
      "horario_entrada": "2024-03-15T10:38:00Z",
      "horario_saida": "2024-03-15T11:30:00Z",
      "categorias_visitadas": ["cabos", "capas", "fones"],
      "categorias_nao_visitadas": ["peliculas", "powerbanks"],
      "produtos_visualizados_total": 8,
      "produtos_adicionados_carrinho": 3,
      "produtos_removidos_carrinho": 1,
      "pesquisas_realizadas": [
        {"termo": "cabo tipo c", "timestamp": "2024-03-15T10:42:00Z", "resultados": 5},
        {"termo": "capa samsung", "timestamp": "2024-03-15T10:55:00Z", "resultados": 12},
        {"termo": "fone bluetooth", "timestamp": "2024-03-15T11:10:00Z", "resultados": 8}
      ],
      "eventos_timeline": [
        {"tipo": "entrada_site", "timestamp": "2024-03-15T10:38:00Z"},
        {"tipo": "liberou_precos", "timestamp": "2024-03-15T10:39:00Z"},
        {"tipo": "visitou_categoria", "categoria": "cabos", "timestamp": "2024-03-15T10:40:00Z"},
        {"tipo": "pesquisou", "termo": "cabo tipo c", "timestamp": "2024-03-15T10:42:00Z"},
        {"tipo": "visualizou_produto", "produto": "Cabo USB-C 2m", "timestamp": "2024-03-15T10:43:00Z"},
        {"tipo": "adicionou_carrinho", "produto": "Cabo USB-C 2m", "quantidade": 10, "timestamp": "2024-03-15T10:45:00Z"},
        {"tipo": "finalizou_pedido", "timestamp": "2024-03-15T11:30:00Z"}
      ],
      "dispositivo": {
        "tipo": "mobile",
        "user_agent": "Mozilla/5.0...",
        "resolucao": "390x844"
      }
    },
    "metricas": {
      "taxa_conversao": true,
      "tempo_ate_primeira_adicao": 7,
      "tempo_ate_finalizacao": 52,
      "alteracoes_carrinho": 4,
      "valor_medio_item": 122.90
    }
  }
}
```

#### Implementação
```python
# views.py
def finalizar_pedido(request):
    # ... lógica de criação do pedido ...
    
    pedido = Pedido.objects.create(
        whatsapp_inicial=request.session.get('whatsapp'),
        whatsapp_confirmado=request.POST.get('whatsapp_confirmacao'),
        nome_cliente=request.POST.get('nome', ''),
        valor_total=calcular_total(carrinho)
    )
    
    # Criar items do pedido
    for item in carrinho['items']:
        ItemPedido.objects.create(
            pedido=pedido,
            produto_id=item['produto_id'],
            modelo_id=item.get('modelo_id'),
            quantidade=item['quantidade'],
            preco_unitario=item['preco'],
            subtotal=item['subtotal']
        )
    
    # Atualizar jornada
    jornada = JornadaCliente.objects.get(
        session_id=request.session.session_key
    )
    jornada.finalizado_em = timezone.now()
    jornada.save()
    
    # Associar jornada ao pedido
    pedido.jornada = jornada
    pedido.save()
    
    # Enviar webhook
    enviar_webhook_pedido_finalizado(pedido, jornada)
    
    return JsonResponse({
        'success': True,
        'codigo_pedido': pedido.codigo
    })

def enviar_webhook_pedido_finalizado(pedido, jornada):
    config = ConfiguracaoWebhook.objects.get(evento='pedido_finalizado')
    
    if not config.ativo or not config.url:
        return
    
    # Preparar dados completos da jornada
    eventos = json.loads(jornada.eventos)
    tempo_total = (jornada.finalizado_em - jornada.iniciado_em).seconds // 60
    
    # Calcular métricas
    primeira_adicao = next(
        (e for e in eventos if e['tipo'] == 'adicionou_carrinho'), 
        None
    )
    tempo_primeira_adicao = None
    if primeira_adicao:
        tempo_primeira_adicao = (
            datetime.fromisoformat(primeira_adicao['timestamp']) - 
            jornada.iniciado_em
        ).seconds // 60
    
    payload = {
        "evento": "pedido_finalizado",
        "timestamp": timezone.now().isoformat(),
        "dados": {
            "pedido": serializar_pedido(pedido),
            "jornada_completa": serializar_jornada(jornada),
            "metricas": {
                "taxa_conversao": True,
                "tempo_ate_primeira_adicao": tempo_primeira_adicao,
                "tempo_ate_finalizacao": tempo_total,
                "alteracoes_carrinho": contar_alteracoes(eventos),
                "valor_medio_item": pedido.valor_total / pedido.items.count()
            }
        }
    }
    
    enviar_com_retry(config, payload)
```

---

## Função Auxiliar de Envio com Retry

```python
# utils/webhooks.py
import requests
import time
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

def enviar_com_retry(config, payload, max_retries=1):
    """
    Envia webhook com retry automático
    """
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'PMCELL-Catalog/1.0'
    }
    
    for tentativa in range(max_retries + 1):
        try:
            response = requests.post(
                config.url,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            # Sucesso
            if response.status_code < 400:
                config.ultima_execucao = timezone.now()
                config.ultimo_status = f"OK: {response.status_code}"
                config.save()
                
                logger.info(f"Webhook {config.evento} enviado com sucesso")
                return True
            
            # Erro do cliente (4xx) - não fazer retry
            elif 400 <= response.status_code < 500:
                config.ultima_execucao = timezone.now()
                config.ultimo_status = f"Erro cliente: {response.status_code}"
                config.save()
                
                logger.error(f"Webhook {config.evento} erro cliente: {response.status_code}")
                return False
            
            # Erro do servidor (5xx) - fazer retry
            else:
                if tentativa < max_retries:
                    time.sleep(5 * (tentativa + 1))  # Backoff exponencial
                    continue
                else:
                    config.ultimo_status = f"Erro servidor: {response.status_code}"
                    
        except requests.exceptions.Timeout:
            if tentativa < max_retries:
                time.sleep(5 * (tentativa + 1))
                continue
            else:
                config.ultimo_status = "Erro: Timeout"
                
        except requests.exceptions.RequestException as e:
            if tentativa < max_retries:
                time.sleep(5 * (tentativa + 1))
                continue
            else:
                config.ultimo_status = f"Erro: {str(e)}"
        
        except Exception as e:
            config.ultimo_status = f"Erro inesperado: {str(e)}"
            logger.exception(f"Erro inesperado no webhook {config.evento}")
            break
    
    # Se chegou aqui, todas as tentativas falharam
    config.ultima_execucao = timezone.now()
    config.save()
    
    logger.error(f"Webhook {config.evento} falhou após {max_retries + 1} tentativas")
    return False
```

---

## Tracking de Eventos para Jornada

```python
# middleware.py
from django.utils.deprecation import MiddlewareMixin
import json

class JornadaClienteMiddleware(MiddlewareMixin):
    """
    Middleware para tracking automático da jornada
    """
    
    def process_request(self, request):
        if not request.session.session_key:
            request.session.create()
        
        # Criar ou recuperar jornada
        jornada, created = JornadaCliente.objects.get_or_create(
            session_id=request.session.session_key,
            defaults={'whatsapp': ''}
        )
        
        request.jornada = jornada
        
        # Registrar evento de página
        if request.path.startswith('/catalogo'):
            self.registrar_evento(jornada, {
                'tipo': 'visualizou_pagina',
                'pagina': request.path,
                'timestamp': timezone.now().isoformat()
            })
    
    def process_response(self, request, response):
        if hasattr(request, 'jornada'):
            # Atualizar tempo no site
            tempo_decorrido = timezone.now() - request.jornada.iniciado_em
            request.jornada.tempo_no_site = tempo_decorrido
            request.jornada.save()
        
        return response
    
    def registrar_evento(self, jornada, evento):
        eventos = json.loads(jornada.eventos) if jornada.eventos else []
        eventos.append(evento)
        jornada.eventos = json.dumps(eventos)
        jornada.save()
```

---

## Configuração no n8n

### Workflow Exemplo para n8n

1. **Webhook Node** (Trigger)
   - URL: https://seu-n8n.com/webhook/pmcell-catalogo
   - Method: POST
   - Response: Immediately

2. **Switch Node** (Router)
   - Route baseado em `{{ $json.evento }}`
   - Cases: preco_liberado, carrinho_abandonado, pedido_finalizado

3. **Branch: Preço Liberado**
   - WhatsApp Business API: Enviar mensagem de boas-vindas
   - CRM: Criar/atualizar lead
   - Google Sheets: Registrar nova liberação

4. **Branch: Carrinho Abandonado**
   - Wait: 2 horas
   - WhatsApp: Enviar lembrete com link
   - Se valor > R$ 500: Notificar vendedor

5. **Branch: Pedido Finalizado**
   - WhatsApp: Confirmar pedido
   - Email: Enviar para financeiro
   - ERP: Criar pedido
   - Google Sheets: Atualizar relatório

### Exemplo de Configuração WhatsApp Business
```javascript
// Node Function n8n
const whatsapp = $input.first().json.dados.whatsapp;
const codigo = $input.first().json.dados.pedido.codigo;
const valor = $input.first().json.dados.pedido.valor_total;

const mensagem = `🎉 *Pedido Confirmado!*

Código: ${codigo}
Valor Total: R$ ${valor}

Em breve entraremos em contato para finalizar o pagamento e entrega.

Obrigado por comprar com PMCELL!`;

return {
  to: whatsapp.replace(/\D/g, '') + '@c.us',
  body: mensagem
};
```

---

## Logs e Monitoramento

### Django Logging Config
```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'webhooks.log',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'webhooks': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### Verificação de Status no Admin
```python
# admin.py
@admin.register(ConfiguracaoWebhook)
class ConfiguracaoWebhookAdmin(admin.ModelAdmin):
    list_display = ['evento', 'ativo', 'ultima_execucao', 'status_badge']
    readonly_fields = ['ultima_execucao', 'ultimo_status']
    
    def status_badge(self, obj):
        if not obj.ultimo_status:
            return format_html('<span style="color: gray;">Nunca executado</span>')
        elif 'OK' in obj.ultimo_status:
            return format_html('<span style="color: green;">✓ {}</span>', obj.ultimo_status)
        else:
            return format_html('<span style="color: red;">✗ {}</span>', obj.ultimo_status)
    
    status_badge.short_description = 'Status'
```

---

## Testes de Webhook

### Comando para Teste Manual
```python
# management/commands/test_webhook.py
from django.core.management.base import BaseCommand
from catalog.utils.webhooks import enviar_com_retry
import json

class Command(BaseCommand):
    help = 'Testa envio de webhook'
    
    def add_arguments(self, parser):
        parser.add_argument('evento', choices=['preco_liberado', 'carrinho_abandonado', 'pedido_finalizado'])
    
    def handle(self, *args, **options):
        evento = options['evento']
        
        # Payload de teste
        payload_teste = {
            "evento": evento,
            "timestamp": timezone.now().isoformat(),
            "dados": {
                "teste": True,
                "mensagem": "Este é um webhook de teste"
            }
        }
        
        config = ConfiguracaoWebhook.objects.get(evento=evento)
        
        if enviar_com_retry(config, payload_teste):
            self.stdout.write(self.style.SUCCESS(f'Webhook {evento} enviado com sucesso!'))
        else:
            self.stdout.write(self.style.ERROR(f'Falha ao enviar webhook {evento}'))
```

### Uso
```bash
python manage.py test_webhook preco_liberado
python manage.py test_webhook carrinho_abandonado
python manage.py test_webhook pedido_finalizado
```