import { CheckIcon } from '@heroicons/react/24/solid';
import { useEffect, useRef, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import api from '../services/api';
import toast from 'react-hot-toast';

export default function PricingPage() {
    const navigate = useNavigate();
    const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
    const user = useAuthStore((s) => s.user);
    const [searchParams] = useSearchParams();
    const upgrade = searchParams.get('upgrade');
    const scriptLoaded = useRef(false);
    const [isPaying, setIsPaying] = useState(false);

    const loadKkiapayScript = () => new Promise((resolve, reject) => {
        if (scriptLoaded.current) return resolve();
        const existing = document.querySelector('script[src^="https://cdn.kkiapay.me/k.js"]');
        if (existing) {
            scriptLoaded.current = true;
            return resolve();
        }
        const s = document.createElement('script');
        s.src = 'https://cdn.kkiapay.me/k.js';
        s.async = true;
        s.onload = () => {
            scriptLoaded.current = true;
            resolve();
        };
        s.onerror = reject;
        document.body.appendChild(s);
    });

    const startPremiumFlow = async (plan = 'PREMIUM_MONTHLY') => {
        try {
            setIsPaying(true);
            const { data: cfg } = await api.get('/payments/config');
            if (!cfg?.kkiapay_public_key) {
                toast.error('KKIAPAY non configuré');
                return;
            }
            await loadKkiapayScript();
            if (typeof window.openKkiapayWidget !== 'function') {
                toast.error('SDK KKIAPAY indisponible');
                return;
            }
            const amount = plan === 'PREMIUM_YEARLY' ? cfg.premium_yearly_price_xof : cfg.premium_monthly_price_xof;
            window.openKkiapayWidget({
                amount,
                currency: 'XOF',
                api_key: cfg.kkiapay_public_key,
                sandbox: !!cfg.sandbox,
                name: user?.full_name,
                email: user?.email,
                phone: user?.phone,
                reason: plan === 'PREMIUM_YEARLY' ? 'Abonnement Premium Annuel Price Tracker' : 'Abonnement Premium Mensuel Price Tracker',
                onSuccess: async (resp) => {
                    try {
                        const tx = resp?.transactionId || resp?.transaction_id || resp?.id;
                        if (!tx) throw new Error('Transaction ID manquant');
                        const r = await api.post('/payments/kkiapay/confirm', {
                            transaction_id: tx,
                            amount_xof: amount,
                            plan,
                        });
                        useAuthStore.getState().setUser(r.data);
                        toast.success('Abonnement Premium activé');
                        navigate('/dashboard');
                    } catch (e) {
                        toast.error('Erreur de confirmation du paiement');
                    }
                },
                onError: () => toast.error('Paiement annulé ou échoué'),
                onClose: () => setIsPaying(false),
            });
        } catch (e) {
            toast.error('Impossible de démarrer le paiement');
        } finally {
            setIsPaying(false);
        }
    };

    useEffect(() => {
        if (!isAuthenticated) return;
        if (upgrade === 'premium_monthly') {
            startPremiumFlow('PREMIUM_MONTHLY');
        } else if (upgrade === 'premium_yearly') {
            startPremiumFlow('PREMIUM_YEARLY');
        }
    }, [isAuthenticated, upgrade]);
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
            planKey: 'PREMIUM_MONTHLY',
        },
        {
            name: 'Premium Annuel',
            price: '10 000 XOF/an',
            priceNote: '~15 EUR',
            features: [
                'Produits illimités',
                'Historique 1 an complet',
                'Prédictions avancées (30 jours)',
                'Conseils d\'achat IA',
                'Alertes Telegram + WhatsApp',
                'Support prioritaire',
            ],
            cta: 'Passer en Annuel',
            highlighted: true,
            planKey: 'PREMIUM_YEARLY',
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
                                onClick={() => {
                                    if (!isAuthenticated) {
                                        // invite user to register/login first
                                        if (plan.highlighted) {
                                            const next = encodeURIComponent(`/pricing?upgrade=${plan.planKey.toLowerCase()}`);
                                            navigate(`/login?next=${next}`);
                                        } else {
                                            navigate('/register');
                                        }
                                        return;
                                    }

                                    if (plan.highlighted) {
                                        if (isPaying) return;
                                        startPremiumFlow(plan.planKey);
                                    } else {
                                        // start with free plan: go to dashboard
                                        navigate('/dashboard');
                                    }
                                }}
                                disabled={plan.highlighted && isPaying}
                                className={`w-full py-3 rounded-lg font-medium flex items-center justify-center gap-2 ${plan.highlighted
                                    ? 'btn-primary'
                                    : 'btn-secondary'
                                    }`}
                            >
                                {plan.highlighted && isPaying ? (
                                    <>
                                        <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                        </svg>
                                        Paiement en cours...
                                    </>
                                ) : (
                                    plan.cta
                                )}
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
