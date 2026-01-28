import { Link } from 'react-router-dom';
import {
    ChartBarIcon,
    BellIcon,
    SparklesIcon,
    CurrencyDollarIcon
} from '@heroicons/react/24/outline';

export default function HomePage() {
    return (
        <div>
            {/* Hero Section */}
            <section className="bg-gradient-to-br from-primary-50 to-primary-100 py-20">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center">
                        <h1 className="text-4xl md:text-6xl font-extrabold text-gray-900 mb-6">
                            Économise sur tes achats au <span className="text-primary-500">Bénin 🇧🇯</span>
                        </h1>
                        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
                            Suis les prix sur Jumia, Amazon et les marchés locaux.
                            Reçois des alertes intelligentes et achète au meilleur moment grâce à l'IA.
                        </p>
                        <div className="flex justify-center space-x-4">
                            <Link to="/register" className="btn-primary text-lg px-8 py-3">
                                Commencer Gratuitement
                            </Link>
                            <Link to="/pricing" className="btn-outline text-lg px-8 py-3">
                                Voir les Tarifs
                            </Link>
                        </div>
                    </div>
                </div>
            </section>

            {/* Features */}
            <section className="py-20">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <h2 className="text-3xl font-bold text-center mb-12">
                        Fonctionnalités
                    </h2>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                        <div className="card text-center">
                            <div className="flex justify-center mb-4">
                                <ChartBarIcon className="h-12 w-12 text-primary-500" />
                            </div>
                            <h3 className="font-bold text-lg mb-2">Suivi de Prix</h3>
                            <p className="text-gray-600">
                                Suis l'évolution des prix de tes produits préférés en temps réel
                            </p>
                        </div>

                        <div className="card text-center">
                            <div className="flex justify-center mb-4">
                                <BellIcon className="h-12 w-12 text-primary-500" />
                            </div>
                            <h3 className="font-bold text-lg mb-2">Alertes Intelligentes</h3>
                            <p className="text-gray-600">
                                Reçois des alertes par WhatsApp ou Telegram quand le prix baisse
                            </p>
                        </div>

                        <div className="card text-center">
                            <div className="flex justify-center mb-4">
                                <SparklesIcon className="h-12 w-12 text-primary-500" />
                            </div>
                            <h3 className="font-bold text-lg mb-2">Prédictions IA</h3>
                            <p className="text-gray-600">
                                L'IA prédit les baisses de prix et te conseille le meilleur moment d'achat
                            </p>
                        </div>

                        <div className="card text-center">
                            <div className="flex justify-center mb-4">
                                <CurrencyDollarIcon className="h-12 w-12 text-primary-500" />
                            </div>
                            <h3 className="font-bold text-lg mb-2">Prix XOF</h3>
                            <p className="text-gray-600">
                                Tous les prix en Franc CFA, adapté au marché béninois
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="bg-primary-500 text-white py-16">
                <div className="max-w-4xl mx-auto text-center px-4">
                    <h2 className="text-3xl font-bold mb-4">
                        Prêt à économiser? 💰
                    </h2>
                    <p className="text-xl mb-8 opacity-90">
                        Rejoins des milliers de Béninois qui économisent avec Price Tracker
                    </p>
                    <Link to="/register" className="bg-white text-primary-500 hover:bg-gray-100 font-bold py-3 px-8 rounded-lg text-lg">
                        Créer mon compte gratuit
                    </Link>
                </div>
            </section>
        </div>
    );
}
