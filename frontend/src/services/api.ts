import axios from 'axios';
import type { 
  Produto, 
  Categoria, 
  Fabricante, 
  MarcaCelular, 
  ModeloCelular,
  Cliente,
  Carrinho,
  Pedido,
  PaginacaoResponse,
  FiltrosProdutos,
  WhatsAppForm,
  CheckoutForm,
  EventoTracking
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para adicionar session_id
api.interceptors.request.use((config) => {
  const sessionId = localStorage.getItem('session_id') || 
                   Math.random().toString(36).substring(2, 15);
  
  if (!localStorage.getItem('session_id')) {
    localStorage.setItem('session_id', sessionId);
  }
  
  config.headers['X-Session-ID'] = sessionId;
  return config;
});

// Interceptor para tratamento de erros
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// PRODUTOS
export const produtosApi = {
  listar: (filtros: FiltrosProdutos = {}, page = 1) => {
    const params = new URLSearchParams();
    
    if (filtros.categoria) params.append('categoria', filtros.categoria.toString());
    if (filtros.fabricante) params.append('fabricante', filtros.fabricante.toString());
    if (filtros.tipo) params.append('tipo', filtros.tipo);
    if (filtros.busca) params.append('search', filtros.busca);
    if (filtros.apenas_destaque) params.append('destaque', 'true');
    if (filtros.apenas_com_estoque) params.append('com_estoque', 'true');
    
    params.append('page', page.toString());
    
    return api.get<PaginacaoResponse<Produto>>(`/produtos/?${params.toString()}`);
  },

  buscar: (id: number) =>
    api.get<Produto>(`/produtos/${id}/`),

  buscarModelos: (produtoId: number) =>
    api.get<MarcaCelular[]>(`/produtos/${produtoId}/marcas/`),

  buscarModelosPorMarca: (produtoId: number, marcaId: number) =>
    api.get<ModeloCelular[]>(`/produtos/${produtoId}/marcas/${marcaId}/modelos/`),
};

// CATEGORIAS
export const categoriasApi = {
  listar: () =>
    api.get<Categoria[]>('/categorias/'),

  buscar: (id: number) =>
    api.get<Categoria>(`/categorias/${id}/`),
};

// FABRICANTES
export const fabricantesApi = {
  listar: () =>
    api.get<Fabricante[]>('/fabricantes/'),

  buscar: (id: number) =>
    api.get<Fabricante>(`/fabricantes/${id}/`),
};

// CLIENTES
export const clientesApi = {
  liberarPrecos: (data: WhatsAppForm) =>
    api.post<{ success: boolean; cliente: Cliente }>('/clientes/liberar-precos/', data),

  buscarPorSession: () =>
    api.get<Cliente>('/clientes/me/'),
};

// CARRINHO
export const carrinhoApi = {
  buscar: () =>
    api.get<Carrinho>('/carrinho/'),

  adicionarItem: (data: {
    produto_id: number;
    produto_modelo_id?: number;
    quantidade: number;
  }) =>
    api.post<{ success: boolean; item: any }>('/carrinho/adicionar/', data),

  atualizarItem: (itemId: number, data: { quantidade: number }) =>
    api.patch<{ success: boolean }>(`/carrinho/itens/${itemId}/`, data),

  removerItem: (itemId: number) =>
    api.delete<{ success: boolean }>(`/carrinho/itens/${itemId}/`),

  limpar: () =>
    api.delete<{ success: boolean }>('/carrinho/limpar/'),
};

// PEDIDOS
export const pedidosApi = {
  criar: (data: CheckoutForm) =>
    api.post<{ success: boolean; pedido: Pedido }>('/pedidos/', data),

  listar: () =>
    api.get<PaginacaoResponse<Pedido>>('/pedidos/'),

  buscar: (id: number) =>
    api.get<Pedido>(`/pedidos/${id}/`),
};

// ANALYTICS
export const analyticsApi = {
  registrarEvento: (evento: EventoTracking) =>
    api.post<{ success: boolean }>('/analytics/evento/', evento),
};

// WEBHOOK
export const webhookApi = {
  whatsapp: (data: any) =>
    api.post('/webhook/whatsapp/', data),
};

export default api;