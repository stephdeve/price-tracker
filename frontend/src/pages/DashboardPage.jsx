import { useEffect, useState } from 'react';
import { useProductStore } from '../store/productStore';
import { useAlertStore } from '../store/alertStore';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { ShoppingCartIcon, BellIcon, ArrowTrendingDownIcon, PlusIcon } from '@heroicons/react/24/outline';
import { useNavigate } from 'react-router-dom';

export default function DashboardPage() {
    const navigate = useNavigate();
    const { trackedProducts, fetchTrackedProducts, fetchPriceHistory, priceDrops, fetchPriceDrops } = useProductStore();
    const { alerts, fetchAlerts } = useAlertStore();

    const [priceData, setPriceData] = useState([]);
    const [selectedProduct, setSelectedProduct] = useState(null);
    const [stats, setStats] = useState({
        totalProducts: 0,
        activeAlerts: 0,
        savings: 0
    });

    useEffect(() => {
        fetchTrackedProducts();
        fetchAlerts();
        fetchPriceDrops({ window_days: 30, min_drop_pct: 10, sample_limit: 200 });
    }, []);

    useEffect(() => {
        // Calculer les statistiques
        const activeAlertsCount = alerts.filter(a => a.is_active).length;

        // Calculer les économies (différence entre premier prix et prix actuel)
        const totalSavings = trackedProducts.reduce((acc, product) => {
            if (product.price_history && product.price_history.length > 0) {
                const firstPrice = product.price_history[0].price;
                const currentPrice = product.current_price;
                if (firstPrice > currentPrice) {
                    return acc + (firstPrice - currentPrice);
                }
            }
            return acc;
        }, 0);

        setStats({
            totalProducts: trackedProducts.length,
            activeAlerts: activeAlertsCount,
            savings: Math.round(totalSavings)
        });

        // Charger l'historique du premier produit par défaut
        if (trackedProducts.length > 0 && !selectedProduct) {
            loadProductHistory(trackedProducts[0]);
        }
    }, [trackedProducts, alerts]);

    const loadProductHistory = async (product) => {
        setSelectedProduct(product);
        const history = await fetchPriceHistory(product.id);

        // Formater les données pour le graphique
        const formattedData = history.map(h => ({
            date: new Date(h.date || h.scraped_at).toLocaleDateString('fr-FR', {
                day: '2-digit',
                month: 'short'
            }),
            prix: h.price,
            timestamp: new Date(h.date || h.scraped_at).getTime()
        })).sort((a, b) => a.timestamp - b.timestamp);

        setPriceData(formattedData);
    };

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex justify-between items-center mb-8">
                <h1 className="text-3xl font-bold">Dashboard</h1>
                <button
                    onClick={() => navigate('/products')}
                    className="btn-primary flex items-center gap-2"
                >
                    <PlusIcon className="h-5 w-5" />
                    Ajouter un produit
                </button>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="card bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-blue-600 font-medium">Produits Suivis</p>
                            <p className="text-3xl font-bold text-blue-900 mt-1">{stats.totalProducts}</p>
                        </div>
                        <div className="bg-blue-500 p-3 rounded-full">
                            <ShoppingCartIcon className="h-8 w-8 text-white" />
                        </div>
                    </div>
                </div>

                <div className="card bg-gradient-to-br from-green-50 to-green-100 border-green-200">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-green-600 font-medium">Alertes Actives</p>
                            <p className="text-3xl font-bold text-green-900 mt-1">{stats.activeAlerts}</p>
                        </div>
                        <div className="bg-green-500 p-3 rounded-full">
                            <BellIcon className="h-8 w-8 text-white" />
                        </div>
                    </div>
                </div>

                <div className="card bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-purple-600 font-medium">Économies Estimées</p>
                            <p className="text-3xl font-bold text-purple-900 mt-1">{stats.savings} <span className="text-lg">FCFA</span></p>
                        </div>
                        <div className="bg-purple-500 p-3 rounded-full">
                            <ArrowTrendingDownIcon className="h-8 w-8 text-white" />
                        </div>
                    </div>
                </div>
            </div>

            {/* Graphique de Prix */}
            {trackedProducts.length > 0 ? (
                <div className="card mb-8">
                    <h2 className="text-xl font-bold mb-4">Évolution des Prix</h2>

                    {/* Sélecteur de produit */}
                    <div className="mb-4">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Produit
                        </label>
                        <select
                            className="input max-w-md"
                            value={selectedProduct?.id || ''}
                            onChange={(e) => {
                                const product = trackedProducts.find(p => p.id === e.target.value);
                                if (product) loadProductHistory(product);
                            }}
                        >
                            {trackedProducts.map(product => (
                                <option key={product.id} value={product.id}>
                                    {product.name}
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* Graphique */}
                    {priceData.length > 0 ? (
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={priceData}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="date" />
                                <YAxis />
                                <Tooltip />
                                <Legend />
                                <Line
                                    type="monotone"
                                    dataKey="prix"
                                    stroke="#8b5cf6"
                                    strokeWidth={2}
                                    dot={{ fill: '#8b5cf6', r: 4 }}
                                    activeDot={{ r: 6 }}
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    ) : (
                        <div className="text-center py-8 text-gray-500">
                            Pas encore d'historique de prix pour ce produit
                        </div>
                    )}
                </div>
            ) : (
                <div className="card mb-8 text-center py-12">
                    <ShoppingCartIcon className="h-20 w-20 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-gray-700 mb-2">
                        Aucun produit suivi
                    </h3>
                    <p className="text-gray-500 mb-4">
                        Commencez à suivre des produits pour voir l'évolution des prix
                    </p>
                    <button
                        onClick={() => navigate('/')}
                        className="btn-primary"
                    >
                        Parcourir les produits
                    </button>
                </div>
            )}

            {/* Produits récents */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Baisses de prix détectées */}
                <div className="card">
                    <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                        <ArrowTrendingDownIcon className="h-6 w-6 text-green-500" />
                        Baisses de Prix Récentes
                    </h2>
                    {priceDrops && priceDrops.length > 0 ? (
                        priceDrops.slice(0, 6).map(item => (
                            <div key={item.product_id} className="flex items-center justify-between py-3 border-b last:border-b-0">
                                <div className="flex-1 pr-4">
                                    <p className="font-medium truncate">{item.name}</p>
                                    <p className="text-sm text-gray-500">{item.marketplace?.toUpperCase()}</p>
                                </div>
                                <div className="text-right">
                                    <p className="font-bold text-purple-600">{item.current_price} FCFA</p>
                                    <p className="text-xs text-green-600">-{item.drop_pct}%</p>
                                </div>
                            </div>
                        ))
                    ) : (
                        <p className="text-gray-500 text-center py-4">Aucune baisse significative détectée</p>
                    )}
                </div>

                {/* Alertes actives */}
                <div className="card">
                    <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                        <BellIcon className="h-6 w-6 text-blue-500" />
                        Alertes Actives
                    </h2>
                    {alerts.filter(a => a.is_active).slice(0, 5).map(alert => (
                        <div key={alert.id} className="flex items-center justify-between py-3 border-b last:border-b-0">
                            <div className="flex-1">
                                <p className="font-medium">Alerte {alert.alert_type}</p>
                                <p className="text-sm text-gray-500">
                                    {alert.product_id}
                                </p>
                            </div>
                            <div className="text-right">
                                <span className="badge badge-success">Actif</span>
                                {alert.threshold_value && (
                                    <p className="text-xs text-gray-600 mt-1">
                                        Seuil: {alert.threshold_value}
                                    </p>
                                )}
                            </div>
                        </div>
                    ))}
                    {alerts.filter(a => a.is_active).length === 0 && (
                        <div className="text-center py-4">
                            <p className="text-gray-500 mb-2">Aucune alerte active</p>
                            <button
                                onClick={() => navigate('/alerts')}
                                className="btn-outline text-sm"
                            >
                                Créer une alerte
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
