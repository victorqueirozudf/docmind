import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './components/pages/Login';
import Register from './components/pages/Register';
import Chat from './components/pages/Chat';
import ProtectedRoute from './ProtectedRoute';
import NotFound from './components/pages/NotFound'
import AdminDashboard from './components/pages/AdminDashboard';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/notFound" element={<NotFound/>}/>
        <Route
          path="/chat"
          element={
            <ProtectedRoute>
              <Chat/>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin"
          element={
            <ProtectedRoute>
              <AdminDashboard/>
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;

