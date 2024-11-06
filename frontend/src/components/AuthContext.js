// AuthContext.js
import React, { createContext, useState, useEffect } from 'react';
import axios from 'axios';

// Cria o contexto
export const AuthContext = createContext();

// Provedor do contexto
export const AuthProvider = ({ children }) => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [userData, setUserData] = useState(null);
    const [loading, setLoading] = useState(true);

    // Função para verificar o token
    const verifyToken = async () => {
        const accessToken = localStorage.getItem('access_token');

        if (!accessToken) {
            setIsAuthenticated(false);
            setLoading(false);
            return;
        }

        try {
            const response = await axios.post('http://localhost:8000/api/authentication/verify-token/', {}, {
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'Content-Type': 'application/json',
                },
            });

            if (response.status === 200) {
                setIsAuthenticated(true);
                setUserData(response.data.user);
            }
        } catch (error) {
            console.error('Erro ao verificar token:', error);
            setIsAuthenticated(false);
            localStorage.removeItem('access_token');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        verifyToken();
    }, []);

    return (
        <AuthContext.Provider value={{ isAuthenticated, setIsAuthenticated, userData, setUserData, loading, verifyToken }}>
            {children}
        </AuthContext.Provider>
    );
};
