import { Phone, ExternalLink, ShieldAlert, AlertTriangle } from 'lucide-react';

interface CrisisAlertProps {
    type?: 'suicidal_ideation' | 'self_harm' | 'harm_to_others' | 'medical_emergency';
}

export function CrisisAlert({ type = 'suicidal_ideation' }: CrisisAlertProps) {
    const isHarmToOthers = type === 'harm_to_others';
    const isMedicalEmergency = type === 'medical_emergency';
    const usesOrangeTheme = isHarmToOthers || isMedicalEmergency;

    return (
        <div className={`${usesOrangeTheme ? 'bg-orange-50 border-orange-200' : 'bg-red-50 border-red-200'} border rounded-xl p-4 my-2 animate-fade-in`}>
            <div className="flex items-start gap-3">
                <div className={`p-2 rounded-lg ${usesOrangeTheme ? 'bg-orange-100 text-orange-600' : 'bg-red-100 text-red-600'}`}>
                    {usesOrangeTheme ? <AlertTriangle size={24} /> : <ShieldAlert size={24} />}
                </div>
                <div className="flex-1">
                    <h3 className={`${usesOrangeTheme ? 'text-orange-800' : 'text-red-800'} font-semibold text-lg mb-1`}>
                        {isMedicalEmergency
                            ? 'Please get urgent medical help.'
                            : isHarmToOthers
                                ? 'Please talk to someone.'
                                : 'You are not alone.'}
                    </h3>
                    <p className={`${usesOrangeTheme ? 'text-orange-700' : 'text-red-700'} text-sm mb-4`}>
                        {isMedicalEmergency
                            ? 'Chest pain with trouble breathing can be an emergency. Call now or ask someone nearby to help you get immediate care.'
                            : isHarmToOthers
                                ? 'What you are feeling is intense, and a professional can help you work through it safely. Please reach out; it is a sign of strength.'
                                : 'If you are in immediate danger or feeling overwhelmed, please reach out for help right now. People want to support you.'}
                    </p>

                    <div className="grid gap-2 sm:grid-cols-2">
                        <a href="tel:1122" className={`flex items-center justify-center gap-2 ${usesOrangeTheme ? 'bg-orange-600 hover:bg-orange-700' : 'bg-red-600 hover:bg-red-700'} text-white py-2 px-4 rounded-lg font-medium transition-colors`}>
                            <Phone size={16} />
                            Call Rescue 1122
                        </a>
                        <a href="tel:+924235761999" className={`flex items-center justify-center gap-2 bg-white border ${usesOrangeTheme ? 'border-orange-200 text-orange-700 hover:bg-orange-50' : 'border-red-200 text-red-700 hover:bg-red-50'} py-2 px-4 rounded-lg font-medium transition-colors`}>
                            <Phone size={16} />
                            Rozan Helpline
                        </a>
                    </div>
                </div>
            </div>
            <div className={`mt-3 pt-3 border-t ${usesOrangeTheme ? 'border-orange-100' : 'border-red-100'} flex justify-end`}>
                <a
                    href="https://umang.com.pk"
                    target="_blank"
                    rel="noopener noreferrer"
                    className={`text-xs ${usesOrangeTheme ? 'text-orange-600 hover:text-orange-800' : 'text-red-600 hover:text-red-800'} flex items-center gap-1 font-medium`}
                >
                    Visit Umang Pakistan <ExternalLink size={10} />
                </a>
            </div>
        </div>
    );
}
