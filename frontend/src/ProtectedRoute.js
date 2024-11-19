// src/ProtectedRoute.js

import React from 'react';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children }) => {
  const accessToken = localStorage.getItem('access');

  if (!accessToken) {
    return <Navigate to="/notFound" replace />;
  }

  return children;
};

export default ProtectedRoute;
