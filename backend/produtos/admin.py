from django.contrib import admin
from django.utils.html import format_html
from .models import Categoria, Fabricante, Produto, MarcaCelular, ModeloCelular, ProdutoModelo


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ativa', 'total_produtos', 'criado_em']
    list_filter = ['ativa', 'criado_em']
    search_fields = ['nome', 'descricao']
    list_editable = ['ativa']
    ordering = ['nome']
    
    def total_produtos(self, obj):
        return obj.produtos.filter(ativo=True).count()
    total_produtos.short_description = 'Produtos Ativos'


@admin.register(Fabricante)
class FabricanteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ativo', 'total_produtos', 'site', 'criado_em']
    list_filter = ['ativo', 'criado_em']
    search_fields = ['nome']
    list_editable = ['ativo']
    ordering = ['nome']
    
    def total_produtos(self, obj):
        return obj.produtos.filter(ativo=True).count()
    total_produtos.short_description = 'Produtos Ativos'


class ProdutoModeloInline(admin.TabularInline):
    model = ProdutoModelo
    extra = 0
    fields = ['modelo', 'preco_atacado', 'preco_super_atacado', 'disponivel', 'estoque']
    readonly_fields = ['criado_em']


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = [
        'nome', 'fabricante', 'categoria', 'tipo', 
        'preco_display', 'estoque', 'ativo', 'destaque'
    ]
    list_filter = [
        'tipo', 'ativo', 'destaque', 'categoria', 
        'fabricante', 'criado_em'
    ]
    search_fields = ['nome', 'descricao', 'caracteristicas']
    list_editable = ['ativo', 'destaque', 'estoque']
    ordering = ['-criado_em']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'caracteristicas', 'categoria', 'fabricante', 'tipo')
        }),
        ('Preços (apenas para Acessórios)', {
            'fields': ('preco_atacado', 'preco_super_atacado', 'quantidade_super_atacado'),
            'classes': ('collapse',),
        }),
        ('Imagens', {
            'fields': ('imagem_principal', 'imagem_2', 'imagem_3'),
        }),
        ('Controle', {
            'fields': ('ativo', 'destaque', 'estoque', 'peso'),
        }),
    )
    
    inlines = []
    
    def get_inlines(self, request, obj):
        if obj and obj.tipo == 'capa_pelicula':
            return [ProdutoModeloInline]
        return []
    
    def preco_display(self, obj):
        if obj.tipo == 'acessorio' and obj.preco_atacado:
            return f"R$ {obj.preco_atacado}"
        elif obj.tipo == 'capa_pelicula':
            modelos_count = obj.modelos_precos.count()
            return f"{modelos_count} modelos" if modelos_count > 0 else "Sem modelos"
        return "-"
    preco_display.short_description = 'Preço/Modelos'


@admin.register(MarcaCelular)
class MarcaCelularAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ativa', 'ordem', 'total_modelos', 'criado_em']
    list_filter = ['ativa', 'criado_em']
    search_fields = ['nome']
    list_editable = ['ativa', 'ordem']
    ordering = ['ordem', 'nome']
    
    def total_modelos(self, obj):
        return obj.modelos.filter(ativo=True).count()
    total_modelos.short_description = 'Modelos Ativos'


@admin.register(ModeloCelular)
class ModeloCelularAdmin(admin.ModelAdmin):
    list_display = ['nome', 'marca', 'ativo', 'ordem', 'criado_em']
    list_filter = ['marca', 'ativo', 'criado_em']
    search_fields = ['nome', 'marca__nome']
    list_editable = ['ativo', 'ordem']
    ordering = ['marca__nome', 'ordem', 'nome']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('marca')


@admin.register(ProdutoModelo)
class ProdutoModeloAdmin(admin.ModelAdmin):
    list_display = [
        'produto', 'modelo', 'preco_atacado', 
        'preco_super_atacado', 'disponivel', 'estoque'
    ]
    list_filter = [
        'disponivel', 'produto__categoria', 
        'modelo__marca', 'criado_em'
    ]
    search_fields = [
        'produto__nome', 'modelo__nome', 
        'modelo__marca__nome'
    ]
    list_editable = ['disponivel', 'estoque']
    ordering = ['produto__nome', 'modelo__marca__nome', 'modelo__nome']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'produto', 'modelo', 'modelo__marca'
        )
