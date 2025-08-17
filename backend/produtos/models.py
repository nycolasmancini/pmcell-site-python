from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)
    icone = models.CharField(max_length=50, blank=True, help_text="Nome do ícone para UI")
    ativa = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Fabricante(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='fabricantes/', blank=True, null=True)
    site = models.URLField(blank=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Fabricante"
        verbose_name_plural = "Fabricantes"
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Produto(models.Model):
    TIPO_CHOICES = [
        ('acessorio', 'Acessório'),
        ('capa_pelicula', 'Capa/Película'),
    ]

    nome = models.CharField(max_length=200)
    descricao = models.TextField()
    caracteristicas = models.TextField(help_text="Características técnicas do produto")
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='produtos')
    fabricante = models.ForeignKey(Fabricante, on_delete=models.CASCADE, related_name='produtos')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    
    # Preços para produtos tipo 'acessorio'
    preco_atacado = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        null=True, 
        blank=True
    )
    preco_super_atacado = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        null=True, 
        blank=True
    )
    quantidade_super_atacado = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Quantidade mínima para preço super atacado"
    )
    
    # Imagens
    imagem_principal = models.ImageField(upload_to='produtos/', blank=True, null=True)
    imagem_2 = models.ImageField(upload_to='produtos/', blank=True, null=True)
    imagem_3 = models.ImageField(upload_to='produtos/', blank=True, null=True)
    
    # Controle
    ativo = models.BooleanField(default=True)
    destaque = models.BooleanField(default=False)
    estoque = models.PositiveIntegerField(default=0)
    peso = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True, help_text="Peso em kg")
    
    # Timestamps
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['tipo', 'ativo']),
            models.Index(fields=['categoria', 'ativo']),
            models.Index(fields=['fabricante', 'ativo']),
        ]

    def __str__(self):
        return f"{self.nome} - {self.fabricante.nome}"

    def get_preco(self, quantidade=1):
        """Retorna o preço baseado na quantidade"""
        if self.tipo == 'acessorio':
            if (self.quantidade_super_atacado and 
                quantidade >= self.quantidade_super_atacado and 
                self.preco_super_atacado):
                return self.preco_super_atacado
            return self.preco_atacado
        return None

    @property
    def imagens(self):
        """Retorna lista de imagens não vazias"""
        imgs = []
        for img in [self.imagem_principal, self.imagem_2, self.imagem_3]:
            if img:
                imgs.append(img)
        return imgs


class MarcaCelular(models.Model):
    """Marcas de celular para capas e películas"""
    nome = models.CharField(max_length=50, unique=True)
    logo = models.ImageField(upload_to='marcas/', blank=True, null=True)
    ativa = models.BooleanField(default=True)
    ordem = models.PositiveIntegerField(default=0, help_text="Ordem de exibição")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Marca de Celular"
        verbose_name_plural = "Marcas de Celular"
        ordering = ['ordem', 'nome']

    def __str__(self):
        return self.nome


class ModeloCelular(models.Model):
    """Modelos específicos de celular"""
    nome = models.CharField(max_length=100)
    marca = models.ForeignKey(MarcaCelular, on_delete=models.CASCADE, related_name='modelos')
    ativo = models.BooleanField(default=True)
    ordem = models.PositiveIntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Modelo de Celular"
        verbose_name_plural = "Modelos de Celular"
        ordering = ['marca__nome', 'ordem', 'nome']
        unique_together = ['nome', 'marca']

    def __str__(self):
        return f"{self.marca.nome} {self.nome}"


class ProdutoModelo(models.Model):
    """Preços específicos por modelo para produtos tipo capa/película"""
    produto = models.ForeignKey(
        Produto, 
        on_delete=models.CASCADE, 
        related_name='modelos_precos',
        limit_choices_to={'tipo': 'capa_pelicula'}
    )
    modelo = models.ForeignKey(ModeloCelular, on_delete=models.CASCADE)
    preco_atacado = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    preco_super_atacado = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    disponivel = models.BooleanField(default=True)
    estoque = models.PositiveIntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Preço por Modelo"
        verbose_name_plural = "Preços por Modelo"
        unique_together = ['produto', 'modelo']
        indexes = [
            models.Index(fields=['produto', 'disponivel']),
            models.Index(fields=['modelo', 'disponivel']),
        ]

    def __str__(self):
        return f"{self.produto.nome} - {self.modelo}"

    def get_preco(self, quantidade=1):
        """Retorna preço baseado na quantidade do produto pai"""
        if (self.produto.quantidade_super_atacado and 
            quantidade >= self.produto.quantidade_super_atacado):
            return self.preco_super_atacado
        return self.preco_atacado
