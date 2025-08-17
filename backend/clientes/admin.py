from django.contrib import admin
from django.utils.html import format_html
from .models import Cliente, SessaoCliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = [
        'nome_display', 'whatsapp_principal', 'precos_liberados',
        'total_pedidos', 'valor_total_compras', 'ultima_compra', 'ativo'
    ]
    list_filter = [
        'precos_liberados', 'ativo', 'estado', 
        'data_liberacao_precos', 'criado_em'
    ]
    search_fields = [
        'nome', 'whatsapp_principal', 'whatsapp_secundario',
        'empresa', 'cnpj', 'cidade'
    ]
    list_editable = ['ativo']
    ordering = ['-criado_em']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'whatsapp_principal', 'whatsapp_secundario')
        }),
        ('Controle de Preços', {
            'fields': ('precos_liberados', 'data_liberacao_precos'),
        }),
        ('Informações da Empresa', {
            'fields': ('empresa', 'cnpj', 'cidade', 'estado'),
            'classes': ('collapse',),
        }),
        ('Estatísticas', {
            'fields': ('total_pedidos', 'valor_total_compras', 'ultima_compra'),
            'classes': ('collapse',),
        }),
        ('Controle', {
            'fields': ('ativo',),
        }),
    )
    
    readonly_fields = [
        'data_liberacao_precos', 'total_pedidos', 
        'valor_total_compras', 'ultima_compra'
    ]
    
    def nome_display(self, obj):
        if obj.nome:
            return f"{obj.nome} ({obj.whatsapp_principal})"
        return obj.whatsapp_principal
    nome_display.short_description = 'Cliente'
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('pedidos')


@admin.register(SessaoCliente)
class SessaoClienteAdmin(admin.ModelAdmin):
    list_display = [
        'cliente', 'session_id_short', 'ip_address', 
        'ativa', 'paginas_visitadas', 'produtos_visualizados',
        'tempo_total_minutos', 'iniciada_em'
    ]
    list_filter = [
        'ativa', 'iniciada_em', 'finalizada_em'
    ]
    search_fields = [
        'cliente__nome', 'cliente__whatsapp_principal',
        'session_id', 'ip_address'
    ]
    ordering = ['-iniciada_em']
    
    readonly_fields = [
        'session_id', 'ip_address', 'user_agent',
        'iniciada_em', 'ultima_atividade'
    ]
    
    def session_id_short(self, obj):
        return obj.session_id[:12] + '...' if len(obj.session_id) > 12 else obj.session_id
    session_id_short.short_description = 'Session ID'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('cliente')
