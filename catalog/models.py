from django.db import models
from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField
from django.core.validators import RegexValidator
from django.utils import timezone
import uuid


class User(AbstractUser):
    is_vendedor = models.BooleanField(default=False, verbose_name="É vendedor")
    
    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"


class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    ordem = models.PositiveIntegerField(default=0, verbose_name="Ordem")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    
    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['ordem', 'nome']
    
    def __str__(self):
        return self.nome


class Produto(models.Model):
    TIPO_CHOICES = [
        ('normal', 'Produto Normal'),
        ('capa_pelicula', 'Capa/Película'),
    ]
    
    nome = models.CharField(max_length=200, verbose_name="Nome")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    descricao = models.TextField(verbose_name="Descrição")
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, verbose_name="Categoria")
    fabricante = models.CharField(max_length=100, blank=True, verbose_name="Fabricante")
    caracteristicas = models.TextField(blank=True, verbose_name="Características")
    
    em_estoque = models.BooleanField(default=True, verbose_name="Em estoque")
    destaque = models.BooleanField(default=False, verbose_name="Produto em destaque")
    
    quantidade_super_atacado = models.PositiveIntegerField(
        default=10, 
        verbose_name="Quantidade mínima para super atacado"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['-created_at']
        abstract = True
    
    def __str__(self):
        return self.nome


class ProdutoNormal(Produto):
    preco_atacado = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Preço atacado"
    )
    preco_super_atacado = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Preço super atacado"
    )
    
    class Meta:
        verbose_name = "Produto Normal"
        verbose_name_plural = "Produtos Normais"
    
    def calcular_preco(self, quantidade):
        if quantidade >= self.quantidade_super_atacado:
            return self.preco_super_atacado
        return self.preco_atacado


class ProdutoCapaPelicula(Produto):
    
    class Meta:
        verbose_name = "Produto Capa/Película"
        verbose_name_plural = "Produtos Capa/Película"
    
    def get_range_precos(self):
        precos = self.precomodelo_set.all().values_list('preco_atacado', 'preco_super_atacado')
        if not precos:
            return None, None
        
        atacado_min = min(p[0] for p in precos)
        atacado_max = max(p[0] for p in precos)
        super_min = min(p[1] for p in precos)
        super_max = max(p[1] for p in precos)
        
        return {
            'atacado': {'min': atacado_min, 'max': atacado_max},
            'super_atacado': {'min': super_min, 'max': super_max}
        }


class ImagemProduto(models.Model):
    produto_normal = models.ForeignKey(
        ProdutoNormal, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='imagens'
    )
    produto_capa = models.ForeignKey(
        ProdutoCapaPelicula, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='imagens'
    )
    
    imagem = CloudinaryField(verbose_name="Imagem")
    alt_text = models.CharField(max_length=200, blank=True, verbose_name="Texto alternativo")
    ordem = models.PositiveIntegerField(default=0, verbose_name="Ordem")
    principal = models.BooleanField(default=False, verbose_name="Imagem principal")
    
    class Meta:
        verbose_name = "Imagem do Produto"
        verbose_name_plural = "Imagens dos Produtos"
        ordering = ['ordem']
    
    def __str__(self):
        produto = self.produto_normal or self.produto_capa
        return f"Imagem de {produto.nome if produto else 'N/A'}"


class MarcaCelular(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    ordem = models.PositiveIntegerField(default=0, verbose_name="Ordem")
    
    class Meta:
        verbose_name = "Marca de Celular"
        verbose_name_plural = "Marcas de Celular"
        ordering = ['ordem', 'nome']
    
    def __str__(self):
        return self.nome


class ModeloCelular(models.Model):
    marca = models.ForeignKey(MarcaCelular, on_delete=models.CASCADE, verbose_name="Marca")
    nome = models.CharField(max_length=100, verbose_name="Nome")
    slug = models.SlugField(verbose_name="Slug")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    ordem = models.PositiveIntegerField(default=0, verbose_name="Ordem")
    
    class Meta:
        verbose_name = "Modelo de Celular"
        verbose_name_plural = "Modelos de Celular"
        ordering = ['ordem', 'nome']
        unique_together = ['marca', 'slug']
    
    def __str__(self):
        return f"{self.marca.nome} {self.nome}"


class PrecoModelo(models.Model):
    produto = models.ForeignKey(ProdutoCapaPelicula, on_delete=models.CASCADE, verbose_name="Produto")
    modelo = models.ForeignKey(ModeloCelular, on_delete=models.CASCADE, verbose_name="Modelo")
    preco_atacado = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Preço atacado"
    )
    preco_super_atacado = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Preço super atacado"
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        verbose_name = "Preço por Modelo"
        verbose_name_plural = "Preços por Modelo"
        unique_together = ['produto', 'modelo']
    
    def __str__(self):
        return f"{self.produto.nome} - {self.modelo}"
    
    def calcular_preco(self, quantidade):
        if quantidade >= self.produto.quantidade_super_atacado:
            return self.preco_super_atacado
        return self.preco_atacado


phone_regex = RegexValidator(
    regex=r'^\(\d{2}\)\s\d{4,5}-\d{4}$',
    message="Formato deve ser: (XX) XXXXX-XXXX ou (XX) XXXX-XXXX"
)


class Pedido(models.Model):
    STATUS_CHOICES = [
        ('aberto', 'Aberto'),
        ('solucionado', 'Solucionado'),
        ('cancelado', 'Cancelado'),
    ]
    
    codigo = models.CharField(max_length=20, unique=True, verbose_name="Código")
    whatsapp = models.CharField(
        max_length=20, 
        validators=[phone_regex], 
        verbose_name="WhatsApp"
    )
    nome_cliente = models.CharField(max_length=200, blank=True, verbose_name="Nome do cliente")
    
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='aberto',
        verbose_name="Status"
    )
    
    valor_total = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        verbose_name="Valor total"
    )
    
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Pedido {self.codigo} - {self.whatsapp}"
    
    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = self.gerar_codigo()
        super().save(*args, **kwargs)
    
    def gerar_codigo(self):
        return f"PM{timezone.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:6].upper()}"


class ItemPedido(models.Model):
    TIPO_CHOICES = [
        ('normal', 'Produto Normal'),
        ('modelo', 'Modelo de Capa/Película'),
    ]
    
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, verbose_name="Tipo")
    
    produto_normal = models.ForeignKey(
        ProdutoNormal, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        verbose_name="Produto Normal"
    )
    preco_modelo = models.ForeignKey(
        PrecoModelo, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        verbose_name="Preço do Modelo"
    )
    
    quantidade = models.PositiveIntegerField(verbose_name="Quantidade")
    preco_unitario = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Preço unitário"
    )
    preco_total = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        verbose_name="Preço total"
    )
    
    class Meta:
        verbose_name = "Item do Pedido"
        verbose_name_plural = "Itens do Pedido"
    
    def __str__(self):
        if self.tipo == 'normal':
            return f"{self.produto_normal.nome} x{self.quantidade}"
        else:
            return f"{self.preco_modelo.produto.nome} ({self.preco_modelo.modelo}) x{self.quantidade}"
    
    def save(self, *args, **kwargs):
        if self.tipo == 'normal' and self.produto_normal:
            self.preco_unitario = self.produto_normal.calcular_preco(self.quantidade)
        elif self.tipo == 'modelo' and self.preco_modelo:
            self.preco_unitario = self.preco_modelo.calcular_preco(self.quantidade)
        
        self.preco_total = self.preco_unitario * self.quantidade
        super().save(*args, **kwargs)


class CarrinhoAbandonado(models.Model):
    whatsapp = models.CharField(
        max_length=20, 
        validators=[phone_regex], 
        verbose_name="WhatsApp"
    )
    dados_carrinho = models.JSONField(verbose_name="Dados do carrinho")
    valor_estimado = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        verbose_name="Valor estimado"
    )
    
    tempo_abandono = models.DateTimeField(verbose_name="Momento do abandono")
    webhook_enviado = models.BooleanField(default=False, verbose_name="Webhook enviado")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    
    class Meta:
        verbose_name = "Carrinho Abandonado"
        verbose_name_plural = "Carrinhos Abandonados"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Carrinho abandonado - {self.whatsapp} - R$ {self.valor_estimado}"


class JornadaCliente(models.Model):
    EVENTO_CHOICES = [
        ('entrada', 'Entrada no site'),
        ('liberacao_preco', 'Liberação de preços'),
        ('categoria_visitada', 'Categoria visitada'),
        ('pesquisa', 'Pesquisa realizada'),
        ('produto_visualizado', 'Produto visualizado'),
        ('item_adicionado', 'Item adicionado ao carrinho'),
        ('item_removido', 'Item removido do carrinho'),
        ('checkout_iniciado', 'Checkout iniciado'),
        ('pedido_finalizado', 'Pedido finalizado'),
        ('saida', 'Saída do site'),
    ]
    
    whatsapp = models.CharField(
        max_length=20, 
        validators=[phone_regex], 
        blank=True,
        verbose_name="WhatsApp"
    )
    sessao_id = models.CharField(max_length=100, verbose_name="ID da sessão")
    
    evento = models.CharField(max_length=20, choices=EVENTO_CHOICES, verbose_name="Evento")
    dados_evento = models.JSONField(blank=True, null=True, verbose_name="Dados do evento")
    
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Timestamp")
    
    class Meta:
        verbose_name = "Jornada do Cliente"
        verbose_name_plural = "Jornadas dos Clientes"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.evento} - {self.whatsapp or self.sessao_id} - {self.timestamp}"


class ConfiguracaoWebhook(models.Model):
    EVENTO_CHOICES = [
        ('liberacao_preco', 'Liberação de preços'),
        ('carrinho_abandonado', 'Carrinho abandonado'),
        ('pedido_finalizado', 'Pedido finalizado'),
    ]
    
    evento = models.CharField(
        max_length=20, 
        choices=EVENTO_CHOICES, 
        unique=True,
        verbose_name="Evento"
    )
    url = models.URLField(verbose_name="URL do webhook")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    timeout = models.PositiveIntegerField(default=30, verbose_name="Timeout (segundos)")
    retry_ativo = models.BooleanField(default=True, verbose_name="Retry ativo")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Configuração de Webhook"
        verbose_name_plural = "Configurações de Webhooks"
    
    def __str__(self):
        return f"Webhook {self.evento}"


class ConfiguracaoGeral(models.Model):
    chave = models.CharField(max_length=100, unique=True, verbose_name="Chave")
    valor = models.TextField(verbose_name="Valor")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Configuração Geral"
        verbose_name_plural = "Configurações Gerais"
    
    def __str__(self):
        return self.chave
