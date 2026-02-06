import { useEffect, useState } from 'react';
import { useAlertStore } from '../store/alertStore';
import { useProductStore } from '../store/productStore';
import { BellIcon, PlusIcon, PencilIcon, TrashIcon, CheckIcon, XMarkIcon, PaperAirplaneIcon } from '@heroicons/react/24/outline';

export default function AlertsPage() {
    const { alerts, fetchAlerts, createAlert, updateAlert, deleteAlert, testAlert, loading } = useAlertStore();
    const { trackedProducts, fetchTrackedProducts } = useProductStore();

    const [showForm, setShowForm] = useState(false);
    const [editingAlert, setEditingAlert] = useState(null);
    const [filter, setFilter] = useState('all'); // all, active, inactive
    const [testingAlertId, setTestingAlertId] = useState(null);

    const [formData, setFormData] = useState({
        product_id: '',
        alert_type: 'target_price',
        threshold_value: '',
        notification_channel: 'email'
    });

    useEffect(() => {
        fetchAlerts();
        fetchTrackedProducts();
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            if (editingAlert) {
                await updateAlert(editingAlert.id, formData);
            } else {
                await createAlert({
                    ...formData,
                    threshold_value: parseFloat(formData.threshold_value)
                });
            }
            resetForm();
        } catch (error) {
            alert('Erreur: ' + error.message);
        }
    };

    const resetForm = () => {
        setFormData({
            product_id: '',
            alert_type: 'target_price',
            threshold_value: '',
            notification_channel: 'email'
        });
        setEditingAlert(null);
        setShowForm(false);
    };

    const handleEdit = (alert) => {
        setFormData({
            product_id: alert.product_id,
            alert_type: alert.alert_type,
            threshold_value: alert.threshold_value?.toString() || '',
            notification_channel: alert.notification_channel
        });
        setEditingAlert(alert);
        setShowForm(true);
    };

    const handleDelete = async (alertId) => {
        if (confirm('Supprimer cette alerte ?')) {
            try {
                await deleteAlert(alertId);
            } catch (error) {
                alert('Erreur de suppression');
            }
        }
    };

    const handleToggleActive = async (alert) => {
        try {
            await updateAlert(alert.id, {
                ...alert,
                is_active: !alert.is_active
            });
        } catch (error) {
            alert('Erreur de mise à jour');
        }
    };

    const handleTest = async (alertId) => {
        setTestingAlertId(alertId);
        try {
            const result = await testAlert(alertId);
            alert('Notification de test envoyée!\n' + result.message);
        } catch (error) {
            alert(' Échec du test: ' + error.message);
        } finally {
            setTestingAlertId(null);
        }
    };

    const filteredAlerts = alerts.filter(alert => {
        if (filter === 'active') return alert.is_active;
        if (filter === 'inactive') return !alert.is_active;
        return true;
    });

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex justify-between items-center mb-8">
                <h1 className="text-3xl font-bold flex items-center gap-2">
                    <BellIcon className="h-8 w-8" />
                    Mes Alertes
                </h1>
                <button
                    onClick={() => setShowForm(!showForm)}
                    className="btn-primary flex items-center gap-2"
                >
                    <PlusIcon className="h-5 w-5" />
                    {showForm ? 'Annuler' : 'Nouvelle Alerte'}
                </button>
            </div>

            {/* Formulaire de création/modification */}
            {showForm && (
                <div className="card mb-8">
                    <h2 className="text-xl font-bold mb-4">
                        {editingAlert ? 'Modifier l\'alerte' : 'Créer une alerte'}
                    </h2>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Produit
                            </label>
                            <select
                                className="input"
                                value={formData.product_id}
                                onChange={(e) => setFormData({ ...formData, product_id: e.target.value })}
                                required
                            >
                                <option value="">Sélectionner un produit</option>
                                {trackedProducts.map(product => (
                                    <option key={product.id} value={product.id}>
                                        {product.name}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Type d'alerte
                            </label>
                            <select
                                className="input"
                                value={formData.alert_type}
                                onChange={(e) => setFormData({ ...formData, alert_type: e.target.value })}
                                required
                            >
                                <option value="target_price">Prix cible</option>
                                <option value="percentage_drop">Baisse en %</option>
                                <option value="availability">Disponibilité</option>
                            </select>
                        </div>

                        {formData.alert_type !== 'availability' && (
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Seuil {formData.alert_type === 'target_price' ? '(FCFA)' : '(%)'}
                                </label>
                                <input
                                    type="number"
                                    className="input"
                                    value={formData.threshold_value}
                                    onChange={(e) => setFormData({ ...formData, threshold_value: e.target.value })}
                                    placeholder={formData.alert_type === 'target_price' ? 'Ex: 50000' : 'Ex: 20'}
                                    required
                                />
                            </div>
                        )}

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Canal de notification
                            </label>
                            <select
                                className="input"
                                value={formData.notification_channel}
                                onChange={(e) => setFormData({ ...formData, notification_channel: e.target.value })}
                                required
                            >
                                <option value="email">Email</option>
                                <option value="telegram">Telegram</option>
                                <option value="whatsapp">WhatsApp</option>
                                <option value="sms">SMS</option>
                            </select>
                        </div>

                        <div className="flex gap-3">
                            <button type="submit" className="btn-primary" disabled={loading}>
                                {loading ? 'Enregistrement...' : (editingAlert ? 'Mettre à jour' : 'Créer')}
                            </button>
                            <button
                                type="button"
                                onClick={resetForm}
                                className="btn-secondary"
                            >
                                Annuler
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {/* Filtres */}
            <div className="flex gap-2 mb-6">
                <button
                    onClick={() => setFilter('all')}
                    className={`px-4 py-2 rounded-lg font-medium ${filter === 'all' ? 'bg-primary-500 text-white' : 'bg-gray-200 text-gray-700'
                        }`}
                >
                    Toutes ({alerts.length})
                </button>
                <button
                    onClick={() => setFilter('active')}
                    className={`px-4 py-2 rounded-lg font-medium ${filter === 'active' ? 'bg-green-500 text-white' : 'bg-gray-200 text-gray-700'
                        }`}
                >
                    Actives ({alerts.filter(a => a.is_active).length})
                </button>
                <button
                    onClick={() => setFilter('inactive')}
                    className={`px-4 py-2 rounded-lg font-medium ${filter === 'inactive' ? 'bg-gray-500 text-white' : 'bg-gray-200 text-gray-700'
                        }`}
                >
                    Inactives ({alerts.filter(a => !a.is_active).length})
                </button>
            </div>

            {/* Liste des alertes */}
            {filteredAlerts.length > 0 ? (
                <div className="space-y-4">
                    {filteredAlerts.map(alert => (
                        <div key={alert.id} className="card hover:shadow-md transition-shadow">
                            <div className="flex items-start justify-between">
                                <div className="flex-1">
                                    <div className="flex items-center gap-3 mb-2">
                                        <h3 className="font-bold text-lg">
                                            {alert.alert_type === 'target_price' && ' Prix Cible'}
                                            {alert.alert_type === 'percentage_drop' && ' Baisse %'}
                                            {alert.alert_type === 'availability' && ' Disponibilité'}
                                        </h3>
                                        <span className={`badge ${alert.is_active ? 'badge-success' : 'bg-gray-200 text-gray-700'}`}>
                                            {alert.is_active ? 'Active' : 'Inactive'}
                                        </span>
                                        <span className="badge bg-blue-100 text-blue-800">
                                            {alert.notification_channel}
                                        </span>
                                    </div>
                                    <p className="text-gray-600 mb-1">
                                        Produit ID: {alert.product_id}
                                    </p>
                                    {alert.threshold_value && (
                                        <p className="text-sm text-gray-500">
                                            Seuil: {alert.threshold_value}
                                            {alert.alert_type === 'target_price' ? ' FCFA' : '%'}
                                        </p>
                                    )}
                                </div>

                                {/* Actions */}
                                <div className="flex gap-2">
                                    <button
                                        onClick={() => handleToggleActive(alert)}
                                        className="p-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors"
                                        title={alert.is_active ? 'Désactiver' : 'Activer'}
                                    >
                                        {alert.is_active ? <XMarkIcon className="h-5 w-5 text-red-600" /> : <CheckIcon className="h-5 w-5 text-green-600" />}
                                    </button>
                                    <button
                                        onClick={() => handleTest(alert.id)}
                                        disabled={testingAlertId === alert.id}
                                        className="p-2 rounded-lg bg-blue-100 hover:bg-blue-200 transition-colors"
                                        title="Tester la notification"
                                    >
                                        <PaperAirplaneIcon className="h-5 w-5 text-blue-600" />
                                    </button>
                                    <button
                                        onClick={() => handleEdit(alert)}
                                        className="p-2 rounded-lg bg-yellow-100 hover:bg-yellow-200 transition-colors"
                                        title="Modifier"
                                    >
                                        <PencilIcon className="h-5 w-5 text-yellow-600" />
                                    </button>
                                    <button
                                        onClick={() => handleDelete(alert.id)}
                                        className="p-2 rounded-lg bg-red-100 hover:bg-red-200 transition-colors"
                                        title="Supprimer"
                                    >
                                        <TrashIcon className="h-5 w-5 text-red-600" />
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <div className="card text-center py-12">
                    <BellIcon className="h-20 w-20 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-gray-700 mb-2">
                        {filter === 'all' ? 'Aucune alerte configurée' : `Aucune alerte ${filter === 'active' ? 'active' : 'inactive'}`}
                    </h3>
                    <p className="text-gray-500 mb-4">
                        Créez une alerte pour être notifié des changements de prix
                    </p>
                    {filter !== 'all' && (
                        <button onClick={() => setFilter('all')} className="btn-outline">
                            Voir toutes les alertes
                        </button>
                    )}
                </div>
            )}
        </div>
    );
}
