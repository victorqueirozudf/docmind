// src/components/common/Navbar.jsx
import React from "react";
import { useNavigate } from "react-router-dom";
import Logo from "../../assets/images/Logo.png";

const Navbar = ({ onLogout, user }) => {
  const navigate = useNavigate();

  return (
    <div className="sticky z-20 top-0 flex items-center justify-between bg-black text-white px-5 py-3 h-1/6 caret-transparent">
      {/* Logo */}
      <img
        src={Logo}
        alt="Logo"
        className="custom-navbar-logo-size cursor-pointer"
        onClick={() => navigate("/")} // Navega para a página inicial ao clicar no logo
      />

      {/* Botões */}
      <div className="flex items-center gap-4">
        {/* Botão de administrador (só aparece para superusuários) */}
        {user?.is_superuser && (
          <button
            onClick={() => navigate("/admin")} // Navega para a página de administração
            className="text-white bg-blue-500 px-4 py-2 rounded-lg hover:bg-blue-600 transition"
          >
            Administração
          </button>
        )}

        {/* Botão de logout */}
        <button
          onClick={onLogout}
          className="text-white hover:text-gray-400"
          title="Logout"
        >
          <svg
            className="h-5 w-5"
            xmlns="http://www.w3.org/2000/svg"
            fill="currentColor"
            viewBox="0 0 512 512"
          >
            <path d="M377.9 105.9L500.7 228.7c7.2 7.2 11.3 17.1 11.3 27.3s-4.1 20.1-11.3 27.3L377.9 406.1c-6.4 6.4-15 9.9-24 9.9c-18.7 0-33.9-15.2-33.9-33.9l0-62.1-128 0c-17.7 0-32-14.3-32-32l0-64c0-17.7 14.3-32 32-32l128 0 0-62.1c0-18.7 15.2-33.9 33.9-33.9c9 0 17.6 3.6 24 9.9zM160 96L96 96c-17.7 0-32 14.3-32 32l0 256c0 17.7 14.3 32 32 32l64 0c17.7 0 32 14.3 32 32s-14.3 32-32 32l-64 0c-53 0-96-43-96-96L0 128C0 75 43 32 96 32l64 0c17.7 0 32 14.3 32 32s-14.3 32-32 32z" />
          </svg>
        </button>
      </div>
    </div>
  );
};

export default Navbar;
