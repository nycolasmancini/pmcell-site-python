# 📡 Documentação de APIs e Webhooks - PMCELL

## 🔗 APIs Disponíveis

### 1. Liberação de Preços
**Endpoint**: `POST /api/liberate-prices/`

Libera os preços do catálogo para um WhatsApp específico.

**Headers**:
```
Content-Type: application/json
X-CSRFToken: [token]
```

**Body**:
```json
{
  "whatsapp": "(11) 99999-9999",
  "timestamp": "2025-08-17T20:00:00Z" // opcional
}
```

**Response Sucesso (200)**:
```json
{
  "success": true
}
```

**Response Erro (400)**:
```json
{
  "error": "WhatsApp inválido"
}
```

**Rate Limit**: 5 requisições por minuto por IP

---

### 2. Adicionar ao Carrinho
**Endpoint**: `POST /api/add-to-cart/`

Adiciona um produto ao carrinho do cliente.

**Headers**:
```
Content-Type: application/json
X-CSRFToken: [token]
Cookie: user_whatsapp=(11) 99999-9999
```

**Body para Produtos Normais**:
```json
{
  "product_id": 1,
  "product_type": "normal",
  "quantity": 10
}
```

**Body para Capas/Películas**:
```json
{
  "product_id": 1,
  "product_type": "modelo", 
  "model_id": 3,
  "quantity": 5
}
```

**Response (200)**:
```json
{
  "success": true
}
```

---

### 3. Obter Itens do Carrinho
**Endpoint**: `POST /api/get-cart-items/`

Retorna os dados dos produtos no carrinho com preços calculados.

**Body**:
```json
{
  "items": [
    {
      "id": 1,
      "type": "normal",
      "quantity": 10
    },
    {
      "id": 2,
      "type": "modelo",
      "model_id": 3,
      "quantity": 5
    }
  ]
}
```

**Response (200)**:
```json
{
  "items": [
    {
      "id": 1,
      "type": "normal", 
      "name": "Cabo USB-C 1 Metro",
      "price": 10.00,
      "quantity": 10,
      "total": 100.00,
      "price_type": "super_atacado"
    }
  ]
}
```

---

### 4. Sugestões de Busca
**Endpoint**: `GET /api/search-suggestions/?q={termo}`

Retorna sugestões inteligentes para autocomplete.

**Parameters**:
- `q`: Termo de busca (mínimo 2 caracteres)

**Response (200)**:
```json
{
  "suggestions": [
    {
      "text": "Cabo USB-C",
      "type": "produto"
    },
    {
      "text": "Cabos",
      "type": "categoria"  
    },
    {
      "text": "Apple",
      "type": "marca"
    }
  ]
}
```

**Rate Limit**: 30 requisições por minuto por IP

---

### 5. Tracking de Jornada
**Endpoint**: `POST /api/track-journey/`

Registra eventos da jornada do cliente.

**Body**:
```json
{
  "whatsapp": "(11) 99999-9999", // opcional
  "evento": "produto_visualizado",
  "dados_evento": {
    "produto_id": 1,
    "produto_nome": "Cabo USB-C",
    "categoria": "cabos"
  }
}
```

**Eventos Disponíveis**:
- `entrada` - Entrada no site
- `liberacao_preco` - Liberação de preços
- `categoria_visitada` - Navegação por categoria
- `pesquisa` - Busca realizada
- `produto_visualizado` - Produto visualizado
- `item_adicionado` - Item adicionado ao carrinho
- `item_removido` - Item removido do carrinho
- `checkout_iniciado` - Início do checkout
- `pedido_finalizado` - Pedido concluído
- `saida` - Saída do site

**Response (200)**:
```json
{
  "success": true
}
```

**Rate Limit**: 60 requisições por minuto por IP

---

### 6. Carrinho Abandonado
**Endpoint**: `POST /api/track-abandoned-cart/`

Registra um carrinho abandonado após inatividade.

**Body**:
```json
{
  "whatsapp": "(11) 99999-9999",
  "cart_data": [
    {
      "id": 1,
      "type": "normal",
      "quantity": 5
    }
  ],
  "estimated_value": 50.00,
  "session_id": "abc123"
}
```

**Response (200)**:
```json
{
  "success": true
}
```

**Rate Limit**: 3 requisições por minuto por IP

---

## 🎣 Webhooks

### Configuração

Os webhooks são configurados via Django Admin em `/admin/catalog/configuracaowebhook/`.

**Campos de Configuração**:
- `evento`: Tipo de evento (liberacao_preco, carrinho_abandonado, pedido_finalizado)
- `url`: URL de destino do webhook
- `ativo`: Se o webhook está ativo
- `timeout`: Timeout em segundos (padrão: 30s)
- `retry_ativo`: Se deve tentar novamente em caso de falha

---

### 1. Webhook de Liberação de Preços

**Evento**: `liberacao_preco`

**Payload**:
```json
{
  "evento": "liberacao_preco",
  "timestamp": "2025-08-17T20:00:00Z",
  "retry_count": 0,
  "whatsapp": "(11) 99999-9999",
  "liberation_timestamp": "2025-08-17T20:00:00Z"
}
```

**Disparado**: Quando um cliente fornece o WhatsApp para liberar preços

---

### 2. Webhook de Carrinho Abandonado

**Evento**: `carrinho_abandonado`

**Payload**:
```json
{
  "evento": "carrinho_abandonado", 
  "timestamp": "2025-08-17T20:30:00Z",
  "retry_count": 0,
  "whatsapp": "(11) 99999-9999",
  "cart_data": [
    {
      "id": 1,
      "type": "normal",
      "quantity": 5,
      "name": "Cabo USB-C"
    }
  ],
  "estimated_value": 50.00,
  "abandonment_time": "2025-08-17T20:30:00Z"
}
```

**Disparado**: 30 minutos após inatividade com itens no carrinho

---

### 3. Webhook de Pedido Finalizado

**Evento**: `pedido_finalizado`

**Payload**:
```json
{
  "evento": "pedido_finalizado",
  "timestamp": "2025-08-17T21:00:00Z", 
  "retry_count": 0,
  "whatsapp": "(11) 99999-9999",
  "order_code": "PM20250817000001",
  "customer_name": "João Silva",
  "total_value": 150.00,
  "items": [
    {
      "product_name": "Cabo USB-C 1 Metro",
      "quantity": 10,
      "unit_price": 10.00,
      "total_price": 100.00,
      "price_type": "super_atacado"
    }
  ],
  "journey_summary": {
    "categories_visited": ["cabos", "carregadores"],
    "searches_performed": ["cabo usb"],
    "products_viewed": [1, 2, 3],
    "time_on_site": "00:15:30"
  }
}
```

**Disparado**: Quando um pedido é finalizado com sucesso

---

## 🔄 Sistema de Retry

### Configuração
- **Tentativas**: 1 retry automático após falha
- **Delay**: 5 segundos entre tentativas
- **Timeout**: Configurável por webhook (padrão: 30s)

### Headers Enviados
```
Content-Type: application/json
User-Agent: PMCELL-Webhook/1.0
```

### Códigos de Status
- **2xx**: Sucesso, sem retry
- **4xx/5xx**: Falha, executa retry se habilitado
- **Timeout**: Executa retry se habilitado

### Logs
Todos os webhooks são logados com detalhes de sucesso/falha para monitoramento.

---

## 🛡️ Segurança

### Rate Limiting
- **Liberação de preços**: 5 req/min
- **Sugestões de busca**: 30 req/min  
- **Tracking de jornada**: 60 req/min
- **Carrinho abandonado**: 3 req/min
- **Webhooks específicos**: 1 req/5s

### Headers de Segurança
Todas as respostas incluem headers de segurança:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`

### Validação
- WhatsApp brasileiro obrigatório: `(XX) XXXXX-XXXX` ou `(XX) XXXX-XXXX`
- CSRF protection em todas as APIs
- Sanitização de inputs

---

## 🧪 Testes

### Teste de Webhook (httpbin)
```bash
# Configure no admin: https://httpbin.org/post
curl -X POST /api/liberate-prices/ \
  -H "Content-Type: application/json" \
  -d '{"whatsapp": "(11) 99999-9999"}'
```

### Teste de Rate Limit
```bash
# Dispare 6 requests rápidas para ver o 429
for i in {1..6}; do
  curl -X POST /api/liberate-prices/ \
    -H "Content-Type: application/json" \
    -d '{"whatsapp": "(11) 99999-999'$i'"}' &
done
```

### Monitoramento
- Logs de webhook em Django admin
- Métricas de rate limiting
- Tracking de jornadas completas

---

**🔌 Integração com n8n ou Zapier recomendada para automação de vendas**