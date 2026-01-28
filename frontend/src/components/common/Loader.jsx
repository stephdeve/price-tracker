export default function Loader() {
    return (
        <div className="flex items-center justify-center min-h-[400px]">
            <div className="relative">
                <div className="w-16 h-16 border-4 border-primary-200 border-t-primary-500 rounded-full animate-spin"></div>
                <div className="mt-4 text-center text-gray-600">Chargement...</div>
            </div>
        </div>
    );
}
