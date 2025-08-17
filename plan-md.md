# Plano de Desenvolvimento - PMCELL Catálogo B2B

## Status Geral: 🟡 Em Progresso - Fase 1 Completa
**Última Atualização**: 17/08/2025 - Setup Inicial Concluído
**Sprint Atual**: Modelos e Admin (Fase 2)

---

## FASE 1: SETUP E INFRAESTRUTURA ✅

### 1.1 Configuração de Serviços
- [x] Criar conta no GitHub
- [x] Criar repositório `pmcell-catalog`
- [ ] Criar conta no Railway
- [ ] Criar conta no Cloudinary
- [ ] Configurar n8n (opcional por enquanto)

### 1.2 Setup Local
- [x] Instalar Python 3.9+
- [x] Criar ambiente virtual
- [x] Instalar Django e dependências

### 1.3 Projeto Django Inicial
- [x] `django-admin startproject pmcell`
- [x] Criar app `catalog`
- [x] Configurar settings.py para Railway
- [x] Configurar PostgreSQL
- [x] Configurar Cloudinary
- [x] Criar requirements.txt

### 1.4 Deploy Inicial
- [ ] Inicializar Git
- [ ] Primeiro commit
- [ ] Conectar GitHub ao Railway
- [ ] Deploy teste "Hello World"
- [ ] Configurar domínio (se tiver)

**Comando para esta fase**: `Setup completo do ambiente`

---

## FASE 2: MODELOS E ADMIN 🔴

### 2.1 Modelos Base
- [ ] Modelo User customizado (is_vendedor)
- [ ] Modelo Categoria
- [ ] Modelo abstrato Produto
- [ ] Modelo ProdutoNormal
- [ ] Modelo ProdutoCapaPelicula
- [ ] Modelo MarcaCelular
- [ ] Modelo ModeloCelular
- [ ] Modelo PrecoModelo

### 2.2 Modelos de Pedido
- [ ] Modelo Pedido
- [ ] Modelo ItemPedido
- [ ] Modelo CarrinhoAbandonado
- [ ] Modelo JornadaCliente

### 2.3 Modelos de Configuração
- [ ] Modelo ConfiguracaoWebhook
- [ ] Modelo ConfiguracaoGeral

### 2.4 Admin Interface
- [ ] Configurar admin para ProdutoNormal
- [ ] Configurar admin para ProdutoCapaPelicula (inline para modelos)
- [ ] Configurar admin para Categorias
- [ ] Configurar admin para Pedidos
- [ ] Configurar admin para Usuários
- [ ] Customizar dashboard admin
- [ ] Implementar permissões (Admin vs Vendedor)

### 2.5 Fixtures e Dados Teste
- [ ] Criar categorias iniciais
- [ ] Criar produtos de teste
- [ ] Criar marcas/modelos de teste

**Comando para esta fase**: `Criar todos os modelos e configurar admin`

---

## FASE 3: FRONTEND BASE 🔴

### 3.1 Setup Frontend
- [ ] Configurar Tailwind CSS
- [ ] Configurar Alpine.js
- [ ] Configurar HTMX
- [ ] Criar template base.html
- [ ] Configurar static files

### 3.2 Layout Principal
- [ ] Header com logo PMCELL
- [ ] Barra de pesquisa
- [ ] Menu de categorias
- [ ] Footer
- [ ] Indicador de carrinho

### 3.3 Sistema de Liberação de Preços
- [ ] Modal de WhatsApp
- [ ] Validação de número brasileiro
- [ ] Sistema de cookies (7 dias)
- [ ] Blur/overlay nos preços bloqueados
- [ ] Lógica de desbloqueio

**Comando para esta fase**: `Implementar layout base e sistema de WhatsApp`

---

## FASE 4: CATÁLOGO DE PRODUTOS 🔴

### 4.1 Listagem de Produtos
- [ ] Grid responsivo de cards (2 col mobile)
- [ ] Card de produto normal
- [ ] Card de capa/película (com range de preço)
- [ ] Lazy loading de imagens
- [ ] Filtro por categoria
- [ ] Ordenação

### 4.2 Pesquisa
- [ ] Implementar busca com regex
- [ ] Busca por nome
- [ ] Busca por categoria
- [ ] Busca por marca
- [ ] Autocomplete (opcional)

### 4.3 Detalhes do Produto
- [ ] Modal/página de detalhes
- [ ] Carrossel de imagens
- [ ] Seletor de quantidade (+/-)
- [ ] Cálculo automático atacado/super atacado
- [ ] Botão adicionar ao carrinho

### 4.4 Sistema Capas/Películas
- [ ] Botão "Ver Modelos"
- [ ] Modal de seleção de marca
- [ ] Lista de modelos por marca
- [ ] Preço específico por modelo
- [ ] Adicionar modelo específico ao carrinho

**Comando para esta fase**: `Criar catálogo completo com ambos tipos de produto`

---

## FASE 5: CARRINHO E CHECKOUT 🔴

### 5.1 Carrinho de Compras
- [ ] Armazenamento em localStorage
- [ ] Adicionar/remover items
- [ ] Alterar quantidades
- [ ] Cálculo de preços (atacado/super)
- [ ] Persistência 7 dias

### 5.2 Página do Carrinho
- [ ] Listar items
- [ ] Editar quantidades
- [ ] Remover items
- [ ] Resumo de valores
- [ ] Botão finalizar

### 5.3 Finalização
- [ ] Form nome + confirmação WhatsApp
- [ ] Validação de campos
- [ ] Geração código do pedido
- [ ] Salvar pedido no banco
- [ ] Página de confirmação

**Comando para esta fase**: `Implementar carrinho completo e checkout`

---

## FASE 6: TRACKING E WEBHOOKS 🔴

### 6.1 Sistema de Tracking
- [ ] Capturar tempo no site
- [ ] Registrar categorias visitadas
- [ ] Salvar pesquisas realizadas
- [ ] Registrar produtos visualizados
- [ ] Monitorar carrinho

### 6.2 Jornada do Cliente
- [ ] Modelo para armazenar jornada
- [ ] Associar ao WhatsApp
- [ ] Timeline de eventos
- [ ] Consolidar dados no pedido

### 6.3 Webhooks
- [ ] Webhook liberação de preços
- [ ] Webhook carrinho abandonado (timer)
- [ ] Webhook pedido finalizado
- [ ] Sistema de retry
- [ ] Interface admin para URLs

### 6.4 Carrinhos Abandonados
- [ ] Detectar abandono (30 min?)
- [ ] Salvar estado do carrinho
- [ ] Listar no admin
- [ ] Filtros e status

**Comando para esta fase**: `Implementar tracking completo e webhooks`

---

## FASE 7: OTIMIZAÇÕES E POLISH 🔴

### 7.1 Performance
- [ ] Otimizar queries (select_related)
- [ ] Cache de categorias
- [ ] Compressão de assets
- [ ] Minificação CSS/JS
- [ ] Otimização de imagens Cloudinary

### 7.2 UX/Animações
- [ ] Transições suaves Alpine.js
- [ ] Loading states
- [ ] Feedback visual de ações
- [ ] Animações de carrinho
- [ ] Micro-interações

### 7.3 SEO/Meta
- [ ] Meta tags
- [ ] Open Graph
- [ ] Sitemap
- [ ] Robots.txt
- [ ] Schema.org para produtos

### 7.4 Segurança
- [ ] Rate limiting
- [ ] Validações extras
- [ ] Testes de SQL injection
- [ ] Configurar CORS
- [ ] Headers de segurança

**Comando para esta fase**: `Otimizar performance e adicionar polish`

---

## FASE 8: TESTES E AJUSTES FINAIS 🔴

### 8.1 Testes Funcionais
- [ ] Testar fluxo completo de compra
- [ ] Testar produtos normais
- [ ] Testar capas/películas
- [ ] Testar em mobile
- [ ] Testar webhooks

### 8.2 Testes de Carga
- [ ] Testar com muitos produtos
- [ ] Testar múltiplos usuários
- [ ] Monitorar performance

### 8.3 Documentação
- [ ] README.md do projeto
- [ ] Documentação de APIs/Webhooks
- [ ] Guia de uso do admin
- [ ] Backup e restore

### 8.4 Preparação para Produção
- [ ] Configurar domínio final
- [ ] SSL/HTTPS
- [ ] Backup automático
- [ ] Monitoramento
- [ ] Google Analytics (opcional)

**Comando para esta fase**: `Testes finais e go-live`

---

## PROGRESSO POR SPRINT

### Sprint 1 (Dias 1-2): Setup + Modelos ⏳
- **Meta**: Ter o projeto rodando no Railway com admin funcional
- **Fases**: 1.1 até 2.5
- **Status**: Não iniciado

### Sprint 2 (Dias 3-4): Frontend + Catálogo ⏳
- **Meta**: Catálogo funcional com liberação de preços
- **Fases**: 3.1 até 4.4
- **Status**: Aguardando Sprint 1

### Sprint 3 (Dias 5-6): Carrinho + Tracking ⏳
- **Meta**: Sistema completo de compra
- **Fases**: 5.1 até 6.4
- **Status**: Aguardando Sprint 2

### Sprint 4 (Dia 7): Polish + Deploy ⏳
- **Meta**: Otimizações e lançamento
- **Fases**: 7.1 até 8.4
- **Status**: Aguardando Sprint 3

---

## NOTAS DE DESENVOLVIMENTO

### ⚠️ Pontos Críticos
1. Validação de WhatsApp brasileiro (com e sem 9)
2. Cálculo correto de super atacado para modelos
3. Range de preços para capas/películas
4. Carrinho em localStorage (não vincular ao WhatsApp)
5. Webhook retry mechanism

### 💡 Decisões Tomadas
1. Django ao invés de Node.js (admin pronto)
2. HTMX ao invés de React (simplicidade)
3. Railway ao invés de Vercel (backend Python)
4. Cloudinary para imagens (free tier bom)
5. Sem autenticação de usuário final (só WhatsApp)

### 📝 Lembretes
- Sempre testar em mobile primeiro
- Salvar jornada mesmo sem nome
- Produtos fora de estoque não aparecem
- Super atacado por modelo individual (capas)
- Webhooks configuráveis no admin

### 🐛 Bugs Conhecidos
- Nenhum ainda

### ✅ Features Concluídas
- ✅ Setup completo do ambiente Django
- ✅ Configuração para Railway e PostgreSQL
- ✅ Integração com Cloudinary
- ✅ App catalog criado
- ✅ Estrutura básica de arquivos
- ✅ Configuração de static files e whitenoise

---

## COMANDOS ÚTEIS

```bash
# Desenvolvimento local
python manage.py runserver
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic

# Deploy Railway
railway login
railway link
railway up
railway logs

# Git
git add .
git commit -m "feat: descrição"
git push origin main
```

---

## LINKS IMPORTANTES

- **Repositório**: [Será criado]
- **Railway App**: [Será criado]
- **Cloudinary**: [Será configurado]
- **n8n**: [Será configurado]

---

**Use @plan.md em cada prompt para atualizar o progresso!**