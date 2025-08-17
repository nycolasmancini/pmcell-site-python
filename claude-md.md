# Projeto: Catálogo B2B PMCELL

## Visão Geral
Sistema de catálogo online B2B para venda de acessórios de celular no atacado da marca PMCELL. O catálogo possui sistema de liberação de preços via WhatsApp, carrinho de compras, tracking de jornada do cliente e dois tipos distintos de produtos.

## Stack Tecnológico
- **Backend**: Django 5.0 + Django REST Framework
- **Frontend**: Django Templates + HTMX + Alpine.js + Tailwind CSS
- **Banco de Dados**: PostgreSQL (Railway)
- **Storage de Imagens**: Cloudinary
- **Deploy**: Railway
- **Webhooks**: n8n

## Arquitetura do Sistema

### 1. Tipos de Produtos

#### 1.1 Produtos Normais (Acessórios)
- Nome, descrição, características, fabricante
- Preço atacado e super atacado
- Quantidade mínima para super atacado (definida por produto)
- Adição direta ao carrinho do catálogo
- Categorias: Cabos, Carregadores, Fones, etc.

#### 1.2 Produtos Especiais (Capas e Películas)
- Nome, descrição, características, fabricante
- Botão "Ver Modelos" ao invés de adicionar ao carrinho
- Fluxo: Produto → Marcas → Modelos → Carrinho
- Cada modelo tem preço próprio (atacado e super atacado)
- Quantidade para super atacado definida no produto pai
- Super atacado só vale comprando X peças do MESMO modelo
- No catálogo mostra range de preços (min-max)

### 2. Sistema de Preços

#### 2.1 Liberação de Preços
- Site inicia com preços bloqueados
- Modal solicita WhatsApp para liberar
- Cookie de 7 dias mantém liberação
- Cada visita nova solicita WhatsApp novamente

#### 2.2 Regras de Super Atacado
- Quantidade mínima definida por produto
- Para acessórios: X unidades do mesmo produto
- Para capas/películas: X unidades do mesmo modelo específico

### 3. Interface do Usuário

#### 3.1 Catálogo
- Cards responsivos: 2 colunas mobile, mais em desktop
- Imagem principal + carrossel de imagens ao clicar
- Barra de pesquisa com regex (busca nome, categoria, marca)
- Filtros por categoria
- Botões +/- para quantidade
- Produtos fora de estoque não aparecem

#### 3.2 Carrinho
- Armazenado em cookies locais (não vinculado ao WhatsApp)
- Persiste por 7 dias
- Mostra preços conforme quantidade (atacado/super atacado)

#### 3.3 Finalização
- Solicita nome do cliente
- Confirma WhatsApp (permite correção)
- Gera código único do pedido
- Salva mesmo sem nome preenchido

### 4. Painel Administrativo

#### 4.1 Níveis de Acesso
- **Admin**: Acesso total
- **Vendedor**: Visualiza apenas pedidos e carrinhos

#### 4.2 Módulos
- **Produtos Normais**: CRUD completo
- **Capas/Películas**: CRUD com gestão de marcas/modelos
- **Categorias**: CRUD de categorias
- **Usuários**: Gestão de admins e vendedores
- **Pedidos**: Visualização com filtros (aberto/solucionado)
- **Carrinhos Abandonados**: Lista e análise
- **Configurações**: URLs de webhooks, configurações gerais

#### 4.3 Cadastro de Produtos
- Upload múltiplas imagens (Cloudinary)
- Toggle em estoque/fora de estoque
- Para capas/películas: interface para adicionar marcas → modelos → preços

### 5. Tracking e Analytics

#### 5.1 Dados Coletados
- Tempo no site
- Categorias visitadas/não visitadas
- Pesquisas realizadas
- Produtos visualizados em detalhe
- Carrinho montado
- Jornada completa até pedido

#### 5.2 Armazenamento
- Todos os dados salvos no PostgreSQL
- Estrutura preparada para analytics futuros

### 6. Webhooks

#### 6.1 Eventos
- **Liberação de preços**: WhatsApp fornecido
- **Carrinho abandonado**: Após X minutos de inatividade
- **Pedido finalizado**: Com dados completos da jornada

#### 6.2 Configuração
- URLs configuráveis no admin para cada evento
- Formato JSON
- Retry automático (1x após falha)
- Sem autenticação (n8n)

### 7. Design e UX

#### 7.1 Visual
- Design clean e minimalista
- Cores: Laranja PMCELL para marca, verde/azul para CTAs
- Modo claro apenas
- Animações suaves com Alpine.js
- Mobile-first

#### 7.2 Performance
- HTMX para interações sem reload
- Lazy loading de imagens
- Otimização automática via Cloudinary

## Modelos de Dados

### Principais Entidades
1. **User** (Django built-in + is_vendedor field)
2. **Categoria**
3. **Produto** (abstract)
   - ProdutoNormal
   - ProdutoCapaPelicula
4. **MarcaCelular**
5. **ModeloCelular**
6. **PrecoModelo** (relação Modelo + Produto)
7. **CarrinhoAbandonado**
8. **Pedido**
9. **ItemPedido**
10. **JornadaCliente**
11. **ConfiguracaoWebhook**

## Validações Importantes

### WhatsApp
- Formato: (XX) XXXXX-XXXX ou (XX) XXXX-XXXX
- Aceitar com ou sem o 9 adicional
- Apenas números brasileiros

### Carrinho
- Verificar quantidade mínima para super atacado
- Calcular preço correto baseado na quantidade
- Para capas/películas: validar modelo selecionado

## Segurança
- CSRF protection (Django built-in)
- Autenticação para admin
- Sanitização de inputs de pesquisa
- Rate limiting para webhooks
- Validação de uploads de imagem

## Deploy Railway

### Variáveis de Ambiente
```
DATABASE_URL=postgresql://...
SECRET_KEY=...
CLOUDINARY_URL=cloudinary://...
DEBUG=False
ALLOWED_HOSTS=.railway.app
```

### Comandos
```bash
# Inicial
railway login
railway link
railway up

# Updates
git push origin main  # Auto-deploy via GitHub
```

## Estrutura de Pastas
```
pmcell_catalog/
├── manage.py
├── requirements.txt
├── railway.json
├── pmcell/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── catalog/
│   ├── models.py
│   ├── views.py
│   ├── admin.py
│   ├── forms.py
│   └── urls.py
├── templates/
│   ├── base.html
│   ├── catalog/
│   └── admin/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
└── media/  # Desenvolvimento local apenas
```

## Prioridades de Desenvolvimento
1. Setup inicial Django + Railway
2. Modelos de dados + Admin
3. Sistema de liberação de preços
4. Catálogo com produtos normais
5. Sistema de capas/películas
6. Carrinho + Finalização
7. Webhooks + Tracking
8. Polish (animações, otimizações)