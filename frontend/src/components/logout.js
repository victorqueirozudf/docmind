import { useEffect } from "react";
import axios from "axios";

export const Logout = () => {
    useEffect(() => {
        const logoutUser = async () => {
            try {
                const refreshToken = localStorage.getItem('refresh_token');
                // alert(refreshToken)
                if (!refreshToken) {
                    alert('Você não está logado.');
                    window.location.href = '/login';
                    return;
                }

                const response = await axios.post(
                    'http://localhost:8000/logout/',
                    { refresh_token: refreshToken },
                    {
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${localStorage.getItem('access_token')}` // Adicionando o token
                        }
                    }
                );

                console.log('logout: ', response.data);
                localStorage.clear();
                delete axios.defaults.headers.common['Authorization'];
                window.location.href = '/login';

                alert('Deslogado com sucesso! ')
            } catch (error) {
                console.error('Erro no logout:', error);
                alert('O logout não funcionou. Tente novamente.');
            }
        };

        logoutUser();
    }, []);

    return <div></div>;
};
