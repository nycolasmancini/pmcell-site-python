// Tipos para o catálogo PMCELL

export interface Categoria {
  id: number;
  nome: string;
  descricao: string;
  icone: string;
  ativa: boolean;
  criado_em: string;
  atualizado_em: string;
}

export interface Fabricante {
  id: number;
  nome: string;
  logo?: string;
  site?: string;
  ativo: boolean;
  criado_em: string;
}

export interface MarcaCelular {
  id: number;
  nome: string;
  logo?: string;
  ativa: boolean;
  ordem: number;
  criado_em: string;
}

export interface ModeloCelular {
  id: number;
  nome: string;
  marca: MarcaCelular;
  ativo: boolean;
  ordem: number;
  criado_em: string;
}

export interface ProdutoModelo {
  id: number;
  produto: number;
  modelo: ModeloCelular;
  preco_atacado: string;
  preco_super_atacado: string;
  disponivel: boolean;
  estoque: number;
  criado_em: string;
  atualizado_em: string;
}

export interface Produto {
  id: number;
  nome: string;
  descricao: string;
  caracteristicas: string;
  categoria: Categoria;
  fabricante: Fabricante;
  tipo: 'acessorio' | 'capa_pelicula';
  preco_atacado?: string;
  preco_super_atacado?: string;
  quantidade_super_atacado?: number;
  imagem_principal?: string;
  imagem_2?: string;
  imagem_3?: string;
  ativo: boolean;
  destaque: boolean;
  estoque: number;
  peso?: string;
  criado_em: string;
  atualizado_em: string;
  modelos_precos?: ProdutoModelo[];
  imagens: string[];
}

export interface Cliente {
  id: number;
  nome: string;
  whatsapp_principal: string;
  whatsapp_secundario?: string;
  precos_liberados: boolean;
  data_liberacao_precos?: string;
  empresa?: string;
  cnpj?: string;
  cidade?: string;
  estado?: string;
  ativo: boolean;
  criado_em: string;
  atualizado_em: string;
  total_pedidos: number;
  valor_total_compras: string;
  ultima_compra?: string;
}

export interface ItemCarrinho {
  id: number;
  produto: Produto;
  produto_modelo?: ProdutoModelo;
  quantidade: number;
  preco_unitario: string;
  criado_em: string;
  atualizado_em: string;
}

export interface Carrinho {
  id: number;
  cliente: Cliente;
  session_id?: string;
  criado_em: string;
  atualizado_em: string;
  finalizado: boolean;
  abandonado: boolean;
  data_abandono?: string;
  itens: ItemCarrinho[];
  total_itens: number;
  valor_total: string;
  quantidade_produtos: number;
}

export interface Pedido {
  id: number;
  cliente: Cliente;
  nome_cliente: string;
  whatsapp_cliente: string;
  numero_pedido: string;
  status: 'pendente' | 'confirmado' | 'preparando' | 'enviado' | 'entregue' | 'cancelado';
  subtotal: string;
  desconto: string;
  total_final: string;
  observacoes?: string;
  observacoes_internas?: string;
  criado_em: string;
  atualizado_em: string;
  data_confirmacao?: string;
  data_envio?: string;
  data_entrega?: string;
  itens: ItemPedido[];
  total_itens: number;
}

export interface ItemPedido {
  id: number;
  produto: Produto;
  produto_modelo?: ProdutoModelo;
  nome_produto: string;
  nome_modelo?: string;
  quantidade: number;
  preco_unitario: string;
  subtotal: string;
  criado_em: string;
}

// Tipos para formulários e estados

export interface WhatsAppForm {
  whatsapp: string;
}

export interface CheckoutForm {
  nome: string;
  whatsapp_confirmacao: string;
  observacoes?: string;
}

export interface FiltrosProdutos {
  categoria?: number;
  fabricante?: number;
  tipo?: 'acessorio' | 'capa_pelicula';
  busca?: string;
  apenas_destaque?: boolean;
  apenas_com_estoque?: boolean;
}

export interface PaginacaoResponse<T> {
  count: number;
  next?: string;
  previous?: string;
  results: T[];
}

// Tipos para analytics e tracking

export interface EventoTracking {
  tipo_evento: 'page_view' | 'product_view' | 'search' | 'add_cart' | 'remove_cart' | 
              'checkout_start' | 'checkout_complete' | 'price_unlock' | 'filter_use' | 'model_view';
  pagina?: string;
  termo_busca?: string;
  object_id?: number;
  dados_extras?: Record<string, any>;
}

// Tipos para API responses

export interface ApiError {
  detail?: string;
  message?: string;
  errors?: Record<string, string[]>;
}

export interface ApiResponse<T> {
  data?: T;
  error?: ApiError;
  success: boolean;
}