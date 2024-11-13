// src/components/UploadModal.jsx
import React, { useState } from 'react';

function UploadModal({ showModal, onClose, onCreateChat }) {
  const [chatName, setChatName] = useState('');
  const [file, setFile] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleCreateChat = () => {
    onCreateChat(chatName, file);
    onClose();
    setChatName('');
    setFile(null);
  };

  if (!showModal) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg w-full max-w-md p-6 relative">
        <button
          onClick={onClose}
          className="absolute top-3 right-3 text-2xl font-bold text-gray-500 hover:text-black"
        >
          &times;
        </button>
        <h2 className="text-2xl font-bold mb-4">NOVO CHAT</h2>
        <hr className="mb-4" />

        {/* Campo para o nome do chat */}
        <label className="block text-gray-700 font-semibold mb-2">Nome do Chat:</label>
        <input
          type="text"
          value={chatName}
          onChange={(e) => setChatName(e.target.value)}
          placeholder="Digite o nome aqui..."
          className="w-full px-4 py-2 mb-4 border rounded-lg bg-gray-100 focus:outline-none focus:border-gray-300"
        />

        {/* Área de upload de arquivo */}
        <div className="w-full border-2 border-dashed border-gray-300 rounded-lg p-6 text-center mb-4">
          <input type="file" onChange={handleFileChange} className="hidden" id="fileUpload" />
          <label htmlFor="fileUpload" className="cursor-pointer text-gray-500 hover:text-gray-700">
            <svg className="w-10 h-10 mx-auto mb-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v4a2 2 0 002 2h12a2 2 0 002-2v-4m-4-4l-4-4m0 0l-4 4m4-4v12" />
            </svg>
            {file ? file.name : 'Click or drag file to this area to upload'}
          </label>
        </div>

        {/* Botão para criar o novo chat */}
        <button
          onClick={handleCreateChat}
          className="w-full py-2 bg-black text-white rounded-lg font-semibold hover:bg-gray-800"
        >
          + Novo Chat
        </button>
      </div>
    </div>
  );
}

export default UploadModal;
