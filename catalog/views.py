from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Min, Max
from django.core.paginator import Paginator
from django.contrib import messages
import json
import re
import uuid

from .models import (
    Categoria, ProdutoNormal, ProdutoCapaPelicula, 
    MarcaCelular, ModeloCelular, PrecoModelo,
    Pedido, ItemPedido, JornadaCliente, ConfiguracaoWebhook
)
from .cache_utils import get_cached_categories, get_cached_search_suggestions


def home(request):
    """
    Homepage with product catalog
    """
    # Get all categories for navigation (cached)
    categories = get_cached_categories()
    
    # Get products based on filters
    search_query = request.GET.get('q', '').strip()
    category_filter = request.GET.get('category', 'all')
    sort_by = request.GET.get('sort', 'name')  # Default sort by name
    
    # Base queryset for normal products (in stock only) - optimized
    produtos_normais = ProdutoNormal.objects.filter(em_estoque=True).select_related(
        'categoria'
    ).prefetch_related('imagens')
    
    # Base queryset for capa/pelicula products (in stock only) - optimized  
    produtos_capas = ProdutoCapaPelicula.objects.filter(em_estoque=True).select_related(
        'categoria'
    ).prefetch_related(
        'imagens',
        'precomodelo_set__modelo__marca'
    )
    
    # Apply search filter
    if search_query:
        # Search filter for normal products
        search_filter_normal = (
            Q(nome__icontains=search_query) |
            Q(descricao__icontains=search_query) |
            Q(categoria__nome__icontains=search_query) |
            Q(fabricante__icontains=search_query)
        )
        produtos_normais = produtos_normais.filter(search_filter_normal)
        
        # Enhanced search filter for capa/película products (includes phone brands/models)
        search_filter_capas = (
            Q(nome__icontains=search_query) |
            Q(descricao__icontains=search_query) |
            Q(categoria__nome__icontains=search_query) |
            Q(fabricante__icontains=search_query) |
            Q(precomodelo__modelo__nome__icontains=search_query) |
            Q(precomodelo__modelo__marca__nome__icontains=search_query)
        )
        produtos_capas = produtos_capas.filter(search_filter_capas).distinct()
    
    # Apply category filter
    if category_filter != 'all':
        produtos_normais = produtos_normais.filter(categoria__slug=category_filter)
        produtos_capas = produtos_capas.filter(categoria__slug=category_filter)
    
    # Combine and order products
    produtos = []
    
    # Add normal products
    for produto in produtos_normais:
        produtos.append({
            'type': 'normal',
            'object': produto,
            'price_range': None,
        })
    
    # Add capa/película products with price ranges (optimized)
    for produto in produtos_capas:
        # Use prefetched data instead of additional query
        precos_models = produto.precomodelo_set.all()
        if precos_models:
            precos_atacado = [p.preco_atacado for p in precos_models]
            precos_super = [p.preco_super_atacado for p in precos_models]
            precos = {
                'min_atacado': min(precos_atacado) if precos_atacado else 0,
                'max_atacado': max(precos_atacado) if precos_atacado else 0,
                'min_super': min(precos_super) if precos_super else 0,
                'max_super': max(precos_super) if precos_super else 0,
            }
        else:
            precos = {'min_atacado': 0, 'max_atacado': 0, 'min_super': 0, 'max_super': 0}
        
        price_range = {
            'min_atacado': precos['min_atacado'] or 0,
            'max_atacado': precos['max_atacado'] or 0,
            'min_super': precos['min_super'] or 0,
            'max_super': precos['max_super'] or 0,
        }
        
        produtos.append({
            'type': 'capa_pelicula',
            'object': produto,
            'price_range': price_range,
        })
    
    # Apply sorting
    if sort_by == 'name':
        produtos.sort(key=lambda x: x['object'].nome)
    elif sort_by == 'name_desc':
        produtos.sort(key=lambda x: x['object'].nome, reverse=True)
    elif sort_by == 'price_asc':
        def get_min_price(item):
            if item['type'] == 'normal':
                return item['object'].preco_atacado
            else:
                return item['price_range']['min_atacado'] or 9999
        produtos.sort(key=get_min_price)
    elif sort_by == 'price_desc':
        def get_min_price(item):
            if item['type'] == 'normal':
                return item['object'].preco_atacado
            else:
                return item['price_range']['min_atacado'] or 0
        produtos.sort(key=get_min_price, reverse=True)
    elif sort_by == 'category':
        produtos.sort(key=lambda x: x['object'].categoria.nome)
    
    # Pagination
    paginator = Paginator(produtos, 20)  # 20 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'categories': categories,
        'page_obj': page_obj,
        'search_query': search_query,
        'category_filter': category_filter,
        'sort_by': sort_by,
        'total_products': paginator.count,
    }
    
    # Return partial template for HTMX requests
    if request.headers.get('HX-Request'):
        return render(request, 'catalog/products_grid.html', context)
    
    return render(request, 'catalog/home.html', context)


def search(request):
    """
    HTMX search endpoint
    """
    return home(request)  # Reuse home logic


def product_detail(request, product_id, product_type):
    """
    Product detail view for normal products
    """
    if product_type == 'normal':
        product = get_object_or_404(ProdutoNormal, id=product_id, em_estoque=True)
        template = 'catalog/product_detail_normal.html'
        context = {'product': product}
        
    elif product_type == 'capa_pelicula':
        product = get_object_or_404(ProdutoCapaPelicula, id=product_id, em_estoque=True)
        
        # Get marcas and modelos for this product (optimized)
        marcas = MarcaCelular.objects.filter(
            modelocelular__precomodelo__produto=product
        ).distinct().order_by('nome').prefetch_related(
            'modelocelular_set__precomodelo_set'
        )
        
        context = {
            'product': product,
            'marcas': marcas,
        }
        template = 'catalog/product_detail_capa.html'
    else:
        return HttpResponse('Invalid product type', status=400)
    
    return render(request, template, context)


def get_modelos_by_marca(request, product_id, marca_id):
    """
    HTMX endpoint to get models for a specific brand
    """
    product = get_object_or_404(ProdutoCapaPelicula, id=product_id, em_estoque=True)
    marca = get_object_or_404(MarcaCelular, id=marca_id)
    
    # Get models for this brand that have prices for this product (optimized)
    modelos = ModeloCelular.objects.filter(
        marca=marca,
        precomodelo__produto=product
    ).select_related('marca').prefetch_related(
        'precomodelo_set'
    ).order_by('nome')
    
    context = {
        'product': product,
        'marca': marca,
        'modelos': modelos,
    }
    
    return render(request, 'catalog/modelos_list.html', context)


def cart(request):
    """
    Shopping cart page
    """
    return render(request, 'catalog/cart.html')


def checkout(request):
    """
    Checkout process
    """
    if request.method == 'POST':
        try:
            # Handle JSON request from AJAX
            if request.content_type == 'application/json':
                import uuid
                from datetime import datetime
                
                data = json.loads(request.body)
                nome_cliente = data.get('nome_cliente', '').strip()
                whatsapp = data.get('whatsapp', '').strip()
                cart_items = data.get('cart_items', [])
                total = data.get('total', 0)
                
                # Validate required fields
                if not whatsapp or not validate_whatsapp(whatsapp):
                    return JsonResponse({'success': False, 'error': 'WhatsApp inválido'}, status=400)
                
                if not cart_items:
                    return JsonResponse({'success': False, 'error': 'Carrinho vazio'}, status=400)
                
                # Generate unique order code
                order_code = f"PM{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
                
                # Create order
                pedido = Pedido.objects.create(
                    codigo=order_code,
                    nome_cliente=nome_cliente or 'Cliente não informado',
                    whatsapp=whatsapp,
                    valor_total=total,
                    status='pendente'
                )
                
                # Create order items
                for item_data in cart_items:
                    # Determine product based on type
                    if item_data['productType'] == 'normal':
                        try:
                            produto = ProdutoNormal.objects.get(id=item_data['productId'])
                            ItemPedido.objects.create(
                                pedido=pedido,
                                produto_normal=produto,
                                quantidade=item_data['quantity'],
                                preco_unitario=item_data['unitPrice'],
                                preco_total=item_data['unitPrice'] * item_data['quantity']
                            )
                        except ProdutoNormal.DoesNotExist:
                            continue
                            
                    elif item_data['productType'] == 'capa_pelicula' and item_data.get('modelId'):
                        try:
                            produto = ProdutoCapaPelicula.objects.get(id=item_data['productId'])
                            modelo = ModeloCelular.objects.get(id=item_data['modelId'])
                            ItemPedido.objects.create(
                                pedido=pedido,
                                produto_capa_pelicula=produto,
                                modelo_celular=modelo,
                                quantidade=item_data['quantity'],
                                preco_unitario=item_data['unitPrice'],
                                preco_total=item_data['unitPrice'] * item_data['quantity']
                            )
                        except (ProdutoCapaPelicula.DoesNotExist, ModeloCelular.DoesNotExist):
                            continue
                
                # Create journey tracking
                JornadaCliente.objects.create(
                    whatsapp=whatsapp,
                    evento='pedido_finalizado',
                    dados_evento={
                        'codigo_pedido': order_code,
                        'valor_total': total,
                        'items_count': len(cart_items),
                        'nome_cliente': nome_cliente
                    }
                )
                
                # Send webhook
                try:
                    from .webhook_utils import send_order_completed_webhook
                    send_order_completed_webhook(pedido)
                except Exception as e:
                    # Log webhook error but don't fail the request
                    print(f"Webhook error: {e}")
                
                return JsonResponse({
                    'success': True,
                    'order_code': order_code,
                    'redirect_url': f'/checkout/success/?order={order_code}'
                })
            
            # Handle traditional form submission (fallback)
            nome_cliente = request.POST.get('nome_cliente', '').strip()
            whatsapp = request.POST.get('whatsapp', '').strip()
            
            # Validate WhatsApp
            if not whatsapp or not validate_whatsapp(whatsapp):
                messages.error(request, 'WhatsApp inválido')
                return render(request, 'catalog/checkout.html')
            
            messages.success(request, 'Pedido registrado com sucesso!')
            return render(request, 'catalog/checkout_success.html')
            
        except Exception as e:
            if request.content_type == 'application/json':
                return JsonResponse({'success': False, 'error': 'Erro interno do servidor'}, status=500)
            else:
                messages.error(request, 'Erro ao processar pedido')
                return render(request, 'catalog/checkout.html')
    
    return render(request, 'catalog/checkout.html')


def checkout_success(request):
    """
    Checkout success page
    """
    order_code = request.GET.get('order')
    pedido = None
    
    if order_code:
        try:
            pedido = Pedido.objects.get(codigo=order_code)
        except Pedido.DoesNotExist:
            pass
    
    context = {
        'order_code': order_code,
        'pedido': pedido,
    }
    
    return render(request, 'catalog/checkout_success.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def liberate_prices(request):
    """
    API endpoint to liberate prices via WhatsApp
    """
    try:
        data = json.loads(request.body)
        whatsapp = data.get('whatsapp', '').strip()
        
        if not validate_whatsapp(whatsapp):
            return JsonResponse({'error': 'WhatsApp inválido'}, status=400)
        
        # Create or update journey tracking
        JornadaCliente.objects.create(
            whatsapp=whatsapp,
            sessao_id=request.session.session_key or str(uuid.uuid4()),
            evento='liberacao_preco',
            dados_evento={'timestamp': data.get('timestamp')}
        )
        
        # Send webhook
        try:
            from .webhook_utils import send_price_liberation_webhook
            send_price_liberation_webhook(whatsapp, data.get('timestamp'))
        except Exception as e:
            # Log webhook error but don't fail the request
            print(f"Webhook error: {e}")
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt  
@require_http_methods(["POST"])
def add_to_cart(request):
    """
    API endpoint to add product to cart and track action
    """
    try:
        data = json.loads(request.body)
        
        # Track the cart addition
        whatsapp = request.COOKIES.get('user_whatsapp', '')
        if whatsapp:
            JornadaCliente.objects.create(
                whatsapp=whatsapp,
                evento='adicionar_carrinho',
                dados_evento=data
            )
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def get_cart_items(request):
    """
    API endpoint to get cart items with full product data
    """
    try:
        data = json.loads(request.body)
        cart_items = data.get('cart', [])
        
        response_items = []
        
        for item in cart_items:
            product_id = item.get('productId')
            product_type = item.get('productType')
            model_id = item.get('modelId')
            quantity = item.get('quantity', 1)
            
            if product_type == 'normal':
                try:
                    product = ProdutoNormal.objects.select_related('categoria').prefetch_related('imagens').get(id=product_id, em_estoque=True)
                    
                    # Calculate pricing based on quantity
                    price_atacado = float(product.preco_atacado)
                    price_super = float(product.preco_super_atacado)
                    is_super_atacado = quantity >= product.quantidade_super_atacado
                    unit_price = price_super if is_super_atacado else price_atacado
                    
                    response_items.append({
                        'key': item.get('key'),
                        'productId': product_id,
                        'productType': product_type,
                        'name': product.nome,
                        'category': product.categoria.nome,
                        'image': product.imagens.filter(principal=True).first().imagem.url if product.imagens.filter(principal=True).exists() else None,
                        'quantity': quantity,
                        'unitPrice': unit_price,
                        'priceAtacado': price_atacado,
                        'priceSuperAtacado': price_super,
                        'isSuperAtacado': is_super_atacado,
                        'minQuantitySuper': product.quantidade_super_atacado,
                        'modelId': None,
                        'modelName': None,
                    })
                except ProdutoNormal.DoesNotExist:
                    continue
                    
            elif product_type == 'capa_pelicula' and model_id:
                try:
                    product = ProdutoCapaPelicula.objects.select_related('categoria').prefetch_related('imagens').get(id=product_id, em_estoque=True)
                    modelo = ModeloCelular.objects.select_related('marca').get(id=model_id)
                    preco_modelo = PrecoModelo.objects.select_related('produto', 'modelo__marca').get(produto=product, modelo=modelo)
                    
                    # Calculate pricing based on quantity
                    price_atacado = float(preco_modelo.preco_atacado)
                    price_super = float(preco_modelo.preco_super_atacado)
                    is_super_atacado = quantity >= product.quantidade_super_atacado
                    unit_price = price_super if is_super_atacado else price_atacado
                    
                    response_items.append({
                        'key': item.get('key'),
                        'productId': product_id,
                        'productType': product_type,
                        'name': product.nome,
                        'category': product.categoria.nome,
                        'image': product.imagens.filter(principal=True).first().imagem.url if product.imagens.filter(principal=True).exists() else None,
                        'quantity': quantity,
                        'unitPrice': unit_price,
                        'priceAtacado': price_atacado,
                        'priceSuperAtacado': price_super,
                        'isSuperAtacado': is_super_atacado,
                        'minQuantitySuper': product.quantidade_super_atacado,
                        'modelId': model_id,
                        'modelName': f"{modelo.marca.nome} {modelo.nome}",
                    })
                except (ProdutoCapaPelicula.DoesNotExist, ModeloCelular.DoesNotExist, PrecoModelo.DoesNotExist):
                    continue
        
        return JsonResponse({'items': response_items})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def track_journey(request):
    """
    API endpoint to track customer journey events
    """
    try:
        data = json.loads(request.body)
        evento = data.get('evento')
        dados_evento = data.get('dados', {})
        sessao_id = data.get('sessao_id', '')
        whatsapp = data.get('whatsapp', '')
        
        # Get WhatsApp from cookie if not provided
        if not whatsapp:
            whatsapp = request.COOKIES.get('user_whatsapp', '')
        
        # Generate session ID if not provided
        if not sessao_id:
            import uuid
            sessao_id = str(uuid.uuid4())
        
        # Create journey entry
        JornadaCliente.objects.create(
            whatsapp=whatsapp,
            sessao_id=sessao_id,
            evento=evento,
            dados_evento=dados_evento
        )
        
        return JsonResponse({'success': True, 'sessao_id': sessao_id})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def track_abandoned_cart(request):
    """
    API endpoint to track abandoned cart
    """
    try:
        data = json.loads(request.body)
        whatsapp = data.get('whatsapp', '')
        cart_data = data.get('cart_data', [])
        estimated_value = data.get('estimated_value', 0)
        
        # Get WhatsApp from cookie if not provided
        if not whatsapp:
            whatsapp = request.COOKIES.get('user_whatsapp', '')
        
        if not whatsapp or not cart_data:
            return JsonResponse({'error': 'WhatsApp and cart data required'}, status=400)
        
        from django.utils import timezone
        from .models import CarrinhoAbandonado
        
        # Check if we already have an abandoned cart for this WhatsApp
        abandoned_cart, created = CarrinhoAbandonado.objects.get_or_create(
            whatsapp=whatsapp,
            webhook_enviado=False,
            defaults={
                'dados_carrinho': cart_data,
                'valor_estimado': estimated_value,
                'tempo_abandono': timezone.now(),
            }
        )
        
        # If not created, update the existing one
        if not created:
            abandoned_cart.dados_carrinho = cart_data
            abandoned_cart.valor_estimado = estimated_value
            abandoned_cart.tempo_abandono = timezone.now()
            abandoned_cart.save()
        
        # Track journey event
        JornadaCliente.objects.create(
            whatsapp=whatsapp,
            sessao_id=data.get('sessao_id', ''),
            evento='carrinho_abandonado',
            dados_evento={
                'items_count': len(cart_data),
                'estimated_value': estimated_value,
                'abandonment_time': timezone.now().isoformat()
            }
        )
        
        # Send webhook
        try:
            from .webhook_utils import send_abandoned_cart_webhook
            send_abandoned_cart_webhook(
                whatsapp, 
                cart_data, 
                estimated_value, 
                timezone.now().isoformat()
            )
        except Exception as e:
            print(f"Webhook error: {e}")
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def _get_search_suggestions(query):
    """
    Internal function to get search suggestions (used by cache)
    """
    suggestions = []
    
    # Add category suggestions
    categories = Categoria.objects.filter(
        nome__icontains=query, 
        ativo=True
    ).values_list('nome', flat=True)[:3]
    for cat in categories:
        suggestions.append({'text': cat, 'type': 'categoria'})
    
    # Add phone brand suggestions for capas/películas
    marcas = MarcaCelular.objects.filter(
        nome__icontains=query
    ).distinct().values_list('nome', flat=True)[:3]
    for marca in marcas:
        suggestions.append({'text': marca, 'type': 'marca'})
    
    # Add product name suggestions
    produtos = list(ProdutoNormal.objects.filter(
        nome__icontains=query,
        em_estoque=True
    ).values_list('nome', flat=True)[:2])
    
    produtos += list(ProdutoCapaPelicula.objects.filter(
        nome__icontains=query,
        em_estoque=True
    ).values_list('nome', flat=True)[:2])
    
    for produto in produtos[:4]:
        suggestions.append({'text': produto, 'type': 'produto'})
    
    return suggestions[:8]


@csrf_exempt
@require_http_methods(["GET"])
def search_suggestions(request):
    """
    API endpoint for search suggestions (cached)
    """
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    suggestions = get_cached_search_suggestions(query)
    return JsonResponse({'suggestions': suggestions})


def validate_whatsapp(whatsapp):
    """
    Validate Brazilian WhatsApp number
    """
    # Remove all non-digits
    digits = re.sub(r'\D', '', whatsapp)
    
    # Should be 10-11 digits
    if len(digits) < 10 or len(digits) > 11:
        return False
    
    # Should start with valid DDD (11-99)
    ddd = int(digits[:2])
    if ddd < 11 or ddd > 99:
        return False
    
    # If 11 digits, 3rd digit should be 9 (mobile)
    if len(digits) == 11 and digits[2] != '9':
        return False
    
    return True


def health_check(request):
    """
    Health check endpoint for Railway deployment
    """
    return JsonResponse({
        'status': 'healthy',
        'timestamp': request.headers.get('x-request-timestamp', ''),
        'service': 'pmcell-catalog'
    })
