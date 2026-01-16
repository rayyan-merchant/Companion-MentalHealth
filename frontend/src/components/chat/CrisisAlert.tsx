import { Phone, ExternalLink, ShieldAlert } from 'lucide-react';

export function CrisisAlert() {
    return (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 my-2 animate-fade-in">
            <div className="flex items-start gap-3">
                <div className="p-2 bg-red-100 rounded-lg text-red-600">
                    <ShieldAlert size={24} />
                </div>
                <div className="flex-1">
                    <h3 className="text-red-800 font-semibold text-lg mb-1">
                        You are not alone.
                    </h3>
                    <p className="text-red-700 text-sm mb-4">
                        If you are in immediate danger or feeling overwhelmed, please reach out for help right now. People want to support you.
                    </p>

                    <div className="grid gap-2 sm:grid-cols-2">
                        <a href="tel:15" className="flex items-center justify-center gap-2 bg-red-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-red-700 transition-colors">
                            <Phone size={16} />
                            Call Emergency (15)
                        </a>
                        <a href="tel:+924235761999" className="flex items-center justify-center gap-2 bg-white border border-red-200 text-red-700 py-2 px-4 rounded-lg font-medium hover:bg-red-50 transition-colors">
                            <Phone size={16} />
                            Rozan Helpline
                        </a>
                    </div>
                </div>
            </div>
            <div className="mt-3 pt-3 border-t border-red-100 flex justify-end">
                <a
                    href="https://umang.com.pk"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-red-600 hover:text-red-800 flex items-center gap-1 font-medium"
                >
                    Visit Umang Pakistan <ExternalLink size={10} />
                </a>
            </div>
        </div>
    );
}
