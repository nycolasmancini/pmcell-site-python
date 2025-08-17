from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import (
    User, Categoria, ProdutoNormal, ProdutoCapaPelicula, ImagemProduto,
    MarcaCelular, ModeloCelular, PrecoModelo, Pedido, ItemPedido,
    CarrinhoAbandonado, JornadaCliente, ConfiguracaoWebhook, ConfiguracaoGeral
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_vendedor', 'is_staff')
    list_filter = ('is_vendedor', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Configurações PMCELL', {'fields': ('is_vendedor',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Configurações PMCELL', {'fields': ('is_vendedor',)}),
    )


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'slug', 'ativo', 'ordem', 'created_at')
    list_filter = ('ativo', 'created_at')
    search_fields = ('nome', 'descricao')
    prepopulated_fields = {'slug': ('nome',)}
    ordering = ('ordem', 'nome')


class ImagemProdutoInline(admin.TabularInline):
    model = ImagemProduto
    extra = 1
    fields = ('imagem', 'alt_text', 'ordem', 'principal')


@admin.register(ProdutoNormal)
class ProdutoNormalAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'preco_atacado', 'preco_super_atacado', 'em_estoque', 'destaque')
    list_filter = ('categoria', 'em_estoque', 'destaque', 'created_at')
    search_fields = ('nome', 'descricao', 'fabricante')
    prepopulated_fields = {'slug': ('nome',)}
    inlines = [ImagemProdutoInline]
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'slug', 'descricao', 'categoria', 'fabricante', 'caracteristicas')
        }),
        ('Preços', {
            'fields': ('preco_atacado', 'preco_super_atacado', 'quantidade_super_atacado')
        }),
        ('Status', {
            'fields': ('em_estoque', 'destaque')
        }),
    )


class PrecoModeloInline(admin.TabularInline):
    model = PrecoModelo
    extra = 1
    fields = ('modelo', 'preco_atacado', 'preco_super_atacado', 'ativo')


@admin.register(ProdutoCapaPelicula)
class ProdutoCapaPeliculaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'get_range_precos_display', 'em_estoque', 'destaque')
    list_filter = ('categoria', 'em_estoque', 'destaque', 'created_at')
    search_fields = ('nome', 'descricao', 'fabricante')
    prepopulated_fields = {'slug': ('nome',)}
    inlines = [ImagemProdutoInline, PrecoModeloInline]
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'slug', 'descricao', 'categoria', 'fabricante', 'caracteristicas')
        }),
        ('Configurações', {
            'fields': ('quantidade_super_atacado', 'em_estoque', 'destaque')
        }),
    )
    
    def get_range_precos_display(self, obj):
        range_precos = obj.get_range_precos()
        if range_precos:
            return f"R$ {range_precos['atacado']['min']} - R$ {range_precos['atacado']['max']}"
        return "Sem preços"
    get_range_precos_display.short_description = "Range de preços"


@admin.register(MarcaCelular)
class MarcaCelularAdmin(admin.ModelAdmin):
    list_display = ('nome', 'slug', 'ativo', 'ordem')
    list_filter = ('ativo',)
    search_fields = ('nome',)
    prepopulated_fields = {'slug': ('nome',)}
    ordering = ('ordem', 'nome')


@admin.register(ModeloCelular)
class ModeloCelularAdmin(admin.ModelAdmin):
    list_display = ('nome', 'marca', 'slug', 'ativo', 'ordem')
    list_filter = ('marca', 'ativo')
    search_fields = ('nome', 'marca__nome')
    prepopulated_fields = {'slug': ('nome',)}
    ordering = ('marca__nome', 'ordem', 'nome')


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ('preco_unitario', 'preco_total')
    fields = ('tipo', 'produto_normal', 'preco_modelo', 'quantidade', 'preco_unitario', 'preco_total')


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'whatsapp', 'nome_cliente', 'status', 'valor_total', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('codigo', 'whatsapp', 'nome_cliente')
    readonly_fields = ('codigo', 'valor_total', 'created_at', 'updated_at')
    inlines = [ItemPedidoInline]
    fieldsets = (
        ('Informações do Cliente', {
            'fields': ('whatsapp', 'nome_cliente')
        }),
        ('Pedido', {
            'fields': ('codigo', 'status', 'valor_total', 'observacoes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False


@admin.register(CarrinhoAbandonado)
class CarrinhoAbandonadoAdmin(admin.ModelAdmin):
    list_display = ('whatsapp', 'valor_estimado', 'tempo_abandono', 'webhook_enviado', 'created_at')
    list_filter = ('webhook_enviado', 'created_at', 'tempo_abandono')
    search_fields = ('whatsapp',)
    readonly_fields = ('created_at',)
    
    def has_add_permission(self, request):
        return False


@admin.register(JornadaCliente)
class JornadaClienteAdmin(admin.ModelAdmin):
    list_display = ('whatsapp', 'sessao_id', 'evento', 'timestamp')
    list_filter = ('evento', 'timestamp')
    search_fields = ('whatsapp', 'sessao_id')
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)
    
    def has_add_permission(self, request):
        return False


@admin.register(ConfiguracaoWebhook)
class ConfiguracaoWebhookAdmin(admin.ModelAdmin):
    list_display = ('evento', 'url', 'ativo', 'timeout', 'retry_ativo', 'updated_at')
    list_filter = ('ativo', 'retry_ativo', 'evento')
    fields = ('evento', 'url', 'ativo', 'timeout', 'retry_ativo')


@admin.register(ConfiguracaoGeral)
class ConfiguracaoGeralAdmin(admin.ModelAdmin):
    list_display = ('chave', 'valor_preview', 'updated_at')
    search_fields = ('chave', 'valor')
    readonly_fields = ('updated_at',)
    
    def valor_preview(self, obj):
        if len(obj.valor) > 50:
            return obj.valor[:50] + '...'
        return obj.valor
    valor_preview.short_description = "Valor"


# Customizar o admin site
admin.site.site_header = "PMCELL - Administração"
admin.site.site_title = "PMCELL Admin"
admin.site.index_title = "Painel de Controle"
