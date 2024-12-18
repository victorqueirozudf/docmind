import React from 'react';

const DeleteChatModal = ({ chatName, onClose, onDelete }) => {
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
      <div className="bg-white rounded-lg shadow-lg p-5 w-1/3 relative">
        <button
          onClick={onClose}
          className="absolute top-3 right-3 text-gray-500 hover:text-black"
        >
          <svg className="w-7 h-7" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
            <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </button>
        <h2 className="text-xl font-bold mb-4">Excluir chat {chatName}</h2>
        <p className=" text-gray-700 mb-1">Deseja mesmo apagar o chat?</p>
        <p className=" text-gray-500 mb-6">Isso excluirá todo o histórico do chat.</p>
        <div className="flex items-center justify-center gap-4">
          <button
            onClick={onClose}
            className="py-2 px-6 rounded-lg hover:underline transition-colors"
          >
            Cancelar
          </button>
          <button
            onClick={onDelete}
            className="bg-black text-white py-2 px-6 rounded-lg hover:bg-gray-800 transition-colors"
          >
            Apagar
          </button>
        </div>
      </div>
    </div>
  );
};

export default DeleteChatModal;
