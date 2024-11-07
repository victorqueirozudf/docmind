// Register.js
import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';  // Importar useNavigate para redirecionamento

export const SignUp = () => {
    const [formData, setFormData] = useState({
        username: '',
        password: ''
    });

    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);
    const navigate = useNavigate();  // Inicializar o hook useNavigate

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('http://localhost:8000/authentication/signup/', formData);
            if (response.status === 201) {
                setSuccess(true);
                setError('');
                navigate('/login');  // Redireciona para a página de login após o sucesso
            }
        } catch (err) {
            setError('Erro ao registrar. Verifique os dados e tente novamente.');
        }
    };

    return (
        <div>
            <h2>Registrar-se</h2>
            {success ? (
                <p>Usuário registrado com sucesso! Redirecionando para o login...</p>
            ) : (
                <form onSubmit={handleSubmit}>
                    <div>
                        <label>Nome de usuário:</label>
                        <input
                            type="text"
                            name="username"
                            value={formData.username}
                            onChange={handleChange}
                            required
                        />
                    </div>
                    <div>
                        <label>Senha:</label>
                        <input
                            type="password"
                            name="password"
                            value={formData.password}
                            onChange={handleChange}
                            required
                        />
                    </div>
                    {error && <p style={{ color: 'red' }}>{error}</p>}
                    <button type="submit">Registrar</button>
                </form>
            )}
        </div>
    );
}
