import json
import logging
import requests
from django.utils import timezone
from datetime import timedelta
from .models import ConfiguracaoWebhook

logger = logging.getLogger(__name__)


class WebhookSender:
    """
    Utility class for sending webhooks with retry mechanism
    """
    
    @staticmethod
    def send_webhook(evento, data, retry_count=0):
        """
        Send webhook for a specific event
        
        Args:
            evento (str): Event type (liberacao_preco, carrinho_abandonado, pedido_finalizado)
            data (dict): Data to send in webhook
            retry_count (int): Current retry attempt (0 = first attempt)
        
        Returns:
            bool: True if successful, False if failed
        """
        try:
            # Get webhook configuration for this event
            webhook_config = ConfiguracaoWebhook.objects.filter(
                evento=evento,
                ativo=True
            ).first()
            
            if not webhook_config or not webhook_config.url:
                logger.info(f"No webhook configured for event: {evento}")
                return True  # Not an error if no webhook is configured
            
            # Prepare webhook payload
            payload = {
                'evento': evento,
                'timestamp': timezone.now().isoformat(),
                'retry_count': retry_count,
                **data
            }
            
            # Send webhook request
            response = requests.post(
                webhook_config.url,
                json=payload,
                timeout=webhook_config.timeout,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'PMCELL-Webhook/1.0'
                }
            )
            
            # Check if request was successful
            if response.status_code >= 200 and response.status_code < 300:
                logger.info(f"Webhook sent successfully for event: {evento}")
                return True
            else:
                logger.error(f"Webhook failed with status {response.status_code} for event: {evento}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error(f"Webhook timeout for event: {evento}")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Webhook request error for event {evento}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending webhook for event {evento}: {str(e)}")
            return False
    
    @staticmethod
    def send_webhook_with_retry(evento, data):
        """
        Send webhook with automatic retry mechanism
        
        Args:
            evento (str): Event type
            data (dict): Data to send
        
        Returns:
            bool: True if successful (either on first try or retry), False if all attempts failed
        """
        # First attempt
        success = WebhookSender.send_webhook(evento, data, retry_count=0)
        
        if success:
            return True
        
        # Check if retry is enabled for this event
        webhook_config = ConfiguracaoWebhook.objects.filter(
            evento=evento,
            ativo=True
        ).first()
        
        if not webhook_config or not webhook_config.retry_ativo:
            logger.info(f"Retry disabled for event: {evento}")
            return False
        
        # Wait a bit and retry
        import time
        time.sleep(5)  # Wait 5 seconds before retry
        
        logger.info(f"Retrying webhook for event: {evento}")
        success = WebhookSender.send_webhook(evento, data, retry_count=1)
        
        if success:
            logger.info(f"Webhook retry successful for event: {evento}")
        else:
            logger.error(f"Webhook retry failed for event: {evento}")
        
        return success


def send_price_liberation_webhook(whatsapp, timestamp=None):
    """
    Send webhook for price liberation event
    """
    data = {
        'whatsapp': whatsapp,
        'liberation_timestamp': timestamp or timezone.now().isoformat(),
    }
    
    return WebhookSender.send_webhook_with_retry('liberacao_preco', data)


def send_abandoned_cart_webhook(whatsapp, cart_data, estimated_value, abandonment_time=None):
    """
    Send webhook for abandoned cart event
    """
    data = {
        'whatsapp': whatsapp,
        'cart_data': cart_data,
        'estimated_value': float(estimated_value),
        'abandonment_time': abandonment_time or timezone.now().isoformat(),
        'items_count': len(cart_data) if cart_data else 0,
    }
    
    return WebhookSender.send_webhook_with_retry('carrinho_abandonado', data)


def send_order_completed_webhook(pedido):
    """
    Send webhook for completed order event
    """
    # Get order items
    items = []
    for item in pedido.itens.all():
        if item.tipo == 'normal':
            items.append({
                'type': 'normal',
                'product_id': item.produto_normal.id,
                'product_name': item.produto_normal.nome,
                'quantity': item.quantidade,
                'unit_price': float(item.preco_unitario),
                'total_price': float(item.preco_total),
            })
        elif item.tipo == 'modelo':
            items.append({
                'type': 'modelo',
                'product_id': item.preco_modelo.produto.id,
                'product_name': item.preco_modelo.produto.nome,
                'model_id': item.preco_modelo.modelo.id,
                'model_name': f"{item.preco_modelo.modelo.marca.nome} {item.preco_modelo.modelo.nome}",
                'quantity': item.quantidade,
                'unit_price': float(item.preco_unitario),
                'total_price': float(item.preco_total),
            })
    
    data = {
        'order': {
            'codigo': pedido.codigo,
            'whatsapp': pedido.whatsapp,
            'nome_cliente': pedido.nome_cliente,
            'valor_total': float(pedido.valor_total),
            'status': pedido.status,
            'created_at': pedido.created_at.isoformat(),
            'items': items,
            'items_count': len(items),
        }
    }
    
    return WebhookSender.send_webhook_with_retry('pedido_finalizado', data)