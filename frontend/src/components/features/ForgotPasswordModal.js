import React from "react";

function ForgotPasswordModal({ showModal, onClose }) {
  if (!showModal) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg w-1/3 p-6 relative shadow-lg">
        {/* Botão para fechar a modal */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-600 hover:text-black"
        >
          ✖
        </button>
        <h2 className="text-2xl font-bold mb-4 text-black text-center">
          Esqueceu a senha?
        </h2>
        <p className="text-gray-700 text-center">
          Para redefinir sua senha, entre em contato com o administrador do sistema.
        </p>
        <p className="text-gray-700 text-center mt-4">
          <strong>Email do Administrador:</strong> 
          <span className="text-blue-500"> admin@admin.com</span>
        </p>
        <div className="flex justify-center mt-6">
          <button
            onClick={onClose}
            className="bg-black text-white px-4 py-2 rounded-lg hover:bg-gray-800"
          >
            Fechar
          </button>
        </div>
      </div>
    </div>
  );
}

export default ForgotPasswordModal;