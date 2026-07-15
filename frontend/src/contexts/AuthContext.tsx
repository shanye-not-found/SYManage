import { createContext, useState ,useEffect, useContext } from 'react';
import type { CurrentUser } from '../types';
import { getCurrentUser, login as apiLogin, logout as apiLogout } from '../api/api';


type AuthContextValue = {
    currentUser: CurrentUser | null;
    login: (email: string, password: string) => Promise<void>;
    logout: () => Promise<void>;
    isAuthenticated: boolean;
}

export const AuthContext = createContext<AuthContextValue | null>(null);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    useEffect(() => {
        getCurrentUser().then((user) => {
            setCurrentUser(user);
            setIsAuthenticated(user !== null);
        }).catch((error) => {
            apiLogout();
        });
    }, []);


    const login = async (email: string, password: string) => {
        await apiLogin(email, password);
        getCurrentUser().then((user) => {
            setCurrentUser(user);
            setIsAuthenticated(user !== null);
        }).catch((error) => {
            apiLogout();
        });
    };

    const logout = async () => {
        await apiLogout();
        setCurrentUser(null);
        setIsAuthenticated(false);
    };

    return (
        <AuthContext.Provider value={{ currentUser, login, logout, isAuthenticated }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const auth = useContext(AuthContext);
    if (!auth) {
        throw new Error('useAuth 必须在 <AuthProvider> 内部使用');
    }
    return auth;
};

