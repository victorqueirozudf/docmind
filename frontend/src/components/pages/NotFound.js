import React from "react";
import { useNavigate } from "react-router-dom";
import Logo from "../../assets/images/Logo.png";

function NotFound() {
    const navigate = useNavigate();
    
    return(
        <>
        <div className="sticky z-20 top-0 flex items-center justify-between bg-black text-white px-5 py-3 h-2/6">
            {/* Logo */}
            <img
                src={Logo}
                alt="Logo"
                className="custom-navbar-logo-size cursor-pointer caret-transparent"
                onClick={() => navigate("/")} // Navega para a página inicial ao clicar no logo
            />
        </div>

        <div className="flex justify-center items-center w-full h-4/6">
            <h1 className="font-bold text-9xl">Tela não encontrada</h1>
        </div>
        </>
    )
}

export default NotFound