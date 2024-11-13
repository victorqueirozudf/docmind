import React from 'react';
import '../index.css'
import { Link, useNavigate } from 'react-router-dom';
import Logo from '../images/Logo.png'

function Login() {
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    // Lógica de autenticação aqui
    navigate('/chat');
  };

  return (
    <div className="flex min-h-screen">
      {/* Left side - Logo and text */}
      <div className="flex flex-col items-center justify-center w-2/5 bg-black text-white p-8">
        <div className="text-center">
          <img src={Logo} alt="Logo" className="mb-4 mx-auto custom-logo-size" /> {/* Adicione o caminho da imagem */}
          <p className="text-lg font-light">A inteligência que transforma seu PDF.</p>
        </div>
      </div>

      {/* Right side - Login form */}
      <div className="flex items-center justify-center w-3/5 p-8 bg-white custom-padding">
        <div className="w-full max-w-lg">
          <h2 className="text-3xl font-extrabold text-center mb-6">LOGIN</h2>
          <form>
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="username">
                Usuário
              </label>
              <input
                type="text"
                id="username"
                placeholder="Usuário"
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-gray-500"
              />
            </div>
            <div className="mb-6">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="password">
                Senha
              </label>
              <input
                type="password"
                id="password"
                placeholder="Senha"
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-gray-500"
              />
            </div>
            <div className="text-center mb-6">
              <a href="/" className="text-sm font-medium text-blue-500 hover:underline">
                Esqueci senha
              </a>
            </div>
            <button
              type="submit"
              onSubmit={handleSubmit}
              className="w-full pt-3 pb-3 font-semibold bg-black text-white py-2 rounded hover:bg-gray-800 transition duration-300"
            >
              ACESSAR
            </button>
          </form>
          <p className="mt-6 text-center font-semibold text-gray-700">
            Não possui conta? <Link to="/cadastrar" className="text-blue-500 hover:underline">Criar Conta</Link>
          </p>
        </div>
      </div>
    </div>
  );
}

export default Login;
