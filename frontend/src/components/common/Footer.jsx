import { Link } from 'react-router-dom';

export default function Footer() {
    return (
        <footer className="bg-gray-900 text-gray-300 mt-auto">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                    {/* About */}
                    <div>
                        <h3 className="text-white font-bold text-lg mb-4">Price Tracker Bénin</h3>
                        <p className="text-sm">
                            Suivez les prix sur Jumia, Amazon et les marchés locaux.
                            Économisez grâce à l'IA.
                        </p>
                    </div>

                    {/* Links */}
                    <div>
                        <h4 className="text-white font-semibold mb-4">Liens rapides</h4>
                        <ul className="space-y-2 text-sm">
                            <li><Link to="/dashboard" className="hover:text-white">Dashboard</Link></li>
                            <li><Link to="/pricing" className="hover:text-white">Tarifs</Link></li>
                            <li><Link to="/alerts" className="hover:text-white">Mes Alertes</Link></li>
                        </ul>
                    </div>

                    {/* Support */}
                    <div>
                        <h4 className="text-white font-semibold mb-4">Support</h4>
                        <ul className="space-y-2 text-sm">
                            <li><a href="#" className="hover:text-white">FAQ</a></li>
                            <li><a href="#" className="hover:text-white">Contact</a></li>
                            <li><a href="#" className="hover:text-white">Guide</a></li>
                        </ul>
                    </div>

                    {/* Legal */}
                    <div>
                        <h4 className="text-white font-semibold mb-4">Légal</h4>
                        <ul className="space-y-2 text-sm">
                            <li><a href="#" className="hover:text-white">CGU</a></li>
                            <li><a href="#" className="hover:text-white">Confidentialité</a></li>
                            <li><a href="#" className="hover:text-white">Cookies</a></li>
                        </ul>
                    </div>
                </div>

                <div className="border-t border-gray-800 mt-8 pt-8 text-sm text-center">
                    <p>&copy; 2026 Price Tracker Bénin. Fait avec heart au Bénin 🇧🇯</p>
                </div>
            </div>
        </footer>
    );
}
