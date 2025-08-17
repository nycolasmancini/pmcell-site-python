from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from clientes.models import Cliente
from produtos.models import Produto


class EventoTracking(models.Model):
    TIPO_EVENTO_CHOICES = [
        ('page_view', 'Visualização de Página'),
        ('product_view', 'Visualização de Produto'),
        ('search', 'Busca'),
        ('add_cart', 'Adicionar ao Carrinho'),
        ('remove_cart', 'Remover do Carrinho'),
        ('checkout_start', 'Início do Checkout'),
        ('checkout_complete', 'Checkout Finalizado'),
        ('price_unlock', 'Liberação de Preços'),
        ('filter_use', 'Uso de Filtro'),
        ('model_view', 'Visualização de Modelos'),
    ]

    # Identificação
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='eventos', null=True, blank=True)
    session_id = models.CharField(max_length=100)
    
    # Evento
    tipo_evento = models.CharField(max_length=30, choices=TIPO_EVENTO_CHOICES)
    pagina = models.CharField(max_length=200, blank=True)
    termo_busca = models.CharField(max_length=200, blank=True)
    
    # Objeto relacionado (produto, categoria, etc)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Dados técnicos
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    
    # Dados adicionais (JSON)
    dados_extras = models.JSONField(default=dict, blank=True)
    
    # Timestamp
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Evento de Tracking"
        verbose_name_plural = "Eventos de Tracking"
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['session_id', 'tipo_evento']),
            models.Index(fields=['cliente', 'tipo_evento']),
            models.Index(fields=['tipo_evento', 'criado_em']),
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        cliente_info = self.cliente.nome_display if self.cliente else self.session_id[:8]
        return f"{self.get_tipo_evento_display()} - {cliente_info}"


class JornadaCliente(models.Model):
    """Agrupamento de eventos por sessão para análise de jornada"""
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='jornadas')
    session_id = models.CharField(max_length=100, unique=True)
    
    # Análise da jornada
    primeira_pagina = models.CharField(max_length=200, blank=True)
    ultima_pagina = models.CharField(max_length=200, blank=True)
    paginas_visitadas = models.PositiveIntegerField(default=0)
    produtos_visualizados = models.PositiveIntegerField(default=0)
    buscas_realizadas = models.PositiveIntegerField(default=0)
    itens_carrinho = models.PositiveIntegerField(default=0)
    
    # Tempos (em minutos)
    tempo_total_sessao = models.PositiveIntegerField(default=0)
    tempo_ate_primeira_busca = models.PositiveIntegerField(null=True, blank=True)
    tempo_ate_carrinho = models.PositiveIntegerField(null=True, blank=True)
    tempo_ate_checkout = models.PositiveIntegerField(null=True, blank=True)
    
    # Conversão
    converteu_pedido = models.BooleanField(default=False)
    valor_pedido = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Controle
    ativa = models.BooleanField(default=True)
    iniciada_em = models.DateTimeField(auto_now_add=True)
    finalizada_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Jornada do Cliente"
        verbose_name_plural = "Jornadas do Cliente"
        ordering = ['-iniciada_em']
        indexes = [
            models.Index(fields=['cliente', 'converteu_pedido']),
            models.Index(fields=['ativa', 'iniciada_em']),
        ]

    def __str__(self):
        status = "Convertida" if self.converteu_pedido else "Ativa" if self.ativa else "Abandonada"
        return f"Jornada {self.cliente.nome_display} - {status}"


class ProdutoAnalytics(models.Model):
    """Estatísticas agregadas por produto"""
    produto = models.OneToOneField(Produto, on_delete=models.CASCADE, related_name='analytics')
    
    # Visualizações
    total_visualizacoes = models.PositiveIntegerField(default=0)
    visualizacoes_mes_atual = models.PositiveIntegerField(default=0)
    visualizacoes_semana_atual = models.PositiveIntegerField(default=0)
    
    # Carrinho
    total_adicoes_carrinho = models.PositiveIntegerField(default=0)
    total_remocoes_carrinho = models.PositiveIntegerField(default=0)
    
    # Conversão
    total_vendas = models.PositiveIntegerField(default=0)
    valor_total_vendas = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Taxa de conversão (calculada)
    taxa_conversao_carrinho = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # %
    taxa_conversao_venda = models.DecimalField(max_digits=5, decimal_places=2, default=0)      # %
    
    # Controle
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Analytics do Produto"
        verbose_name_plural = "Analytics dos Produtos"
        ordering = ['-total_visualizacoes']

    def __str__(self):
        return f"Analytics - {self.produto.nome}"

    def calcular_taxas_conversao(self):
        """Recalcula as taxas de conversão"""
        if self.total_visualizacoes > 0:
            self.taxa_conversao_carrinho = (self.total_adicoes_carrinho / self.total_visualizacoes) * 100
            self.taxa_conversao_venda = (self.total_vendas / self.total_visualizacoes) * 100
        else:
            self.taxa_conversao_carrinho = 0
            self.taxa_conversao_venda = 0
        self.save()


class RelatorioSemanal(models.Model):
    """Relatórios semanais agregados"""
    ano = models.PositiveIntegerField()
    semana = models.PositiveIntegerField()  # 1-52
    
    # Métricas gerais
    total_visitantes = models.PositiveIntegerField(default=0)
    total_sessoes = models.PositiveIntegerField(default=0)
    total_page_views = models.PositiveIntegerField(default=0)
    
    # Produtos
    produtos_mais_vistos = models.JSONField(default=list)  # Lista de IDs e contadores
    termos_mais_buscados = models.JSONField(default=list)
    
    # Conversão
    total_carrinhos_criados = models.PositiveIntegerField(default=0)
    total_carrinhos_abandonados = models.PositiveIntegerField(default=0)
    total_pedidos = models.PositiveIntegerField(default=0)
    valor_total_pedidos = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Tempo médio
    tempo_medio_sessao = models.PositiveIntegerField(default=0)  # minutos
    
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Relatório Semanal"
        verbose_name_plural = "Relatórios Semanais"
        unique_together = ['ano', 'semana']
        ordering = ['-ano', '-semana']

    def __str__(self):
        return f"Relatório Semana {self.semana}/{self.ano}"
