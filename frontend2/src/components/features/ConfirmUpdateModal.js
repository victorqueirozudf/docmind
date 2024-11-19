import React from 'react';

const ConfirmUpdateModal = ({ onConfirm, onCancel }) => {
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
      <div className="bg-white rounded-lg shadow-lg p-6 w-80 max-w-md relative">
        <button
          onClick={onCancel}
          className="absolute top-3 right-3 text-gray-500 hover:text-black"
        >
          <svg className="w-5 h-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
            <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </button>
        <h2 className="text-lg font-bold text-center mb-4">Confirmar atualização</h2>
        <p className="text-center text-gray-700 mb-6">Tem certeza que deseja atualizar o chat?</p>
        <div className="flex items-center justify-center gap-4">
          <button
            onClick={onConfirm}
            className="bg-black text-white py-2 px-6 rounded-lg hover:bg-gray-800 transition-colors"
          >
            Sim
          </button>
          <button
            onClick={onCancel}
            className="border border-gray-400 py-2 px-6 rounded-lg hover:bg-gray-100 transition-colors"
          >
            Não
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmUpdateModal;
