/**
 * Authentication Store (Zustand)
 */
import { create } from 'zustand';
import api from '../services/api';
import toast from 'react-hot-toast';

export const useAuthStore = create((set) => ({
    user: null,
    isAuthenticated: false,
    isLoading: true,

    // Initialize auth state from localStorage
    initializeAuth: async () => {
        const token = localStorage.getItem('access_token');
        if (token) {
            try {
                const response = await api.get('/auth/me');
                set({ user: response.data, isAuthenticated: true, isLoading: false });
            } catch (error) {
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                set({ user: null, isAuthenticated: false, isLoading: false });
            }
        } else {
            set({ isLoading: false });
        }
    },

    // Login
    login: async (email, password) => {
        try {
            const formData = new FormData();
            formData.append('username', email);
            formData.append('password', password);

            const response = await api.post('/auth/login', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });

            const { access_token, refresh_token } = response.data;
            localStorage.setItem('access_token', access_token);
            localStorage.setItem('refresh_token', refresh_token);

            // Fetch user data
            const userResponse = await api.get('/auth/me');
            set({ user: userResponse.data, isAuthenticated: true });

            toast.success('Connexion réussie!');
            return true;
        } catch (error) {
            toast.error(error.response?.data?.detail || 'Erreur de connexion');
            return false;
        }
    },

    // Register
    register: async (userData) => {
        try {
            await api.post('/auth/register', userData);
            toast.success('Inscription réussie! Connectez-vous maintenant.');
            return true;
        } catch (error) {
            toast.error(error.response?.data?.detail || 'Erreur d\'inscription');
            return false;
        }
    },

    // Logout
    logout: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        set({ user: null, isAuthenticated: false });
        toast.success('Déconnexion réussie');
    },

    // Update user
    setUser: (user) => set({ user, isAuthenticated: true }),
}));
