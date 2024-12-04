import React, { useState, useEffect } from 'react';
import '../../index.css';
import { Link, useNavigate } from 'react-router-dom';
import Logo from '../../assets/images/Logo.png';
import CryptoJS from 'crypto-js';
import { authAPI } from '../../axios.js';
import ForgotPasswordModal from '../features/ForgotPasswordModal.js';

function Login() {
  const navigate = useNavigate();

  // Variáveis de estado para usuário, senha e mensagens de erro
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [showForgotPasswordModal, setShowForgotPasswordModal] = useState(false);

  // Redireciona para o chat se o usuário já estiver logado
  useEffect(() => {
    const token = localStorage.getItem('access');
    if (token) {
      navigate('/chat'); // Redireciona para o chat
    }
  }, [navigate]);

  const handleSubmit = (e) => {
    e.preventDefault();

    // Verificar se as variáveis de ambiente estão definidas
    const keyString = process.env.REACT_APP_KEY_CRYPTOGRAPHY;
    const ivString = process.env.REACT_APP_IV_CRYPTOGRAPHY;

    if (!keyString || !ivString) {
      setErrorMessage('Configuração de criptografia ausente.');
      return;
    }

    try {
      // Converter strings de chave e IV para formato correto
      const key = CryptoJS.enc.Utf8.parse(keyString);
      const iv = CryptoJS.enc.Utf8.parse(ivString);

      // Criptografar a senha
      const encryptedPassword = CryptoJS.AES.encrypt(password, key, {
        iv: iv,
        mode: CryptoJS.mode.CBC,
        padding: CryptoJS.pad.Pkcs7,
      }).toString();
      
      // Dados para login
      const loginData = { 
        username: username,
        password: encryptedPassword,
      };

      // Realizar a requisição de login
      authAPI
        .login(loginData)
        .then((response) => {
          // Salvar tokens no localStorage
          localStorage.setItem('access', response.data.access);
          localStorage.setItem('refresh', response.data.refresh);

          // Salvar session ID se fornecido
          if (response.data.sessionid) {
            localStorage.setItem('sessionid', response.data.sessionid);
          }
          
          window.alert("Login realizado com sucesso!");

          // Navegar para a página de chat
          navigate('/chat');
        })
        .catch((error) => {
          // Tratar erros
          if (error.response) {
            // Erro retornado pelo servidor
            if (error.response.status === 401) {
              setErrorMessage('Credenciais inválidas. Por favor, tente novamente.');
            } else {
              setErrorMessage('Ocorreu um erro. Por favor, tente novamente mais tarde.');
            }
          } else if (error.request) {
            // Nenhuma resposta recebida
            setErrorMessage('Sem resposta do servidor. Verifique sua conexão.');
          } else {
            // Outros erros
            setErrorMessage('Ocorreu um erro. Por favor, tente novamente.');
          }
        });
    } catch (error) {
      // Tratar erros de criptografia
      setErrorMessage('Erro ao criptografar a senha.');
      console.error('Erro de criptografia:', error);
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

      {/* Lado direito - Formulário de login */}
      <div className="flex items-center justify-center w-3/5 p-8 bg-white custom-padding">
        <div className="w-full max-w-lg">
          <h2 className="text-3xl font-extrabold text-center mb-6">LOGIN</h2>
          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="username">
                Usuário
              </label>
              <input
                type="text"
                id="username"
                placeholder="Usuário"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-gray-500"
                required
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
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-gray-500"
                required
              />
            </div>
            {errorMessage && (
              <p className="text-red-500 mb-4">{errorMessage}</p>
            )}
            <div className="text-center mb-6">
              <button
                onClick={() => setShowForgotPasswordModal(true)}
                className="text-blue-500 font-semibold hover:underline"
                type="button"
              >
                Esqueceu a senha?
              </button>
            </div>
            <button
              type="submit"
              className="w-full pt-3 pb-3 font-semibold bg-black text-white py-2 rounded hover:bg-gray-800 transition duration-300"
            >
              ACESSAR
            </button>
          </form>
          <p className="mt-6 text-center font-semibold text-gray-700">
            Não possui conta? <Link to="/register" className="text-blue-500 hover:underline">Criar Conta</Link>
          </p>
        </div>
      </div>

      {/* Renderiza a modal de "Esqueceu a senha" */}
      <ForgotPasswordModal
        showModal={showForgotPasswordModal}
        onClose={() => setShowForgotPasswordModal(false)}
      />
    </div>
  );
}

export default Login;
