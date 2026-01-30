import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useProductStore } from '../store/productStore';
import { ArrowTopRightOnSquareIcon, CheckIcon } from '@heroicons/react/24/outline';

export default function ProductDetailPage() {
    const { id } = useParams();
    const navigate = useNavigate();
    const { fetchProductById, fetchComparisonGroup } = useProductStore();

    const [product, setProduct] = useState(null);
    const [group, setGroup] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        let mounted = true;
        (async () => {
            setLoading(true);
            const p = await fetchProductById(id);
            const g = await fetchComparisonGroup(id);
            if (mounted) {
                setProduct(p);
                setGroup(g);
                setLoading(false);
            }
        })();
        return () => { mounted = false; };
    }, [id]);

    if (loading) {
        return (
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 text-center">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
                <p className="text-gray-600 mt-4">Chargement du produit...</p>
            </div>
        );
    }

    if (!product) {
        return (
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 text-center">
                <p className="text-gray-600">Produit introuvable</p>
                <button onClick={() => navigate(-1)} className="btn-outline mt-4">Retour</button>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="mb-8">
                <h1 className="text-3xl font-bold mb-2">{product.name}</h1>
                <div className="flex items-center gap-3 text-sm text-gray-600">
                    <span className="badge bg-gray-100 text-gray-800">{product.marketplace?.toUpperCase()}</span>
                    {product.category && <span className="badge bg-purple-50 text-purple-700">{product.category}</span>}
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 card">
                    <div className="flex items-start gap-6">
                        <div className="bg-gray-100 h-48 w-48 rounded-lg flex items-center justify-center">
                            {/* Placeholder image */}
                            <span className="text-gray-400">Image</span>
                        </div>
                        <div className="flex-1">
                            <p className="text-3xl font-extrabold text-primary-600">{product.current_price} <span className="text-lg font-medium">FCFA</span></p>
                            <p className="text-gray-500 mt-2">{product.description || 'Aucune description'}</p>
                            <div className="mt-4 flex gap-3">
                                {product.url && (
                                    <a href={product.url} target="_blank" rel="noopener noreferrer" className="btn-outline flex items-center gap-2">
                                        Ouvrir la page
                                        <ArrowTopRightOnSquareIcon className="h-5 w-5" />
                                    </a>
                                )}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Meilleurs prix inter-sources */}
                <div className="card">
                    <h2 className="text-xl font-bold mb-4">Meilleurs prix (inter-sources)</h2>
                    {!group || !group.offers || group.offers.length === 0 ? (
                        <p className="text-gray-500">Aucune autre offre similaire trouvée pour le moment.</p>
                    ) : (
                        <div className="space-y-3">
                            {group.offers.map((o, idx) => (
                                <div key={o.product_id + idx} className="flex items-start justify-between p-3 rounded-lg border">
                                    <div className="flex-1 mr-4">
                                        <div className="flex items-center gap-2">
                                            <p className="font-medium line-clamp-1">{o.title}</p>
                                            <span className="badge bg-gray-100 text-gray-800">{o.marketplace?.toUpperCase()}</span>
                                            {idx === 0 && (
                                                <span className="badge badge-success flex items-center gap-1">
                                                    <CheckIcon className="h-4 w-4" /> Meilleur prix
                                                </span>
                                            )}
                                        </div>
                                        <a href={o.url} target="_blank" rel="noopener noreferrer" className="text-sm text-blue-600 hover:underline">
                                            Voir l'offre
                                        </a>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-lg font-bold text-primary-700">{o.price} <span className="text-sm">FCFA</span></p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
