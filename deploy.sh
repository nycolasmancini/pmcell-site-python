#!/bin/bash

# 🚀 PMCELL Deploy Script - Deploy Direto no Servidor
echo "🎯 PMCELL Catálogo - Deploy Script"
echo "=================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir com cor
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Verificar se estamos no diretório correto
if [ ! -f "README.md" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    print_error "Execute este script no diretório raiz do projeto PMCELL"
    exit 1
fi

print_status "Diretório correto verificado"

# Verificar se git está inicializado
if [ ! -d ".git" ]; then
    print_error "Repositório Git não encontrado. Execute 'git init' primeiro"
    exit 1
fi

print_status "Repositório Git verificado"

# Verificar se há alterações para commit
if ! git diff-index --quiet HEAD --; then
    print_warning "Há alterações não commitadas"
    read -p "Deseja commitar as alterações? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Commitando alterações..."
        git add .
        git commit -m "🚀 Deploy: $(date '+%Y-%m-%d %H:%M:%S')"
        print_status "Alterações commitadas"
    else
        print_warning "Continuando sem commitar..."
    fi
fi

# Verificar se remote origin existe
if ! git remote get-url origin > /dev/null 2>&1; then
    print_error "Remote 'origin' não configurado"
    echo
    print_info "Você precisa:"
    echo "1. Criar repositório no GitHub"
    echo "2. git remote add origin https://github.com/SEU-USUARIO/pmcell-catalogo.git"
    echo "3. git push -u origin main"
    echo
    exit 1
fi

print_status "Remote origin configurado"

# Push para GitHub
print_info "Fazendo push para GitHub..."
if git push; then
    print_status "Push realizado com sucesso"
else
    print_error "Erro no push. Verifique suas credenciais GitHub"
    exit 1
fi

echo
echo "🎉 PREPARAÇÃO COMPLETA!"
echo "======================"
print_info "Próximos passos:"
echo
echo "1. 🚂 RAILWAY (Backend):"
echo "   - Acesse: https://railway.app"
echo "   - New Project → Deploy from GitHub"
echo "   - Selecione: pmcell-catalogo"
echo "   - Root Directory: /backend"
echo "   - Adicione PostgreSQL"
echo
echo "2. ▲ VERCEL (Frontend):"
echo "   - Acesse: https://vercel.com"
echo "   - New Project → Import GitHub"
echo "   - Selecione: pmcell-catalogo"
echo "   - Root Directory: /frontend"
echo
echo "3. 🔗 CONECTAR:"
echo "   - Configure CORS no Railway"
echo "   - Configure API_URL no Vercel"
echo
print_status "Deploy automático ativado! 🚀"
echo "Qualquer push agora fará deploy automaticamente!"