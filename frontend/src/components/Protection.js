import React from 'react';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ element }) => {
    const isAuthenticated = !!localStorage.getItem('access_token'); // Verifica se há um token de acesso

    return isAuthenticated ? element : <Navigate to="/login" />;
};

export default ProtectedRoute;