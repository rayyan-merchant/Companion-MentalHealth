import { useState } from 'react';
import { ChatShell } from '../components/chat/ChatShell';
import { Composer } from '../components/chat/Composer';
import { QuickPrompts } from '../components/chat/QuickPrompts';
import { ExplanationPanel } from '../components/explanation/ExplanationPanel';
import { useSession } from '../hooks/useSession';

export function Chat() {
    // KRR Hook
    const { messages, krrResult, isLoading, sendUserMessage } = useSession();

    // UI State
    const [selectedMessageId, setSelectedMessageId] = useState<string | null>(null);

    const handleQuickPrompt = (text: string) => {
        sendUserMessage(text);
    };

    return (
        <div className="flex h-full">
            <div className="flex-1 flex flex-col min-w-0">
                <ChatShell
                    messages={messages}
                    isLoading={isLoading}
                    onSelectMessage={setSelectedMessageId}
                />
                <QuickPrompts onSelect={handleQuickPrompt} />
                <Composer onSend={sendUserMessage} disabled={isLoading} />
            </div>

            <aside className="hidden lg:block w-80 xl:w-96 border-l border-gray-100 bg-background overflow-y-auto p-4 pb-2 space-y-4">
                <ExplanationPanel krrResult={krrResult} />
            </aside>
        </div>
    );
}

