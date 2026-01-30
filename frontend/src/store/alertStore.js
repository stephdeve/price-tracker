import { create } from 'zustand';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const useAlertStore = create((set, get) => ({
    alerts: [],
    loading: false,
    error: null,

    // Récupérer toutes les alertes de l'utilisateur
    fetchAlerts: async () => {
        set({ loading: true, error: null });
        try {
            const token = localStorage.getItem('access_token');
            const response = await axios.get(`${API_URL}/alerts`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            set({ alerts: response.data, loading: false });
        } catch (error) {
            set({ error: error.response?.data?.detail || 'Erreur de chargement', loading: false });
        }
    },

    // Créer une nouvelle alerte
    createAlert: async (alertData) => {
        set({ loading: true, error: null });
        try {
            const token = localStorage.getItem('access_token');
            const response = await axios.post(`${API_URL}/alerts`, alertData, {
                headers: { Authorization: `Bearer ${token}` }
            });
            set((state) => ({
                alerts: [...state.alerts, response.data],
                loading: false
            }));
            return response.data;
        } catch (error) {
            set({ error: error.response?.data?.detail || 'Erreur de création', loading: false });
            throw error;
        }
    },

    // Mettre à jour une alerte
    updateAlert: async (alertId, alertData) => {
        set({ loading: true, error: null });
        try {
            const token = localStorage.getItem('access_token');
            const response = await axios.put(`${API_URL}/alerts/${alertId}`, alertData, {
                headers: { Authorization: `Bearer ${token}` }
            });
            set((state) => ({
                alerts: state.alerts.map(a => a.id === alertId ? response.data : a),
                loading: false
            }));
            return response.data;
        } catch (error) {
            set({ error: error.response?.data?.detail || 'Erreur de mise à jour', loading: false });
            throw error;
        }
    },

    // Supprimer une alerte
    deleteAlert: async (alertId) => {
        set({ loading: true, error: null });
        try {
            const token = localStorage.getItem('access_token');
            await axios.delete(`${API_URL}/alerts/${alertId}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            set((state) => ({
                alerts: state.alerts.filter(a => a.id !== alertId),
                loading: false
            }));
        } catch (error) {
            set({ error: error.response?.data?.detail || 'Erreur de suppression', loading: false });
            throw error;
        }
    },

    // Tester une notification
    testAlert: async (alertId) => {
        try {
            const token = localStorage.getItem('access_token');
            const response = await axios.post(`${API_URL}/alerts/${alertId}/test`, {}, {
                headers: { Authorization: `Bearer ${token}` }
            });
            return response.data;
        } catch (error) {
            set({ error: error.response?.data?.detail || 'Erreur du test' });
            throw error;
        }
    }
}));
