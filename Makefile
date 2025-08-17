# PMCELL Catálogo - Makefile para comandos de desenvolvimento

.PHONY: help dev build clean test migrate admin shell logs

# Default target
help:
	@echo "PMCELL Catálogo - Comandos disponíveis:"
	@echo ""
	@echo "  dev          - Iniciar ambiente de desenvolvimento"
	@echo "  build        - Build dos containers"
	@echo "  stop         - Parar todos os containers"
	@echo "  clean        - Limpar containers, volumes e imagens"
	@echo "  migrate      - Rodar migrações do Django"
	@echo "  admin        - Criar superusuário do Django"
	@echo "  shell        - Abrir shell do Django"
	@echo "  logs         - Mostrar logs dos containers"
	@echo "  test         - Rodar testes"
	@echo "  lint         - Verificar código (backend e frontend)"
	@echo "  deps         - Instalar dependências"
	@echo "  reset        - Reset completo do ambiente"
	@echo ""

# Desenvolvimento
dev:
	docker-compose up -d db redis
	@echo "Aguardando banco de dados..."
	sleep 5
	cd backend && python3 -m pip install -r requirements.txt --user
	cd backend && python3 manage.py migrate
	cd backend && python3 manage.py runserver &
	cd frontend && npm install
	cd frontend && npm run dev

# Docker
build:
	docker-compose build

up:
	docker-compose up -d

stop:
	docker-compose stop

down:
	docker-compose down

clean:
	docker-compose down -v --remove-orphans
	docker system prune -f

# Django
migrate:
	cd backend && python3 manage.py migrate

makemigrations:
	cd backend && python3 manage.py makemigrations

admin:
	cd backend && python3 manage.py createsuperuser

shell:
	cd backend && python3 manage.py shell

collectstatic:
	cd backend && python3 manage.py collectstatic --noinput

# Logs
logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

logs-db:
	docker-compose logs -f db

# Testes
test:
	cd backend && python3 manage.py test
	cd frontend && npm run test

test-backend:
	cd backend && python3 manage.py test

test-frontend:
	cd frontend && npm run test

# Lint
lint:
	cd backend && python3 -m black . --check
	cd backend && python3 -m flake8 .
	cd frontend && npm run lint

lint-fix:
	cd backend && python3 -m black .
	cd frontend && npm run lint -- --fix

# Dependências
deps:
	cd backend && python3 -m pip install -r requirements.txt --user
	cd frontend && npm install

deps-update:
	cd backend && python3 -m pip install -r requirements.txt --upgrade --user
	cd frontend && npm update

# Reset
reset: clean
	docker volume rm $$(docker volume ls -q) 2>/dev/null || true
	cd backend && rm -rf __pycache__ .pytest_cache
	cd frontend && rm -rf .next node_modules
	make deps

# Produção
deploy-build:
	docker-compose -f docker-compose.prod.yml build

deploy-up:
	docker-compose -f docker-compose.prod.yml up -d

# Backup
backup:
	docker-compose exec db pg_dump -U pmcell_user pmcell_catalog > backup_$$(date +%Y%m%d_%H%M%S).sql

restore:
	@read -p "Nome do arquivo de backup: " backup_file; \
	docker-compose exec -T db psql -U pmcell_user -d pmcell_catalog < $$backup_file

# Monitoramento
status:
	docker-compose ps
	@echo ""
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@echo "Admin: http://localhost:8000/admin"

health:
	@curl -s http://localhost:8000/api/health/ || echo "Backend não disponível"
	@curl -s http://localhost:3000 > /dev/null && echo "Frontend OK" || echo "Frontend não disponível"