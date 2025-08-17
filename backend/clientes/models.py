from django.db import models
from django.core.validators import RegexValidator


class Cliente(models.Model):
    nome = models.CharField(max_length=200, blank=True)
    
    # WhatsApp principal (usado para liberar preços)
    whatsapp_principal = models.CharField(
        max_length=20,
        validators=[RegexValidator(r'^\+?55\d{10,11}$', 'Formato: +5511999999999')]
    )
    
    # WhatsApp secundário (confirmação no checkout)
    whatsapp_secundario = models.CharField(
        max_length=20,
        blank=True,
        validators=[RegexValidator(r'^\+?55\d{10,11}$', 'Formato: +5511999999999')]
    )
    
    # Controle de liberação de preços
    precos_liberados = models.BooleanField(default=False)
    data_liberacao_precos = models.DateTimeField(null=True, blank=True)
    
    # Informações adicionais
    empresa = models.CharField(max_length=200, blank=True)
    cnpj = models.CharField(max_length=18, blank=True)
    cidade = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=2, blank=True)
    
    # Controle
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    # Estatísticas
    total_pedidos = models.PositiveIntegerField(default=0)
    valor_total_compras = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ultima_compra = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['whatsapp_principal']),
            models.Index(fields=['precos_liberados', 'ativo']),
        ]

    def __str__(self):
        if self.nome:
            return f"{self.nome} ({self.whatsapp_principal})"
        return self.whatsapp_principal

    @property
    def nome_display(self):
        """Nome para exibição, usa WhatsApp se nome vazio"""
        return self.nome if self.nome else self.whatsapp_principal


class SessaoCliente(models.Model):
    """Controla sessões de clientes e tracking"""
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='sessoes')
    session_id = models.CharField(max_length=100, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    
    # Controle de tempo
    iniciada_em = models.DateTimeField(auto_now_add=True)
    ultima_atividade = models.DateTimeField(auto_now=True)
    finalizada_em = models.DateTimeField(null=True, blank=True)
    ativa = models.BooleanField(default=True)
    
    # Estatísticas da sessão
    paginas_visitadas = models.PositiveIntegerField(default=0)
    produtos_visualizados = models.PositiveIntegerField(default=0)
    tempo_total_minutos = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Sessão de Cliente"
        verbose_name_plural = "Sessões de Cliente"
        ordering = ['-iniciada_em']
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['cliente', 'ativa']),
        ]

    def __str__(self):
        return f"Sessão {self.cliente} - {self.iniciada_em.strftime('%d/%m/%Y %H:%M')}"
