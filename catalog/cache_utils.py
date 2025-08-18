"""
Cache utilities for catalog app
"""

from django.core.cache import cache
from django.conf import settings
from .models import Categoria, ProdutoNormal, ProdutoCapaPelicula


def get_cached_categories():
    """
    Get categories from cache or database
    """
    cache_key = 'categories_active'
    categories = cache.get(cache_key)
    
    if categories is None:
        categories = list(Categoria.objects.filter(ativo=True).order_by('nome'))
        cache.set(cache_key, categories, settings.CACHE_TIMEOUT_CATEGORIES)
    
    return categories


def get_cached_product_count():
    """
    Get total product count from cache
    """
    cache_key = 'product_count_total'
    count = cache.get(cache_key)
    
    if count is None:
        normal_count = ProdutoNormal.objects.filter(em_estoque=True).count()
        capa_count = ProdutoCapaPelicula.objects.filter(em_estoque=True).count()
        count = normal_count + capa_count
        cache.set(cache_key, count, settings.CACHE_TIMEOUT_PRODUCTS)
    
    return count


def get_cached_search_suggestions(query):
    """
    Get search suggestions from cache
    """
    cache_key = f'search_suggestions_{query.lower()}'
    suggestions = cache.get(cache_key)
    
    if suggestions is None:
        from .views import _get_search_suggestions
        suggestions = _get_search_suggestions(query)
        cache.set(cache_key, suggestions, settings.CACHE_TIMEOUT_SEARCH)
    
    return suggestions


def invalidate_product_cache():
    """
    Invalidate product-related cache when products are modified
    """
    cache.delete('categories_active')
    cache.delete('product_count_total')
    
    # Clear search suggestion cache
    from django.core.cache.utils import make_template_fragment_key
    cache.delete_many([k for k in cache._cache.keys() if k.startswith('search_suggestions_')])


def invalidate_category_cache():
    """
    Invalidate category cache when categories are modified
    """
    cache.delete('categories_active')


class CacheInvalidationMixin:
    """
    Mixin to add cache invalidation to model admin
    """
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if hasattr(obj, '_meta'):
            model_name = obj._meta.model_name
            if model_name in ['categoria']:
                invalidate_category_cache()
            elif model_name in ['produtonormal', 'produtocapapelicula']:
                invalidate_product_cache()
    
    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        if hasattr(obj, '_meta'):
            model_name = obj._meta.model_name
            if model_name in ['categoria']:
                invalidate_category_cache()
            elif model_name in ['produtonormal', 'produtocapapelicula']:
                invalidate_product_cache()