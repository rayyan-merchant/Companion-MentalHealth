import {
    createContext,
    ReactNode,
    useContext,
    useEffect,
    useState
} from 'react';
import { apiFetch, getPublicConfig } from '../api/client';

export interface User {
    user_id: string;
    email: string;
    created_at: string;
    must_change_password: boolean;
}

interface AuthContextType {
    user: User | null;
    isLoading: boolean;
    isAuthenticated: boolean;
    login: (email: string, password: string) => Promise<User>;
    signup: (email: string, password: string) => Promise<User>;
    logout: () => Promise<void>;
    changePassword: (currentPassword: string, newPassword: string) => Promise<void>;
}

interface AuthResponse {
    user: User;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        let active = true;
        async function bootstrap() {
            try {
                await getPublicConfig();
                const current = await apiFetch<User>('/auth/me');
                if (active) setUser(current);
            } catch {
                if (active) setUser(null);
            } finally {
                if (active) setIsLoading(false);
            }
        }
        bootstrap();
        const clear = () => setUser(null);
        window.addEventListener('companion:unauthorized', clear);
        return () => {
            active = false;
            window.removeEventListener('companion:unauthorized', clear);
        };
    }, []);

    const login = async (email: string, password: string) => {
        const data = await apiFetch<AuthResponse>('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        setUser(data.user);
        return data.user;
    };

    const signup = async (email: string, password: string) => {
        const data = await apiFetch<AuthResponse>('/auth/signup', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        setUser(data.user);
        return data.user;
    };

    const logout = async () => {
        try {
            await apiFetch('/auth/logout', { method: 'POST' });
        } finally {
            setUser(null);
        }
    };

    const changePassword = async (
        currentPassword: string,
        newPassword: string
    ) => {
        const updated = await apiFetch<User>('/auth/change-password', {
            method: 'POST',
            body: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword
            })
        });
        setUser(updated);
    };

    return (
        <AuthContext.Provider value={{
            user,
            isLoading,
            isAuthenticated: Boolean(user),
            login,
            signup,
            logout,
            changePassword
        }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) throw new Error('useAuth must be used within AuthProvider');
    return context;
}
