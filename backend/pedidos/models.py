from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from clientes.models import Cliente
from produtos.models import Produto, ProdutoModelo


class Carrinho(models.Model):
    cliente = models.OneToOneField(Cliente, on_delete=models.CASCADE, related_name='carrinho')
    session_id = models.CharField(max_length=100, blank=True, help_text="Session ID para carrinhos anônimos")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    # Controle de abandono
    finalizado = models.BooleanField(default=False)
    abandonado = models.BooleanField(default=False)
    data_abandono = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Carrinho"
        verbose_name_plural = "Carrinhos"
        ordering = ['-atualizado_em']
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['finalizado', 'abandonado']),
        ]

    def __str__(self):
        return f"Carrinho {self.cliente.nome_display}"

    @property
    def total_itens(self):
        return sum(item.quantidade for item in self.itens.all())

    @property
    def valor_total(self):
        total = Decimal('0.00')
        for item in self.itens.all():
            total += item.valor_total
        return total

    @property
    def quantidade_produtos(self):
        return self.itens.count()


class ItemCarrinho(models.Model):
    carrinho = models.ForeignKey(Carrinho, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    produto_modelo = models.ForeignKey(
        ProdutoModelo, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        help_text="Para produtos tipo capa/película"
    )
    quantidade = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    preco_unitario = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Preço no momento da adição ao carrinho"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Item do Carrinho"
        verbose_name_plural = "Itens do Carrinho"
        unique_together = ['carrinho', 'produto', 'produto_modelo']
        indexes = [
            models.Index(fields=['carrinho', 'produto']),
        ]

    def __str__(self):
        if self.produto_modelo:
            return f"{self.produto.nome} - {self.produto_modelo.modelo} (x{self.quantidade})"
        return f"{self.produto.nome} (x{self.quantidade})"

    @property
    def valor_total(self):
        return self.preco_unitario * self.quantidade

    @property
    def nome_completo(self):
        if self.produto_modelo:
            return f"{self.produto.nome} - {self.produto_modelo.modelo}"
        return self.produto.nome


class Pedido(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('confirmado', 'Confirmado'),
        ('preparando', 'Preparando'),
        ('enviado', 'Enviado'),
        ('entregue', 'Entregue'),
        ('cancelado', 'Cancelado'),
    ]

    # Dados do cliente
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='pedidos')
    nome_cliente = models.CharField(max_length=200)
    whatsapp_cliente = models.CharField(max_length=20)
    
    # Controle do pedido
    numero_pedido = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    
    # Valores
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_final = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Observações
    observacoes = models.TextField(blank=True)
    observacoes_internas = models.TextField(blank=True, help_text="Apenas para equipe")
    
    # Timestamps
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    data_confirmacao = models.DateTimeField(null=True, blank=True)
    data_envio = models.DateTimeField(null=True, blank=True)
    data_entrega = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['numero_pedido']),
            models.Index(fields=['cliente', 'status']),
            models.Index(fields=['status', 'criado_em']),
        ]

    def __str__(self):
        return f"Pedido #{self.numero_pedido} - {self.cliente.nome_display}"

    def save(self, *args, **kwargs):
        if not self.numero_pedido:
            # Gerar número do pedido
            ultimo_numero = Pedido.objects.filter(
                numero_pedido__startswith=f"PMC{self.criado_em.year}"
            ).count()
            self.numero_pedido = f"PMC{self.criado_em.year}{ultimo_numero + 1:04d}"
        super().save(*args, **kwargs)

    @property
    def total_itens(self):
        return sum(item.quantidade for item in self.itens.all())


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    produto_modelo = models.ForeignKey(ProdutoModelo, on_delete=models.CASCADE, null=True, blank=True)
    
    # Dados no momento do pedido (congelados)
    nome_produto = models.CharField(max_length=200)
    nome_modelo = models.CharField(max_length=100, blank=True)
    quantidade = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Item do Pedido"
        verbose_name_plural = "Itens do Pedido"
        indexes = [
            models.Index(fields=['pedido', 'produto']),
        ]

    def __str__(self):
        if self.nome_modelo:
            return f"{self.nome_produto} - {self.nome_modelo} (x{self.quantidade})"
        return f"{self.nome_produto} (x{self.quantidade})"

    def save(self, *args, **kwargs):
        # Calcular subtotal
        self.subtotal = self.preco_unitario * self.quantidade
        super().save(*args, **kwargs)
