from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/success/', views.checkout_success, name='checkout_success'),
    
    # Product details
    path('product/<int:product_id>/<str:product_type>/', views.product_detail, name='product_detail'),
    
    # HTMX endpoints for capas/películas
    path('product/<int:product_id>/marca/<int:marca_id>/modelos/', 
         views.get_modelos_by_marca, name='get_modelos'),
    
    # API endpoints
    path('api/liberate-prices/', views.liberate_prices, name='liberate_prices'),
    path('api/add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('api/get-cart-items/', views.get_cart_items, name='get_cart_items'),
    path('api/search-suggestions/', views.search_suggestions, name='search_suggestions'),
    path('api/track-journey/', views.track_journey, name='track_journey'),
    path('api/track-abandoned-cart/', views.track_abandoned_cart, name='track_abandoned_cart'),
]