export default function DashboardPage() {
    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <h1 className="text-3xl font-bold mb-8">Dashboard</h1>

            <div className="card">
                <p className="text-gray-600">
                    Dashboard en cours de développement.
                    Utilisez les endpoints API pour tester les fonctionnalités.
                </p>
                <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <h3 className="font-semibold text-yellow-800 mb-2">🚧 En cours</h3>
                    <ul className="text-sm text-yellow-700 space-y-1">
                        <li>• Liste des produits trackés</li>
                        <li>• Graphiques de prix</li>
                        <li>• Alertes actives</li>
                    </ul>
                </div>
            </div>
        </div>
    );
}
