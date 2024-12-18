// src/components/common/Navbar.jsx
import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import Logo from "../../assets/images/Logo.png";
import ChangePasswordModal from "../features/ChangePasswordModal";
import { authAPI } from '../../axios'; // Certifique-se de importar authAPI


const Navbar = ({ user }) => { // Remova a prop onLogout
  const navigate = useNavigate();
  const [showChangePasswordModal, setShowChangePasswordModal] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null); // Referência para o dropdown

  const toggleDropdown = () => {
    setDropdownOpen(!dropdownOpen);
  };

  const handleLogout = () => { // Mova a função de logout para aqui
    const refreshToken = localStorage.getItem('refresh'); // Obtém o token de refresh

    if (!refreshToken) {
      window.alert("Ops, ocorreu um problema.");
      console.error('Token de refresh não encontrado.');
      localStorage.removeItem('access');
      localStorage.removeItem('refresh');
      localStorage.removeItem('sessionid');
      navigate('/login');
      return;
    }

    const logoutData = {
      refresh_token: refreshToken, // Dados para logout
    };

    authAPI
      .logout(logoutData) // Chama a API de logout
      .then((response) => {
        // Remove tokens do localStorage
        localStorage.removeItem('access');
        localStorage.removeItem('refresh');
        localStorage.removeItem('sessionid');
        window.alert("Logout realizado com sucesso. Até breve!");
        navigate('/login');
      })
      .catch((error) => {
        // Mesmo se o logout falhar, remove tokens e redireciona
        localStorage.removeItem('access');
        localStorage.removeItem('refresh');
        localStorage.removeItem('sessionid');

        navigate('/login');

        console.error('Erro ao fazer logout:', error);
      });
  };

  const handleClickOutside = (event) => {
    if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
      setDropdownOpen(false);
    }
  };

  useEffect(() => {
    if (dropdownOpen) {
      document.addEventListener("click", handleClickOutside);
    } else {
      document.removeEventListener("click", handleClickOutside);
    }

    return () => {
      document.removeEventListener("click", handleClickOutside);
    };
  }, [dropdownOpen]);

  return (
    <div className="sticky z-20 top-0 flex items-center justify-between bg-black text-white px-5 py-3 h-2/6">
      {/* Logo */}
      <img
        src={Logo}
        alt="Logo"
        className="custom-navbar-logo-size cursor-pointer caret-transparent"
        onClick={() => navigate("/chat")} // Navega para a página inicial ao clicar no logo
      />

      {/* Dropdown de ações */}
      <div className="relative caret-transparent" ref={dropdownRef}>
        <button
          onClick={toggleDropdown}
          className="flex items-center gap-2 rounded-md hover:underline focus:outline-none"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="currentColor" viewBox="0 0 512 512">
            <path d="M224 256A128 128 0 1 0 224 0a128 128 0 1 0 0 256zm-45.7 48C79.8 304 0 383.8 0 482.3C0 498.7 13.3 512 29.7 512l388.6 0c16.4 0 29.7-13.3 29.7-29.7C448 383.8 368.2 304 269.7 304l-91.4 0z"/>
          </svg>
          {user?.username || "Usuário"}
          <svg
            className="h-4 w-4"
            xmlns="http://www.w3.org/2000/svg"
            fill="currentColor"
            viewBox="0 0 512 512"
          >
            <path d="M256 294.1c-14.6 0-28.3-6.4-37.8-17.5L119.1 173.8c-8.9-10.1-7.9-25.2 2.1-34.2s25.2-7.9 34.2 2.1l98.6 113.5l98.6-113.5c8.9-10.1 24-11.1 34.2-2.1s11.1 24 2.1 34.2l-98.6 113.5c-9.5 11.1-23.2 17.5-37.8 17.5z" />
          </svg>
        </button>

        {/* Dropdown Menu */}
        {dropdownOpen && (
          <div className="absolute right-0 mt-2 w-48 bg-white text-black border rounded-lg shadow-md z-50">
            {/* Administração (somente para superusuários) */}
            {user?.is_superuser && (
              <button
                onClick={() => {
                  navigate("/admin");
                  setDropdownOpen(false);
                }}
                className="block w-full text-left px-4 py-2 hover:underline"
              >
                Administração
              </button>
            )}
            
            {/* Alterar Senha */}
            <button
              onClick={() => {
                setShowChangePasswordModal(true);
                setDropdownOpen(false);
              }}
              className="block w-full text-left px-4 py-2 hover:underline"
            >
              Alterar Senha
            </button>

            {/* Logout */}
            <button
              onClick={handleLogout}
              className="block w-full text-left px-4 py-2 text-red-500 hover:underline"
            >
              Logout
            </button>
          </div>
        )}
      </div>

      {/* Modal de Alterar Senha */}
      <ChangePasswordModal
        showModal={showChangePasswordModal}
        onClose={() => setShowChangePasswordModal(false)}
      />
    </div>
  );
};

export default Navbar;
