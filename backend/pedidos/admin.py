from django.contrib import admin
from django.utils.html import format_html
from .models import Carrinho, ItemCarrinho, Pedido, ItemPedido


class ItemCarrinhoInline(admin.TabularInline):
    model = ItemCarrinho
    extra = 0
    readonly_fields = ['preco_unitario', 'criado_em']
    fields = ['produto', 'produto_modelo', 'quantidade', 'preco_unitario']


@admin.register(Carrinho)
class CarrinhoAdmin(admin.ModelAdmin):
    list_display = [
        'cliente', 'total_itens', 'valor_total',
        'finalizado', 'abandonado', 'atualizado_em'
    ]
    list_filter = [
        'finalizado', 'abandonado', 'criado_em', 'atualizado_em'
    ]
    search_fields = [
        'cliente__nome', 'cliente__whatsapp_principal', 'session_id'
    ]
    ordering = ['-atualizado_em']
    
    inlines = [ItemCarrinhoInline]
    
    readonly_fields = [
        'session_id', 'criado_em', 'total_itens', 
        'valor_total', 'quantidade_produtos'
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('cliente').prefetch_related('itens')


@admin.register(ItemCarrinho)
class ItemCarrinhoAdmin(admin.ModelAdmin):
    list_display = [
        'carrinho', 'produto', 'produto_modelo', 
        'quantidade', 'preco_unitario', 'valor_total'
    ]
    list_filter = [
        'carrinho__finalizado', 'produto__categoria', 'criado_em'
    ]
    search_fields = [
        'carrinho__cliente__nome', 'produto__nome', 
        'produto_modelo__modelo__nome'
    ]
    ordering = ['-criado_em']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'carrinho', 'carrinho__cliente', 'produto', 
            'produto_modelo', 'produto_modelo__modelo'
        )


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = [
        'nome_produto', 'nome_modelo', 'preco_unitario', 
        'subtotal', 'criado_em'
    ]
    fields = [
        'produto', 'produto_modelo', 'nome_produto', 
        'nome_modelo', 'quantidade', 'preco_unitario', 'subtotal'
    ]


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = [
        'numero_pedido', 'cliente', 'status', 
        'total_itens', 'total_final', 'criado_em'
    ]
    list_filter = [
        'status', 'criado_em', 'data_confirmacao', 
        'data_envio', 'data_entrega'
    ]
    search_fields = [
        'numero_pedido', 'cliente__nome', 
        'cliente__whatsapp_principal', 'nome_cliente'
    ]
    ordering = ['-criado_em']
    
    fieldsets = (
        ('Informações do Pedido', {
            'fields': ('numero_pedido', 'status', 'cliente')
        }),
        ('Dados do Cliente', {
            'fields': ('nome_cliente', 'whatsapp_cliente')
        }),
        ('Valores', {
            'fields': ('subtotal', 'desconto', 'total_final')
        }),
        ('Observações', {
            'fields': ('observacoes', 'observacoes_internas'),
            'classes': ('collapse',),
        }),
        ('Datas', {
            'fields': (
                'criado_em', 'data_confirmacao', 
                'data_envio', 'data_entrega'
            ),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = [
        'numero_pedido', 'criado_em', 'total_itens'
    ]
    
    inlines = [ItemPedidoInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('cliente').prefetch_related('itens')
    
    actions = ['marcar_como_confirmado', 'marcar_como_enviado']
    
    def marcar_como_confirmado(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status='pendente').update(
            status='confirmado',
            data_confirmacao=timezone.now()
        )
        self.message_user(request, f'{updated} pedidos marcados como confirmados.')
    marcar_como_confirmado.short_description = 'Marcar como confirmado'
    
    def marcar_como_enviado(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status='confirmado').update(
            status='enviado',
            data_envio=timezone.now()
        )
        self.message_user(request, f'{updated} pedidos marcados como enviados.')
    marcar_como_enviado.short_description = 'Marcar como enviado'


@admin.register(ItemPedido)
class ItemPedidoAdmin(admin.ModelAdmin):
    list_display = [
        'pedido', 'nome_produto', 'nome_modelo', 
        'quantidade', 'preco_unitario', 'subtotal'
    ]
    list_filter = [
        'pedido__status', 'criado_em'
    ]
    search_fields = [
        'pedido__numero_pedido', 'nome_produto', 'nome_modelo'
    ]
    ordering = ['-criado_em']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('pedido')
