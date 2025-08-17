import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Cliente, Carrinho, FiltrosProdutos } from '@/types';

interface AppState {
  // Cliente
  cliente: Cliente | null;
  precosLiberados: boolean;
  
  // Carrinho
  carrinho: Carrinho | null;
  
  // Filtros
  filtros: FiltrosProdutos;
  
  // UI State
  modalWhatsAppAberto: boolean;
  modalCarrinhoAberto: boolean;
  modalModelosAberto: boolean;
  produtoSelecionado: number | null;
  
  // Busca
  termoBusca: string;
  
  // Session
  sessionId: string;
}

interface AppActions {
  // Cliente
  setCliente: (cliente: Cliente | null) => void;
  setPrecosLiberados: (liberados: boolean) => void;
  
  // Carrinho
  setCarrinho: (carrinho: Carrinho | null) => void;
  
  // Filtros
  setFiltros: (filtros: Partial<FiltrosProdutos>) => void;
  limparFiltros: () => void;
  
  // UI
  abrirModalWhatsApp: () => void;
  fecharModalWhatsApp: () => void;
  abrirModalCarrinho: () => void;
  fecharModalCarrinho: () => void;
  abrirModalModelos: (produtoId: number) => void;
  fecharModalModelos: () => void;
  
  // Busca
  setTermoBusca: (termo: string) => void;
  
  // Session
  setSessionId: (id: string) => void;
  
  // Reset
  reset: () => void;
}

const initialState: AppState = {
  cliente: null,
  precosLiberados: false,
  carrinho: null,
  filtros: {},
  modalWhatsAppAberto: false,
  modalCarrinhoAberto: false,
  modalModelosAberto: false,
  produtoSelecionado: null,
  termoBusca: '',
  sessionId: '',
};

export const useAppStore = create<AppState & AppActions>()(
  persist(
    (set, get) => ({
      ...initialState,
      
      // Cliente
      setCliente: (cliente) => set({ cliente }),
      setPrecosLiberados: (liberados) => set({ precosLiberados: liberados }),
      
      // Carrinho
      setCarrinho: (carrinho) => set({ carrinho }),
      
      // Filtros
      setFiltros: (novosFiltros) => 
        set((state) => ({ 
          filtros: { ...state.filtros, ...novosFiltros } 
        })),
      
      limparFiltros: () => set({ filtros: {} }),
      
      // UI
      abrirModalWhatsApp: () => set({ modalWhatsAppAberto: true }),
      fecharModalWhatsApp: () => set({ modalWhatsAppAberto: false }),
      
      abrirModalCarrinho: () => set({ modalCarrinhoAberto: true }),
      fecharModalCarrinho: () => set({ modalCarrinhoAberto: false }),
      
      abrirModalModelos: (produtoId) => 
        set({ 
          modalModelosAberto: true, 
          produtoSelecionado: produtoId 
        }),
      
      fecharModalModelos: () => 
        set({ 
          modalModelosAberto: false, 
          produtoSelecionado: null 
        }),
      
      // Busca
      setTermoBusca: (termo) => set({ termoBusca: termo }),
      
      // Session
      setSessionId: (id) => set({ sessionId: id }),
      
      // Reset
      reset: () => set(initialState),
    }),
    {
      name: 'pmcell-app-store',
      partialize: (state) => ({
        cliente: state.cliente,
        precosLiberados: state.precosLiberados,
        sessionId: state.sessionId,
        termoBusca: state.termoBusca,
        filtros: state.filtros,
      }),
    }
  )
);