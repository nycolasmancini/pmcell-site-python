# PMCELL - Catálogo B2B 🚀

Sistema de catálogo online B2B para venda de acessórios de celular no atacado da marca PMCELL.

## 🌟 Funcionalidades

### 🛍️ Catálogo de Produtos
- **Produtos Normais**: Cabos, carregadores, fones - adição direta ao carrinho
- **Capas/Películas**: Seleção por marca e modelo específico do celular
- **Sistema de Preços**: Atacado e super atacado com quantidades mínimas
- **Busca Inteligente**: Por nome, categoria, marca, fabricante com autocomplete

### 🔐 Sistema de Liberação de Preços
- Preços bloqueados por padrão
- Liberação via WhatsApp brasileiro
- Cookie de 7 dias para persistência
- Webhook automático para equipe de vendas

### 🛒 Carrinho e Checkout
- Carrinho em localStorage (persistência 7 dias)
- Cálculo automático atacado/super atacado
- Checkout com validação de dados
- Geração de código único de pedido

### 📊 Tracking e Analytics
- Jornada completa do cliente
- Tempo no site, categorias visitadas
- Produtos visualizados e carrinho
- Carrinhos abandonados com webhook

### 🔗 Webhooks e Integração
- Liberação de preços
- Carrinho abandonado (30 min)
- Pedido finalizado
- Sistema de retry automático

## 🛠️ Stack Tecnológico

- **Backend**: Django 5.0 + Django REST Framework
- **Frontend**: Django Templates + HTMX + Alpine.js + Tailwind CSS
- **Banco de Dados**: PostgreSQL (Railway)
- **Storage**: Cloudinary (imagens)
- **Deploy**: Railway
- **Webhooks**: n8n (opcional)

## 🚀 Instalação e Setup

### Pré-requisitos
- Python 3.9+
- pip
- Git

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/pmcell-catalog.git
cd pmcell-catalog
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Configure as variáveis de ambiente
```bash
# .env (crie o arquivo)
SECRET_KEY=sua-secret-key-aqui
DEBUG=True
DATABASE_URL=postgresql://user:pass@localhost/pmcell_db
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name
```

### 4. Execute as migrações
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Carregue dados de teste (opcional)
```bash
python manage.py loaddata catalog/fixtures/initial_data.json
```

### 6. Execute o servidor
```bash
python manage.py runserver
```

Acesse: http://localhost:8000

## 📁 Estrutura do Projeto

```
pmcell-catalog/
├── manage.py
├── requirements.txt
├── pmcell/               # Configurações Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── catalog/              # App principal
│   ├── models.py         # Modelos de dados
│   ├── views.py          # Views e APIs
│   ├── admin.py          # Interface admin
│   ├── urls.py           # URLs do app
│   ├── cache_utils.py    # Sistema de cache
│   ├── webhook_utils.py  # Webhooks
│   └── middleware.py     # Rate limiting
├── templates/            # Templates HTML
│   ├── base.html
│   ├── catalog/
│   └── components/
└── static/              # CSS, JS, imagens
    ├── css/main.css
    ├── js/main.js
    └── images/
```

## 🔧 Configuração de Produção

### Railway Deploy
1. Conecte o repositório ao Railway
2. Configure as variáveis de ambiente:
   - `SECRET_KEY`
   - `DATABASE_URL` (PostgreSQL)
   - `CLOUDINARY_URL`
   - `DEBUG=False`
   - `ALLOWED_HOSTS=.railway.app`

### Webhooks (n8n)
1. Configure URLs no admin Django
2. Eventos disponíveis:
   - `liberacao_preco`
   - `carrinho_abandonado`
   - `pedido_finalizado`

## 📊 Dados e Modelos

### Principais Entidades
- **Categoria**: Organização dos produtos
- **ProdutoNormal**: Acessórios gerais
- **ProdutoCapaPelicula**: Produtos por modelo de celular
- **MarcaCelular**: Marcas de smartphones
- **ModeloCelular**: Modelos específicos
- **Pedido**: Pedidos finalizados
- **JornadaCliente**: Tracking de comportamento

### Sistema de Preços
- Preço atacado (padrão)
- Preço super atacado (quantidade mínima)
- Cálculo automático baseado na quantidade

## 🔍 APIs Disponíveis

### Liberação de Preços
```bash
POST /api/liberate-prices/
{
  "whatsapp": "(11) 99999-9999"
}
```

### Adicionar ao Carrinho
```bash
POST /api/add-to-cart/
{
  "product_id": 1,
  "product_type": "normal", # ou "modelo"
  "quantity": 10,
  "model_id": 1 # apenas para capas/películas
}
```

### Busca com Sugestões
```bash
GET /api/search-suggestions/?q=cabo
```

### Tracking de Jornada
```bash
POST /api/track-journey/
{
  "evento": "produto_visualizado",
  "dados_evento": {...}
}
```

## 🛡️ Segurança

- Rate limiting por IP
- Validação de WhatsApp brasileiro
- CSRF protection
- Headers de segurança customizados
- Sanitização de inputs

## 📈 Performance

- Cache inteligente (categorias, sugestões)
- Lazy loading de imagens
- Queries otimizadas (select_related)
- Compressão de assets CSS/JS
- CDN via Cloudinary

## 🎨 UX/UI

- Design mobile-first
- Animações suaves (Alpine.js)
- Loading states visuais
- Feedback imediato
- Grid responsivo (2-4 colunas)

## 🧪 Testes

### Testes Funcionais
```bash
# Testar fluxo completo
python manage.py test

# Testar APIs
curl -X POST http://localhost:8000/api/liberate-prices/ \
  -H "Content-Type: application/json" \
  -d '{"whatsapp": "(11) 99999-9999"}'
```

### Testes de Carga
```bash
# Múltiplas requisições simultâneas
for i in {1..10}; do
  curl -s http://localhost:8000/ &
done
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Add nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 📞 Suporte

- **Email**: suporte@pmcell.com
- **WhatsApp**: Entre no catálogo e libere os preços
- **Issues**: [GitHub Issues](https://github.com/seu-usuario/pmcell-catalog/issues)

---

**PMCELL** - Acessórios para celular no atacado 📱✨