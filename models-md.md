# Estrutura de Modelos - PMCELL Catálogo

## Diagrama de Relacionamentos

```
User (Django Built-in)
├── is_vendedor (Boolean)
└── pedidos (FK → Pedido)

Categoria
├── nome
├── slug
├── ordem
└── produtos (FK → Produto)

Produto (Abstract)
├── nome
├── descricao
├── caracteristicas (Text)
├── fabricante
├── categoria (FK → Categoria)
├── imagem_principal (Cloudinary)
├── imagens_adicionais (JSON)
├── preco_atacado
├── preco_super_atacado
├── quantidade_super_atacado
├── em_estoque (Boolean)
├── criado_em
└── atualizado_em
    ├── ProdutoNormal (extends Produto)
    └── ProdutoCapaPelicula (extends Produto)
        └── modelos (M2M → ModeloCelular through PrecoModelo)

MarcaCelular
├── nome (Samsung, Apple, Motorola, etc)
└── modelos (FK → ModeloCelular)

ModeloCelular
├── marca (FK → MarcaCelular)
├── nome (Galaxy S23, iPhone 15, etc)
└── precos (through → PrecoModelo)

PrecoModelo (Through Table)
├── produto_capa_pelicula (FK → ProdutoCapaPelicula)
├── modelo (FK → ModeloCelular)
├── preco_atacado
└── preco_super_atacado

Pedido
├── codigo (Único, auto-gerado: PMC-2024-0001)
├── whatsapp_inicial
├── whatsapp_confirmado
├── nome_cliente
├── items (FK → ItemPedido)
├── valor_total
├── status (aberto/solucionado)
├── jornada (OneToOne → JornadaCliente)
├── criado_em
└── atualizado_em

ItemPedido
├── pedido (FK → Pedido)
├── produto (Generic FK → ProdutoNormal ou ProdutoCapaPelicula)
├── modelo (FK → ModeloCelular, nullable)
├── quantidade
├── preco_unitario
└── subtotal

CarrinhoAbandonado
├── session_id
├── whatsapp
├── items (JSON)
├── valor_total
├── jornada (OneToOne → JornadaCliente)
├── abandonado_em
└── recuperado (Boolean)

JornadaCliente
├── session_id
├── whatsapp
├── tempo_no_site (Duration)
├── categorias_visitadas (JSON Array)
├── categorias_nao_visitadas (JSON Array)
├── pesquisas_realizadas (JSON Array)
├── produtos_visualizados (JSON Array)
├── eventos (JSON Array com timestamps)
├── iniciado_em
└── finalizado_em

ConfiguracaoWebhook
├── evento (choices: preco_liberado/carrinho_abandonado/pedido_finalizado)
├── url
├── ativo (Boolean)
├── ultima_execucao
└── ultimo_status

ConfiguracaoGeral
├── chave
├── valor
└── tipo (string/integer/boolean/json)
```

## Implementação Django Models

### 1. models.py - User Extension

```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_vendedor = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
```

### 2. models.py - Categoria

```python
class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    ordem = models.IntegerField(default=0)
    ativo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'categorias'
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['ordem', 'nome']
    
    def __str__(self):
        return self.nome
```

### 3. models.py - Produtos

```python
from cloudinary.models import CloudinaryField

class Produto(models.Model):
    nome = models.CharField(max_length=200)
    descricao = models.TextField()
    caracteristicas = models.TextField()
    fabricante = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    imagem_principal = CloudinaryField('imagem')
    imagens_adicionais = models.JSONField(default=list, blank=True)
    preco_atacado = models.DecimalField(max_digits=10, decimal_places=2)
    preco_super_atacado = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade_super_atacado = models.IntegerField(default=10)
    em_estoque = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        
class ProdutoNormal(Produto):
    class Meta:
        db_table = 'produtos_normais'
        verbose_name = 'Produto Normal'
        verbose_name_plural = 'Produtos Normais'
    
    def __str__(self):
        return f"{self.nome} - R$ {self.preco_atacado}"

class ProdutoCapaPelicula(Produto):
    class Meta:
        db_table = 'produtos_capas_peliculas'
        verbose_name = 'Capa/Película'
        verbose_name_plural = 'Capas/Películas'
    
    def __str__(self):
        return f"{self.nome} (Capa/Película)"
    
    @property
    def preco_min_atacado(self):
        precos = self.precomodelo_set.all()
        if precos:
            return min(p.preco_atacado for p in precos)
        return self.preco_atacado
    
    @property
    def preco_max_atacado(self):
        precos = self.precomodelo_set.all()
        if precos:
            return max(p.preco_atacado for p in precos)
        return self.preco_atacado
```

### 4. models.py - Marcas e Modelos

```python
class MarcaCelular(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    ordem = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'marcas_celular'
        verbose_name = 'Marca de Celular'
        verbose_name_plural = 'Marcas de Celular'
        ordering = ['ordem', 'nome']
    
    def __str__(self):
        return self.nome

class ModeloCelular(models.Model):
    marca = models.ForeignKey(MarcaCelular, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'modelos_celular'
        verbose_name = 'Modelo de Celular'
        verbose_name_plural = 'Modelos de Celular'
        ordering = ['marca', 'nome']
        unique_together = ['marca', 'nome']
    
    def __str__(self):
        return f"{self.marca.nome} {self.nome}"

class PrecoModelo(models.Model):
    produto = models.ForeignKey(ProdutoCapaPelicula, on_delete=models.CASCADE)
    modelo = models.ForeignKey(ModeloCelular, on_delete=models.CASCADE)
    preco_atacado = models.DecimalField(max_digits=10, decimal_places=2)
    preco_super_atacado = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'precos_modelos'
        verbose_name = 'Preço por Modelo'
        verbose_name_plural = 'Preços por Modelo'
        unique_together = ['produto', 'modelo']
    
    def __str__(self):
        return f"{self.produto.nome} - {self.modelo}"
```

### 5. models.py - Pedidos

```python
class Pedido(models.Model):
    STATUS_CHOICES = [
        ('aberto', 'Em Aberto'),
        ('solucionado', 'Solucionado'),
    ]
    
    codigo = models.CharField(max_length=20, unique=True)
    whatsapp_inicial = models.CharField(max_length=20)
    whatsapp_confirmado = models.CharField(max_length=20, blank=True)
    nome_cliente = models.CharField(max_length=200, blank=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberto')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'pedidos'
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-criado_em']
    
    def save(self, *args, **kwargs):
        if not self.codigo:
            # Gerar código único: PMC-2024-0001
            from datetime import datetime
            year = datetime.now().year
            last_order = Pedido.objects.filter(
                codigo__startswith=f'PMC-{year}-'
            ).order_by('-codigo').first()
            
            if last_order:
                last_num = int(last_order.codigo.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            
            self.codigo = f'PMC-{year}-{new_num:04d}'
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Pedido {self.codigo}"

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    
    # Para permitir tanto ProdutoNormal quanto ProdutoCapaPelicula
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    produto = GenericForeignKey('content_type', 'object_id')
    
    modelo = models.ForeignKey(ModeloCelular, on_delete=models.SET_NULL, null=True, blank=True)
    quantidade = models.IntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'items_pedido'
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Items do Pedido'
    
    def save(self, *args, **kwargs):
        self.subtotal = self.quantidade * self.preco_unitario
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome}"
```

### 6. models.py - Tracking

```python
class JornadaCliente(models.Model):
    session_id = models.CharField(max_length=100)
    whatsapp = models.CharField(max_length=20, blank=True)
    tempo_no_site = models.DurationField(null=True)
    categorias_visitadas = models.JSONField(default=list)
    categorias_nao_visitadas = models.JSONField(default=list)
    pesquisas_realizadas = models.JSONField(default=list)
    produtos_visualizados = models.JSONField(default=list)
    eventos = models.JSONField(default=list)
    iniciado_em = models.DateTimeField(auto_now_add=True)
    finalizado_em = models.DateTimeField(null=True)
    
    class Meta:
        db_table = 'jornadas_cliente'
        verbose_name = 'Jornada do Cliente'
        verbose_name_plural = 'Jornadas dos Clientes'
        ordering = ['-iniciado_em']
    
    def __str__(self):
        return f"Jornada {self.session_id[:8]}..."

class CarrinhoAbandonado(models.Model):
    session_id = models.CharField(max_length=100)
    whatsapp = models.CharField(max_length=20, blank=True)
    items = models.JSONField()
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    jornada = models.OneToOneField(JornadaCliente, on_delete=models.CASCADE, null=True)
    abandonado_em = models.DateTimeField(auto_now_add=True)
    recuperado = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'carrinhos_abandonados'
        verbose_name = 'Carrinho Abandonado'
        verbose_name_plural = 'Carrinhos Abandonados'
        ordering = ['-abandonado_em']
    
    def __str__(self):
        return f"Carrinho {self.session_id[:8]}... - R$ {self.valor_total}"
```

### 7. models.py - Configurações

```python
class ConfiguracaoWebhook(models.Model):
    EVENTO_CHOICES = [
        ('preco_liberado', 'Preço Liberado'),
        ('carrinho_abandonado', 'Carrinho Abandonado'),
        ('pedido_finalizado', 'Pedido Finalizado'),
    ]
    
    evento = models.CharField(max_length=30, choices=EVENTO_CHOICES, unique=True)
    url = models.URLField(blank=True)
    ativo = models.BooleanField(default=True)
    ultima_execucao = models.DateTimeField(null=True)
    ultimo_status = models.CharField(max_length=200, blank=True)
    
    class Meta:
        db_table = 'configuracoes_webhook'
        verbose_name = 'Configuração de Webhook'
        verbose_name_plural = 'Configurações de Webhook'
    
    def __str__(self):
        return f"Webhook: {self.get_evento_display()}"

class ConfiguracaoGeral(models.Model):
    TIPO_CHOICES = [
        ('string', 'Texto'),
        ('integer', 'Número'),
        ('boolean', 'Sim/Não'),
        ('json', 'JSON'),
    ]
    
    chave = models.CharField(max_length=100, unique=True)
    valor = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='string')
    descricao = models.CharField(max_length=200, blank=True)
    
    class Meta:
        db_table = 'configuracoes_gerais'
        verbose_name = 'Configuração Geral'
        verbose_name_plural = 'Configurações Gerais'
    
    def __str__(self):
        return self.chave
    
    def get_value(self):
        if self.tipo == 'integer':
            return int(self.valor)
        elif self.tipo == 'boolean':
            return self.valor.lower() == 'true'
        elif self.tipo == 'json':
            import json
            return json.loads(self.valor)
        return self.valor
```

## Migrations e Seeds

### Dados Iniciais (fixtures/initial_data.json)

```json
{
  "categorias": [
    {"nome": "Cabos", "slug": "cabos", "ordem": 1},
    {"nome": "Carregadores", "slug": "carregadores", "ordem": 2},
    {"nome": "Fones", "slug": "fones", "ordem": 3},
    {"nome": "Capas", "slug": "capas", "ordem": 4},
    {"nome": "Películas", "slug": "peliculas", "ordem": 5},
    {"nome": "Suportes", "slug": "suportes", "ordem": 6},
    {"nome": "Powerbanks", "slug": "powerbanks", "ordem": 7}
  ],
  "marcas": [
    {"nome": "Samsung", "ordem": 1},
    {"nome": "Apple", "ordem": 2},
    {"nome": "Motorola", "ordem": 3},
    {"nome": "Xiaomi", "ordem": 4},
    {"nome": "LG", "ordem": 5},
    {"nome": "Asus", "ordem": 6}
  ],
  "configuracoes_webhook": [
    {"evento": "preco_liberado", "url": "", "ativo": true},
    {"evento": "carrinho_abandonado", "url": "", "ativo": true},
    {"evento": "pedido_finalizado", "url": "", "ativo": true}
  ],
  "configuracoes_gerais": [
    {"chave": "tempo_carrinho_abandonado", "valor": "30", "tipo": "integer", "descricao": "Minutos para considerar carrinho abandonado"},
    {"chave": "cookie_duracao_dias", "valor": "7", "tipo": "integer", "descricao": "Dias de duração do cookie"},
    {"chave": "whatsapp_empresa", "valor": "", "tipo": "string", "descricao": "WhatsApp da empresa"}
  ]
}
```

## Índices Recomendados

```python
# Em cada modelo relevante, adicionar:

class Meta:
    indexes = [
        models.Index(fields=['categoria', 'em_estoque']),  # Para Produto
        models.Index(fields=['marca']),  # Para ModeloCelular
        models.Index(fields=['session_id']),  # Para JornadaCliente
        models.Index(fields=['status', '-criado_em']),  # Para Pedido
        models.Index(fields=['whatsapp']),  # Para queries por WhatsApp
    ]
```

## Notas de Performance

1. **Select Related**: Sempre usar para FKs
   ```python
   produtos = ProdutoNormal.objects.select_related('categoria')
   ```

2. **Prefetch Related**: Para relações M2M e reverse FK
   ```python
   pedidos = Pedido.objects.prefetch_related('items__produto')
   ```

3. **Only/Defer**: Para campos específicos
   ```python
   produtos = Produto.objects.only('nome', 'preco_atacado', 'imagem_principal')
   ```

4. **Annotation**: Para cálculos agregados
   ```python
   from django.db.models import Count, Sum
   pedidos = Pedido.objects.annotate(
       total_items=Count('items'),
       valor_total_calc=Sum('items__subtotal')
   )
   ```