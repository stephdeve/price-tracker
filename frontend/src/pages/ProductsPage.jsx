import { useEffect, useState } from 'react';
import { useProductStore } from '../store/productStore';
import { useNavigate } from 'react-router-dom';
import { ShoppingCartIcon, ArrowTopRightOnSquareIcon, HeartIcon, ArrowTrendingDownIcon, PlusIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { HeartIcon as HeartSolidIcon } from '@heroicons/react/24/solid';
import api from '../services/api';
import toast from 'react-hot-toast';

export default function ProductsPage() {
    const navigate = useNavigate();
    const { products, trackedProducts, fetchProducts, fetchTrackedProducts, trackProduct, untrackProduct, loading } = useProductStore();
    const [filter, setFilter] = useState('all'); // all, tracked, jumia, amazon
    const [showAddModal, setShowAddModal] = useState(false);
    const [productUrl, setProductUrl] = useState('');
    const [scraping, setScraping] = useState(false);

    useEffect(() => {
        fetchProducts();
        fetchTrackedProducts();
    }, []);

    const isTracked = (productId) => {
        return trackedProducts.some(p => p.id === productId);
    };

    const handleTrackToggle = async (productId) => {
        if (isTracked(productId)) {
            await untrackProduct(productId);
        } else {
            await trackProduct(productId);
        }
    };

    const handleScrapeProduct = async (e) => {
        e.preventDefault();
        if (!productUrl.trim()) {
            toast.error('Veuillez entrer une URL');
            return;
        }

        // Déterminer la marketplace
        let marketplace = 'jumia';
        if (productUrl.includes('amazon.com') || productUrl.includes('amazon.')) {
            marketplace = 'amazon';
        }

        setScraping(true);
        try {
            const { data } = await api.post('/products/scrape', {
                url: productUrl,
                marketplace,
            });
            
            toast.success('Produit ajouté avec succès! 🎉');
            setProductUrl('');
            setShowAddModal(false);
            
            // Rafraîchir la liste
            await fetchProducts();
            await fetchTrackedProducts();
        } catch (error) {
            const msg = error.response?.data?.detail || 'Erreur lors du scraping du produit';
            toast.error(msg);
            console.error('Scrape error:', error);
        } finally {
            setScraping(false);
        }
    };

    const filteredProducts = products.filter(product => {
        if (filter === 'tracked') return isTracked(product.id);
        if (filter === 'jumia') return product.marketplace === 'jumia';
        if (filter === 'amazon') return product.marketplace === 'amazon';
        return true;
    });

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold">Produits</h1>
                    <p className="text-gray-600 mt-1">Parcourez et suivez les produits</p>
                </div>
                <button
                    type="button"
                    onClick={() => setShowAddModal(true)}
                    className="btn-primary flex items-center gap-2"
                >
                    <PlusIcon className="h-5 w-5" />
                    Ajouter un produit
                </button>
            </div>

            {/* Modal d'ajout de produit */}
            {showAddModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
                        <div className="flex justify-between items-center mb-4">
                            <h2 className="text-2xl font-bold">Ajouter un Produit</h2>
                            <button
                                onClick={() => setShowAddModal(false)}
                                className="text-gray-500 hover:text-gray-700"
                            >
                                <XMarkIcon className="h-6 w-6" />
                            </button>
                        </div>

                        <form onSubmit={handleScrapeProduct} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    URL du Produit
                                </label>
                                <input
                                    type="url"
                                    value={productUrl}
                                    onChange={(e) => setProductUrl(e.target.value)}
                                    placeholder="https://www.jumia.ci/... ou https://amazon.com/..."
                                    className="input"
                                    required
                                />
                                <p className="text-sm text-gray-500 mt-1">
                                    Collez le lien d'un produit depuis Jumia, Amazon, etc.
                                </p>
                            </div>

                            <div className="flex gap-3">
                                <button
                                    type="submit"
                                    className="btn-primary flex-1"
                                    disabled={scraping}
                                >
                                    {scraping ? 'Scraping...' : 'Scraper le produit'}
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setShowAddModal(false)}
                                    className="btn-secondary"
                                >
                                    Annuler
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Filtres */}
            <div className="flex gap-2 mb-6">
                <button
                    onClick={() => setFilter('all')}
                    className={`px-4 py-2 rounded-lg font-medium ${filter === 'all' ? 'bg-primary-500 text-white' : 'bg-gray-200 text-gray-700'
                        }`}
                >
                    Tous ({products.length})
                </button>
                <button
                    onClick={() => setFilter('tracked')}
                    className={`px-4 py-2 rounded-lg font-medium ${filter === 'tracked' ? 'bg-green-500 text-white' : 'bg-gray-200 text-gray-700'
                        }`}
                >
                    Suivis ({trackedProducts.length})
                </button>
                <button
                    onClick={() => setFilter('jumia')}
                    className={`px-4 py-2 rounded-lg font-medium ${filter === 'jumia' ? 'bg-orange-500 text-white' : 'bg-gray-200 text-gray-700'
                        }`}
                >
                    Jumia
                </button>
                <button
                    onClick={() => setFilter('amazon')}
                    className={`px-4 py-2 rounded-lg font-medium ${filter === 'amazon' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'
                        }`}
                >
                    Amazon
                </button>
            </div>

            {/* Liste des produits */}
            {loading ? (
                <div className="text-center py-12">
                    <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
                    <p className="text-gray-600 mt-4">Chargement des produits...</p>
                </div>
            ) : filteredProducts.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {filteredProducts.map(product => (
                        <div key={product.id} className="card hover:shadow-lg transition-shadow">
                            {/* Image placeholder */}
                            <div className="bg-gray-100 h-48 rounded-lg mb-4 flex items-center justify-center">
                                <ShoppingCartIcon className="h-20 w-20 text-gray-400" />
                            </div>

                            {/* Info */}
                            <div className="mb-4">
                                <div className="flex items-start justify-between mb-2">
                                    <h3 className="font-bold text-lg line-clamp-2 flex-1">
                                        {product.name}
                                    </h3>
                                    <button
                                        onClick={() => handleTrackToggle(product.id)}
                                        className={`ml-2 p-2 rounded-full ${isTracked(product.id)
                                            ? 'bg-red-100 text-red-600'
                                            : 'bg-gray-100 text-gray-400'
                                            }`}
                                        title={isTracked(product.id) ? 'Ne plus suivre' : 'Suivre'}
                                    >
                                        {isTracked(product.id) ? <HeartSolidIcon className="h-5 w-5" /> : <HeartIcon className="h-5 w-5" />}
                                    </button>
                                </div>

                                <div className="flex items-center gap-2 mb-2">
                                    <span className={`badge ${product.marketplace === 'jumia' ? 'bg-orange-100 text-orange-800' : 'bg-blue-100 text-blue-800'
                                        }`}>
                                        {product.marketplace?.toUpperCase()}
                                    </span>
                                    {product.in_stock !== undefined && (
                                        <span className={`badge ${product.in_stock ? 'badge-success' : 'badge-danger'
                                            }`}>
                                            {product.in_stock ? 'En stock' : 'Rupture'}
                                        </span>
                                    )}
                                </div>

                                <div className="flex items-baseline gap-2">
                                    <p className="text-2xl font-bold text-primary-600">
                                        {product.current_price} <span className="text-sm">FCFA</span>
                                    </p>
                                    {product.original_price && product.original_price > product.current_price && (
                                        <div className="flex items-center gap-1 text-green-600 text-sm">
                                            <ArrowTrendingDownIcon className="h-4 w-4" />
                                            <span>
                                                -{Math.round(((product.original_price - product.current_price) / product.original_price) * 100)}%
                                            </span>
                                        </div>
                                    )}
                                </div>

                                {product.original_price && product.original_price > product.current_price && (
                                    <p className="text-sm text-gray-500 line-through">
                                        {product.original_price} FCFA
                                    </p>
                                )}
                            </div>

                            {/* Actions */}
                            <div className="flex gap-2">
                                <button
                                    onClick={() => navigate(`/product/${product.id}`)}
                                    className="flex-1 btn-primary text-sm"
                                >
                                    Voir détails
                                </button>
                                {product.url && (
                                    <a
                                        href={product.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="btn-outline text-sm flex items-center gap-1"
                                    >
                                        <ArrowTopRightOnSquareIcon className="h-5 w-5" />
                                    </a>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <div className="card text-center py-12">
                    <ShoppingCartIcon className="h-20 w-20 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-gray-700 mb-2">
                        {filter === 'tracked'
                            ? 'Aucun produit suivi'
                            : filter === 'all'
                                ? 'Aucun produit disponible'
                                : `Aucun produit ${filter}`
                        }
                    </h3>
                    <p className="text-gray-500 mb-4">
                        {filter === 'tracked'
                            ? 'Cliquez sur le cœur pour suivre des produits'
                            : 'Les produits seront ajoutés prochainement'
                        }
                    </p>
                    {filter !== 'all' && (
                        <button onClick={() => setFilter('all')} className="btn-outline">
                            Voir tous les produits
                        </button>
                    )}
                </div>
            )}
        </div>
    );
}
