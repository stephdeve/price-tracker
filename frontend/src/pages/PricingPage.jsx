import { CheckIcon } from '@heroicons/react/24/solid';

export default function PricingPage() {
    const plans = [
        {
            name: 'Gratuit',
            price: '0 XOF',
            features: [
                '5 produits trackés',
                'Historique 30 jours',
                'Prédictions basiques (7 jours)',
                'Alertes par email',
            ],
            cta: 'Commencer',
            highlighted: false,
        },
        {
            name: 'Premium',
            price: '1000 XOF/mois',
            priceNote: '~1.5 EUR',
            features: [
                'Produits illimités',
                'Historique 1 an complet',
                'Prédictions avancées (30 jours)',
                'Conseils d\'achat IA',
                'Alertes Telegram + WhatsApp',
                'Support prioritaire',
            ],
            cta: 'Passer Premium',
            highlighted: true,
        },
    ];

    return (
        <div className="min-h-[calc(100vh-200px)] py-12">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="text-center mb-12">
                    <h1 className="text-4xl font-extrabold text-gray-900 mb-4">
                        Tarifs Simples et Transparents
                    </h1>
                    <p className="text-xl text-gray-600">
                        Paye en Mobile Money (MTN, Moov) via KKiapay
                    </p>
                </div>

                <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
                    {plans.map((plan) => (
                        <div
                            key={plan.name}
                            className={`card ${plan.highlighted
                                    ? 'ring-2 ring-primary-500 relative'
                                    : ''
                                }`}
                        >
                            {plan.highlighted && (
                                <div className="absolute top-0 right-0 -mt-4 -mr-4">
                                    <span className="badge badge-warning text-sm px-3 py-1">
                                        Recommandé
                                    </span>
                                </div>
                            )}

                            <div className="text-center mb-6">
                                <h3 className="text-2xl font-bold text-gray-900">{plan.name}</h3>
                                <div className="mt-4">
                                    <span className="text-4xl font-extrabold text-gray-900">
                                        {plan.price}
                                    </span>
                                    {plan.priceNote && (
                                        <span className="text-gray-500 ml-2">({plan.priceNote})</span>
                                    )}
                                </div>
                            </div>

                            <ul className="space-y-3 mb-8">
                                {plan.features.map((feature, index) => (
                                    <li key={index} className="flex items-start">
                                        <CheckIcon className="h-5 w-5 text-primary-500 mr-2 mt-0.5" />
                                        <span className="text-gray-700">{feature}</span>
                                    </li>
                                ))}
                            </ul>

                            <button
                                className={`w-full py-3 rounded-lg font-medium ${plan.highlighted
                                        ? 'btn-primary'
                                        : 'btn-secondary'
                                    }`}
                            >
                                {plan.cta}
                            </button>
                        </div>
                    ))}
                </div>

                <div className="mt-12 text-center text-sm text-gray-500">
                    <p>Paiement sécurisé via KKiapay (Mobile Money MTN, Moov)</p>
                </div>
            </div>
        </div>
    );
}
