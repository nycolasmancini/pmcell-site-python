# PMCELL - Catálogo Online

Catálogo online para venda de acessórios para celular no atacado.

## Stack Tecnológica

- **Backend**: Django 5.0 + Django REST Framework
- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS
- **Banco de Dados**: PostgreSQL
- **Deploy**: Railway (Backend) + Vercel (Frontend)

## Estrutura do Projeto

```
ecommerce-pmcell/
├── backend/          # Django API
├── frontend/         # Next.js App
└── docker-compose.yml
```

## Como Rodar

### Backend
```bash
cd backend
pip install -r requirements.txt
python manage.py runserver
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Funcionalidades

- Catálogo responsivo de produtos
- Sistema de preços atacado/super atacado
- Gestão de capas e películas por modelo
- Carrinho de compras
- Tracking de jornada do cliente
- Integração WhatsApp
- Painel administrativo completo