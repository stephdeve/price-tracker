import { Link } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { Fragment } from 'react';
import { Menu, Transition } from '@headlessui/react';
import {
    Bars3Icon,
    UserCircleIcon,
    ChartBarIcon,
    BellIcon,
    ArrowRightOnRectangleIcon
} from '@heroicons/react/24/outline';

export default function Navbar() {
    const { isAuthenticated, user, logout } = useAuthStore();

    return (
        <nav className="bg-white shadow-sm border-b border-gray-200">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16">
                    {/* Logo */}
                    <div className="flex items-center">
                        <Link to="/" className="flex items-center space-x-2">
                            <ChartBarIcon className="h-8 w-8 text-primary-500" />
                            <span className="text-xl font-bold text-gray-900">
                                Price Tracker <span className="text-primary-500">🇧🇯</span>
                            </span>
                        </Link>
                    </div>

                    {/* Desktop Navigation */}
                    <div className="hidden md:flex items-center space-x-8">
                        {isAuthenticated ? (
                            <>
                                <Link
                                    to="/dashboard"
                                    className="text-gray-700 hover:text-primary-500 font-medium"
                                >
                                    Dashboard
                                </Link>
                                <Link
                                    to="/alerts"
                                    className="text-gray-700 hover:text-primary-500 font-medium relative"
                                >
                                    <BellIcon className="h-6 w-6" />
                                </Link>

                                {/* User Menu */}
                                <Menu as="div" className="relative">
                                    <Menu.Button className="flex items-center space-x-2">
                                        <UserCircleIcon className="h-8 w-8 text-gray-600" />
                                        <span className="text-sm font-medium text-gray-700">
                                            {user?.full_name}
                                        </span>
                                        {user?.is_premium && (
                                            <span className="badge badge-warning ml-2">Premium</span>
                                        )}
                                    </Menu.Button>

                                    <Transition
                                        as={Fragment}
                                        enter="transition ease-out duration-100"
                                        enterFrom="transform opacity-0 scale-95"
                                        enterTo="transform opacity-100 scale-100"
                                        leave="transition ease-in duration-75"
                                        leaveFrom="transform opacity-100 scale-100"
                                        leaveTo="transform opacity-0 scale-95"
                                    >
                                        <Menu.Items className="absolute right-0 mt-2 w-48 origin-top-right bg-white rounded-lg shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                                            <div className="py-1">
                                                <Menu.Item>
                                                    {({ active }) => (
                                                        <Link
                                                            to="/profile"
                                                            className={`${active ? 'bg-gray-100' : ''
                                                                } block px-4 py-2 text-sm text-gray-700`}
                                                        >
                                                            Mon Profil
                                                        </Link>
                                                    )}
                                                </Menu.Item>
                                                {!user?.is_premium && (
                                                    <Menu.Item>
                                                        {({ active }) => (
                                                            <Link
                                                                to="/pricing"
                                                                className={`${active ? 'bg-gray-100' : ''
                                                                    } block px-4 py-2 text-sm text-benin-yellow`}
                                                            >
                                                                ⭐ Passer Premium
                                                            </Link>
                                                        )}
                                                    </Menu.Item>
                                                )}
                                                <Menu.Item>
                                                    {({ active }) => (
                                                        <button
                                                            onClick={logout}
                                                            className={`${active ? 'bg-gray-100' : ''
                                                                } flex items-center w-full px-4 py-2 text-sm text-gray-700`}
                                                        >
                                                            <ArrowRightOnRectangleIcon className="h-5 w-5 mr-2" />
                                                            Déconnexion
                                                        </button>
                                                    )}
                                                </Menu.Item>
                                            </div>
                                        </Menu.Items>
                                    </Transition>
                                </Menu>
                            </>
                        ) : (
                            <>
                                <Link to="/pricing" className="text-gray-700 hover:text-primary-500 font-medium">
                                    Tarifs
                                </Link>
                                <Link to="/login" className="text-gray-700 hover:text-primary-500 font-medium">
                                    Connexion
                                </Link>
                                <Link to="/register" className="btn-primary">
                                    Inscription
                                </Link>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </nav>
    );
}
