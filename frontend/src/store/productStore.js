import { create } from 'zustand';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const useProductStore = create((set, get) => ({
    products: [],
    trackedProducts: [],
    priceDrops: [],
    loading: false,
    error: null,

    // Récupérer tous les produits
    fetchProducts: async () => {
        set({ loading: true, error: null });
        try {
            const token = localStorage.getItem('access_token');
            const response = await axios.get(`${API_URL}/products`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            set({ products: response.data, loading: false });
        } catch (error) {
            set({ error: error.response?.data?.detail || 'Erreur de chargement', loading: false });
        }
    },

    // Récupérer les produits suivis par l'utilisateur
    fetchTrackedProducts: async () => {
        set({ loading: true, error: null });
        try {
            const token = localStorage.getItem('access_token');
            const response = await axios.get(`${API_URL}/products/tracked`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            set({ trackedProducts: response.data, loading: false });
        } catch (error) {
            set({ error: error.response?.data?.detail || 'Erreur de chargement', loading: false });
        }
    },

    // Suivre un produit
    trackProduct: async (productId) => {
        try {
            const token = localStorage.getItem('access_token');
            await axios.post(`${API_URL}/products/${productId}/track`, {}, {
                headers: { Authorization: `Bearer ${token}` }
            });
            // Rafraîchir la liste
            get().fetchTrackedProducts();
        } catch (error) {
            set({ error: error.response?.data?.detail || 'Erreur lors du suivi' });
        }
    },

    // Ne plus suivre un produit
    untrackProduct: async (productId) => {
        try {
            const token = localStorage.getItem('access_token');
            await axios.delete(`${API_URL}/products/${productId}/track`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            // Rafraîchir la liste
            get().fetchTrackedProducts();
        } catch (error) {
            set({ error: error.response?.data?.detail || 'Erreur lors de l\'arrêt du suivi' });
        }
    },

    // Récupérer l'historique de prix d'un produit
    fetchPriceHistory: async (productId) => {
        try {
            const token = localStorage.getItem('access_token');
            const response = await axios.get(`${API_URL}/products/${productId}/history`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            return response.data;
        } catch (error) {
            set({ error: error.response?.data?.detail || 'Erreur de chargement historique' });
            return [];
        }
    },

    // Récupérer les baisses de prix
    fetchPriceDrops: async (params = {}) => {
        set({ loading: true, error: null });
        try {
            const token = localStorage.getItem('access_token');
            const query = new URLSearchParams(params).toString();
            const response = await axios.get(`${API_URL}/products/price-drops${query ? `?${query}` : ''}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            set({ priceDrops: response.data, loading: false });
            return response.data;
        } catch (error) {
            set({ error: error.response?.data?.detail || 'Erreur de chargement des baisses de prix', loading: false });
            return [];
        }
    },

    // Récupérer un produit
    fetchProductById: async (productId) => {
        try {
            const token = localStorage.getItem('access_token');
            const response = await axios.get(`${API_URL}/products/${productId}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            return response.data;
        } catch (error) {
            set({ error: error.response?.data?.detail || 'Erreur de chargement du produit' });
            return null;
        }
    },

    // Récupérer le groupe de comparaison
    fetchComparisonGroup: async (productId) => {
        try {
            const token = localStorage.getItem('access_token');
            const response = await axios.get(`${API_URL}/products/${productId}/compare`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            return response.data;
        } catch (error) {
            set({ error: error.response?.data?.detail || 'Erreur de comparaison' });
            return null;
        }
    }
}));
