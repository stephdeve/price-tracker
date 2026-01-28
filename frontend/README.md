# Frontend React - Price Tracker Bénin

## TODO: Initialize React + Vite

Le frontend sera créé dans cette phase suivante.

### Installation

```bash
cd d:\dev\price-tracker-IA
npm create vite@latest frontend -- --template react
cd frontend
npm install

# Installer les dépendances du projet
npm install react-router-dom zustand @tanstack/react-query
npm install react-hook-form zod @hookform/resolvers
npm install axios recharts
npm install react-hot-toast
npm install -D tailwindcss postcss autoprefixer
npm install @headlessui/react @heroicons/react
```

### Structure prévue

```
frontend/
├── src/
│   ├── components/
│   │   ├── auth/
│   │   ├── products/
│   │   ├── prices/
│   │   ├── alerts/
│   │   ├── ai/
│   │   └── common/
│   ├── pages/
│   ├── hooks/
│   ├── services/
│   ├── store/
│   ├── utils/
│   └── styles/
├── public/
├── index.html
├── vite.config.js
├── tailwind.config.js
└── package.json
```

## Voir le walkthrough pour plus de détails
