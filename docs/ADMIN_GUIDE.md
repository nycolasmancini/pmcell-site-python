# 🔧 Guia do Administrador - PMCELL

## 🚪 Acesso ao Admin

**URL**: `https://seu-dominio.com/admin/` ou `http://localhost:8000/admin/`

### Tipos de Usuário
- **Admin**: Acesso total (is_staff=True, is_superuser=True)
- **Vendedor**: Apenas visualização de pedidos e carrinhos (is_vendedor=True)

---

## 📊 Dashboard Principal

### Seções Disponíveis
1. **Catalog** - Gestão de produtos e configurações
2. **Authentication and Authorization** - Usuários e permissões

---

## 🛍️ Gestão de Produtos

### 1. Categorias

**Localização**: `Catalog > Categorias`

**Campos**:
- **Nome**: Nome da categoria (ex: "Cabos")
- **Slug**: URL amigável (auto-gerado)
- **Descrição**: Descrição opcional
- **Ativo**: Se a categoria aparece no site

**Ações**:
- ✅ Criar nova categoria
- ✏️ Editar categoria existente
- 🗑️ Desativar categoria
- 📋 Filtrar por ativo/inativo

---

### 2. Produtos Normais

**Localização**: `Catalog > Produtos normais`

**Campos Principais**:
- **Nome**: Nome do produto
- **Descrição**: Descrição detalhada
- **Categoria**: Categoria pai
- **Fabricante**: Marca do produto
- **Características**: Lista de características

**Preços**:
- **Preço Atacado**: Preço padrão
- **Preço Super Atacado**: Preço com desconto
- **Quantidade Mínima Super**: Qtd mínima para super atacado

**Controle**:
- **Em Estoque**: Se produto aparece no catálogo
- **Destaque**: Produto em destaque (futuro)

**Imagens**:
- Upload múltiplas imagens via inline
- Integração automática com Cloudinary
- Ordem das imagens configurável

**Exemplo de Cadastro**:
```
Nome: Cabo USB-C 2 Metros Premium
Categoria: Cabos
Fabricante: PMCELL
Preço Atacado: R$ 15,00
Preço Super Atacado: R$ 12,00
Quantidade Mínima Super: 20
Em Estoque: ✅
```

---

### 3. Capas e Películas

**Localização**: `Catalog > Produtos capa película`

**Diferencial**: Sistema de marcas e modelos específicos

**Campos Base**:
- **Nome**: Nome do produto (ex: "Capa Transparente Premium")
- **Descrição**: Descrição do produto
- **Categoria**: Geralmente "Capas" ou "Películas"
- **Fabricante**: Marca do fabricante

**Sistema de Modelos**:
- **Quantidade Mínima Super**: Aplicada a CADA modelo específico
- **Configuração via Inline**: Marcas e modelos na mesma tela

**Fluxo de Cadastro**:
1. Criar o produto base
2. Adicionar marcas de celular (inline)
3. Para cada marca, adicionar modelos
4. Definir preços específicos por modelo

**Exemplo Completo**:
```
Produto: Película de Vidro 9H
├── Apple
│   ├── iPhone 14 - R$ 18,00 / R$ 15,00
│   ├── iPhone 14 Pro - R$ 20,00 / R$ 17,00
│   └── iPhone 15 - R$ 22,00 / R$ 19,00
└── Samsung  
    ├── Galaxy S24 - R$ 16,00 / R$ 13,00
    └── Galaxy A54 - R$ 14,00 / R$ 11,00
```

---

## 📱 Gestão de Marcas e Modelos

### Marcas de Celular

**Localização**: `Catalog > Marcas de celular`

**Campos**:
- **Nome**: Nome da marca (ex: "Apple", "Samsung")
- **Ativo**: Se a marca aparece nas opções

### Modelos de Celular

**Localização**: `Catalog > Modelos de celular`

**Campos**:
- **Nome**: Nome do modelo (ex: "iPhone 14 Pro")
- **Marca**: Marca pai
- **Ativo**: Se o modelo aparece nas opções

**Dica**: Modelos são gerenciados automaticamente via inline nos produtos

---

## 🛒 Gestão de Pedidos

### Pedidos Finalizados

**Localização**: `Catalog > Pedidos`

**Informações Exibidas**:
- **Código**: Código único (PM20250817000001)
- **Cliente**: Nome e WhatsApp
- **Status**: Aberto/Solucionado
- **Valor Total**: Valor do pedido
- **Data**: Data da criação

**Filtros Disponíveis**:
- Por status (aberto/solucionado)
- Por data
- Por cliente

**Ações**:
- ✅ Marcar como solucionado
- 👁️ Ver detalhes completos
- 📋 Exportar dados

**Detalhes do Pedido**:
- Lista de itens com preços
- Informações do cliente
- Dados da jornada
- Timestamps completos

---

### Carrinhos Abandonados

**Localização**: `Catalog > Carrinhos abandonados`

**Informações**:
- **WhatsApp**: Cliente que abandonou
- **Valor Estimado**: Valor do carrinho
- **Tempo de Abandono**: Quando foi abandonado
- **Webhook Enviado**: Status do webhook

**Uso**:
- Identificar oportunidades de recuperação
- Analisar produtos mais abandonados
- Monitorar conversão

---

## 📈 Analytics e Jornada

### Jornada dos Clientes

**Localização**: `Catalog > Jornadas dos clientes`

**Dados Coletados**:
- **WhatsApp**: Identificação do cliente
- **Evento**: Tipo de ação realizada
- **Dados do Evento**: Detalhes específicos
- **Timestamp**: Momento da ação

**Eventos Rastreados**:
- Entrada no site
- Liberação de preços
- Categorias visitadas
- Pesquisas realizadas
- Produtos visualizados
- Itens adicionados/removidos
- Checkout iniciado
- Pedido finalizado

**Análises Possíveis**:
- Funil de conversão
- Produtos mais visualizados
- Categorias populares
- Tempo médio no site

---

## 🔗 Configuração de Webhooks

### Configurações de Webhook

**Localização**: `Catalog > Configurações de webhook`

**Eventos Disponíveis**:
1. **Liberação de Preços** (`liberacao_preco`)
2. **Carrinho Abandonado** (`carrinho_abandonado`)  
3. **Pedido Finalizado** (`pedido_finalizado`)

**Configuração por Evento**:
- **URL**: Endpoint de destino
- **Ativo**: Se o webhook está ativo
- **Timeout**: Timeout em segundos (padrão: 30s)
- **Retry Ativo**: Se deve tentar novamente

**Exemplos de URL**:
```
# n8n
https://n8n.seudominio.com/webhook/pmcell-precos

# Zapier  
https://hooks.zapier.com/hooks/catch/123456/abcdef/

# Webhook.site (teste)
https://webhook.site/#!/view/seu-id-aqui
```

**Teste de Webhook**:
1. Configure URL de teste (ex: httpbin.org/post)
2. Ative o webhook
3. Execute ação no site (liberar preços)
4. Verifique logs

---

## ⚙️ Configurações Gerais

### Configurações Gerais

**Localização**: `Catalog > Configurações gerais`

**Configurações Disponíveis**:
- URLs de webhook padrão
- Timeouts globais
- Configurações de cache
- Parâmetros do sistema

**Formato Chave-Valor**:
```
Chave: webhook_timeout_default
Valor: 30

Chave: cache_categories_timeout  
Valor: 3600
```

---

## 👥 Gestão de Usuários

### Usuários do Sistema

**Localização**: `Authentication and Authorization > Users`

**Tipos de Perfil**:

**Administrator (Super Admin)**:
```
✅ is_staff = True
✅ is_superuser = True  
❌ is_vendedor = False
```
- Acesso total ao admin
- Pode gerenciar produtos, usuários, configurações
- Pode ver e editar tudo

**Vendedor**:
```
✅ is_staff = True
❌ is_superuser = False
✅ is_vendedor = True
```
- Acesso limitado ao admin
- Pode ver apenas pedidos e carrinhos
- Não pode editar produtos ou configurações

**Criação de Vendedor**:
1. Criar usuário normal
2. Marcar `is_staff = True`
3. Marcar `is_vendedor = True`
4. NÃO marcar `is_superuser`

---

## 🔧 Manutenção e Monitoramento

### Cache do Sistema

**Verificar Cache**:
```python
# Django shell
python manage.py shell

from django.core.cache import cache
from catalog.cache_utils import get_cached_categories

# Ver categorias em cache
categorias = get_cached_categories()
print(f"Categorias: {len(categorias)}")

# Limpar cache específico
cache.delete('categories_active')

# Limpar todo cache
cache.clear()
```

### Logs de Sistema

**Localização dos Logs**:
- Webhooks: Console do servidor
- Rate limiting: Headers HTTP
- Errors: Django debug

**Monitoramento**:
- Verificar pedidos diários
- Acompanhar carrinhos abandonados
- Monitorar tempo de resposta

---

## 🚨 Solução de Problemas

### Problemas Comuns

**1. Imagens não aparecem**
- Verificar configuração Cloudinary
- Conferir CLOUDINARY_URL no .env
- Testar upload manual

**2. Webhooks não funcionam**
- Verificar se URL está ativa
- Testar com webhook.site
- Verificar logs de erro

**3. Preços não calculam**
- Verificar se produtos têm preços
- Conferir quantidade mínima super atacado
- Verificar se produto está em estoque

**4. Rate limiting muito restritivo**
- Editar catalog/middleware.py
- Ajustar limites por endpoint
- Considerar whitelist IPs

### Comandos Úteis

```bash
# Limpar cache
python manage.py shell -c "from django.core.cache import cache; cache.clear()"

# Recriar superuser
python manage.py createsuperuser

# Verificar produtos ativos
python manage.py shell -c "from catalog.models import *; print(f'Produtos: {ProdutoNormal.objects.filter(em_estoque=True).count()}')"

# Backup dados
python manage.py dumpdata catalog > backup.json

# Restaurar dados  
python manage.py loaddata backup.json
```

---

## 📋 Checklist Pós-Deploy

### Configuração Inicial
- [ ] Criar superuser
- [ ] Configurar categorias base
- [ ] Carregar produtos iniciais
- [ ] Configurar marcas de celular
- [ ] Testar fluxo completo

### Webhooks
- [ ] Configurar URLs de produção
- [ ] Testar todos os eventos
- [ ] Verificar logs
- [ ] Configurar monitoramento

### Segurança
- [ ] Alterar senha padrão
- [ ] Configurar HTTPS
- [ ] Verificar rate limits
- [ ] Testar permissões vendedor

---

**📞 Suporte Admin**: Para problemas técnicos, verificar logs e documentação de APIs.**