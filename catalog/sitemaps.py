"""
Sitemaps for PMCELL catalog
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Categoria, ProdutoNormal, ProdutoCapaPelicula


class StaticViewSitemap(Sitemap):
    """Sitemap for static views"""
    priority = 0.8
    changefreq = 'daily'

    def items(self):
        return ['catalog:home', 'catalog:cart']

    def location(self, item):
        return reverse(item)


class CategorySitemap(Sitemap):
    """Sitemap for categories"""
    priority = 0.7
    changefreq = 'weekly'

    def items(self):
        return Categoria.objects.filter(ativo=True)

    def location(self, obj):
        return f"/?category={obj.slug}"

    def lastmod(self, obj):
        return obj.updated_at


class ProductSitemap(Sitemap):
    """Sitemap for products"""
    priority = 0.6
    changefreq = 'daily'
    limit = 1000

    def items(self):
        # Get both normal products and capa/pelicula products
        normal_products = [(p, 'normal') for p in ProdutoNormal.objects.filter(em_estoque=True)]
        capa_products = [(p, 'capa_pelicula') for p in ProdutoCapaPelicula.objects.filter(em_estoque=True)]
        return normal_products + capa_products

    def location(self, item):
        product, product_type = item
        return reverse('catalog:product_detail', kwargs={
            'product_id': product.id,
            'product_type': product_type
        })

    def lastmod(self, item):
        product, product_type = item
        return product.updated_at


# Sitemap dictionary
sitemaps = {
    'static': StaticViewSitemap,
    'categories': CategorySitemap,
    'products': ProductSitemap,
}