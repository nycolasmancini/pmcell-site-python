from django.contrib import admin
from django.utils.html import format_html
from .models import EventoTracking, JornadaCliente, ProdutoAnalytics, RelatorioSemanal


@admin.register(EventoTracking)
class EventoTrackingAdmin(admin.ModelAdmin):
    list_display = [
        'tipo_evento', 'cliente_info', 'pagina', 
        'objeto_relacionado', 'criado_em'
    ]
    list_filter = [
        'tipo_evento', 'criado_em', 'content_type'
    ]
    search_fields = [
        'cliente__nome', 'cliente__whatsapp_principal',
        'session_id', 'pagina', 'termo_busca'
    ]
    ordering = ['-criado_em']
    
    readonly_fields = [
        'cliente', 'session_id', 'tipo_evento', 'pagina',
        'termo_busca', 'content_object', 'ip_address',
        'user_agent', 'referrer', 'dados_extras', 'criado_em'
    ]
    
    def cliente_info(self, obj):
        if obj.cliente:
            return obj.cliente.nome_display
        return obj.session_id[:12] + '...'
    cliente_info.short_description = 'Cliente/Sessão'
    
    def objeto_relacionado(self, obj):
        if obj.content_object:
            return str(obj.content_object)
        return '-'
    objeto_relacionado.short_description = 'Objeto'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(JornadaCliente)
class JornadaClienteAdmin(admin.ModelAdmin):
    list_display = [
        'cliente', 'status_jornada', 'paginas_visitadas',
        'produtos_visualizados', 'itens_carrinho',
        'tempo_total_sessao', 'valor_pedido'
    ]
    list_filter = [
        'converteu_pedido', 'ativa', 'iniciada_em', 'finalizada_em'
    ]
    search_fields = [
        'cliente__nome', 'cliente__whatsapp_principal', 'session_id'
    ]
    ordering = ['-iniciada_em']
    
    readonly_fields = [
        'session_id', 'primeira_pagina', 'ultima_pagina',
        'iniciada_em', 'finalizada_em'
    ]
    
    def status_jornada(self, obj):
        if obj.converteu_pedido:
            return format_html('<span style="color: green;">✓ Convertida</span>')
        elif obj.ativa:
            return format_html('<span style="color: blue;">● Ativa</span>')
        else:
            return format_html('<span style="color: red;">✗ Abandonada</span>')
    status_jornada.short_description = 'Status'
    
    def has_add_permission(self, request):
        return False


@admin.register(ProdutoAnalytics)
class ProdutoAnalyticsAdmin(admin.ModelAdmin):
    list_display = [
        'produto', 'total_visualizacoes', 'total_adicoes_carrinho',
        'total_vendas', 'taxa_conversao_carrinho', 'taxa_conversao_venda'
    ]
    list_filter = [
        'produto__categoria', 'produto__fabricante', 'atualizado_em'
    ]
    search_fields = [
        'produto__nome', 'produto__categoria__nome', 'produto__fabricante__nome'
    ]
    ordering = ['-total_visualizacoes']
    
    readonly_fields = [
        'produto', 'total_visualizacoes', 'visualizacoes_mes_atual',
        'visualizacoes_semana_atual', 'total_adicoes_carrinho',
        'total_remocoes_carrinho', 'total_vendas', 'valor_total_vendas',
        'taxa_conversao_carrinho', 'taxa_conversao_venda', 'atualizado_em'
    ]
    
    actions = ['recalcular_taxas_conversao']
    
    def recalcular_taxas_conversao(self, request, queryset):
        for analytics in queryset:
            analytics.calcular_taxas_conversao()
        self.message_user(request, f'Taxas recalculadas para {queryset.count()} produtos.')
    recalcular_taxas_conversao.short_description = 'Recalcular taxas de conversão'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(RelatorioSemanal)
class RelatorioSemanalAdmin(admin.ModelAdmin):
    list_display = [
        'semana_ano', 'total_visitantes', 'total_sessoes',
        'total_pedidos', 'valor_total_pedidos', 'taxa_conversao',
        'criado_em'
    ]
    list_filter = ['ano', 'criado_em']
    ordering = ['-ano', '-semana']
    
    readonly_fields = [
        'ano', 'semana', 'total_visitantes', 'total_sessoes',
        'total_page_views', 'produtos_mais_vistos', 'termos_mais_buscados',
        'total_carrinhos_criados', 'total_carrinhos_abandonados',
        'total_pedidos', 'valor_total_pedidos', 'tempo_medio_sessao',
        'criado_em'
    ]
    
    def semana_ano(self, obj):
        return f"Semana {obj.semana}/{obj.ano}"
    semana_ano.short_description = 'Período'
    
    def taxa_conversao(self, obj):
        if obj.total_carrinhos_criados > 0:
            taxa = (obj.total_pedidos / obj.total_carrinhos_criados) * 100
            return f"{taxa:.1f}%"
        return "0%"
    taxa_conversao.short_description = 'Conversão'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
