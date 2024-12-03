import React, { useState, useEffect } from 'react';
import '../../index.css';
import { Link, useNavigate } from 'react-router-dom';
import Logo from '../../assets/images/Logo.png';
import { authAPI } from '../../axios';

function Register() {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Redireciona para o chat se o usuário já estiver logado
  useEffect(() => {
    const token = localStorage.getItem('access');
    if (token) {
      navigate('/chat');
    }
  }, [navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validação de senha e nome de usuário
    if (/\s/.test(username)) {
      setErrorMessage('O nome de usuário não pode conter espaços.');
      return;
    }
    if (password !== confirmPassword) {
      setErrorMessage('As senhas não coincidem.');
      return;
    }

    setErrorMessage('');
    setIsSubmitting(true);

    try {
      await authAPI.signup({ username, password });
      window.alert('Usuário registrado com sucesso. Bem-vindo(a)!');
      navigate('/login');
    } catch (error) {
      setErrorMessage('Erro ao registrar. Verifique as informações e tente novamente.');
      console.error('Erro ao registrar:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen">
      {/* Lado esquerdo - Logo e texto */}
      <div className="flex flex-col items-center justify-center w-2/5 bg-black text-white p-8">
        <div className="text-center">
          <img src={Logo} alt="Logo" className="mb-4 mx-auto custom-logo-size" />
          <p className="text-lg font-light">A inteligência que transforma seu PDF.</p>
        </div>
      </div>

      {/* Lado direito - Formulário de Cadastro */}
      <div className="flex items-center justify-center w-3/5 p-8 bg-white custom-padding">
        <div className="w-full max-w-lg">
          <h2 className="text-3xl font-extrabold text-center mb-6">CRIAR CONTA</h2>
          <form onSubmit={handleSubmit}>
            {/* Campo Usuário */}
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="username">
                Usuário
              </label>
              <input
                type="text"
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Usuário"
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-gray-500"
                required
              />
            </div>

            {/* Campo Senha */}
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="password">
                Senha
              </label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Senha"
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-gray-500"
                required
              />
            </div>

            {/* Campo Confirmar Senha */}
            <div className="mb-6">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="confirmPassword">
                Confirmar Senha
              </label>
              <input
                type="password"
                id="confirmPassword"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Senha"
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-gray-500"
                required
              />
            </div>

            {/* Mensagem de Erro */}
            {errorMessage && <p className="text-red-500 text-sm mb-4">{errorMessage}</p>}

            {/* Botão de Registro */}
            <button
              type="submit"
              className={`w-full pt-3 pb-3 font-semibold text-white py-2 rounded transition duration-300 ${
                isSubmitting ? 'bg-gray-500' : 'bg-black hover:bg-gray-800'
              }`}
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Cadastrando...' : 'Cadastrar'}
            </button>
          </form>
          <p className="mt-6 text-center font-semibold text-gray-700">
            Já possui conta? <Link to="/" className="text-blue-500 hover:underline">Fazer login</Link>
          </p>
        </div>
      </div>
    </div>
  );
}

export default Register;
