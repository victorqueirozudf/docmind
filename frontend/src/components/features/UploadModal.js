// src/components/UploadModal.jsx
import React, { useState } from 'react';

function UploadModal({ showModal, onClose, onCreateChat }) {
  const [chatName, setChatName] = useState('');
  const [files, setFiles] = useState([]);

  const handleFileChange = (event) => {
    const selectedFiles = Array.from(event.target.files);
    setFiles(selectedFiles);
  };

  const handleCreateChat = () => {
    onCreateChat(chatName, files);
    onClose();
    setChatName('');
    setFiles([]);
  };

  if (!showModal) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50">
      <div className="flex flex-col gap-5 bg-white rounded-lg w-2/5 p-6 relative">
        <div className='flex items-center justify-between'>
          <h2 className="text-2xl font-bold">Novo Chat</h2>
          <button
            onClick={onClose}
            className="absolute top-3 right-3 text-gray-500 hover:text-black"
          >
            <svg className="w-5 h-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
        </div>

        <hr />

        {/* Campo para o nome do chat */}
        <div className='flex flex-col gap-1'>
          <label className="block text-black font-semibold mb-2">Nome do Chat:</label>
          <input
            type="text"
            value={chatName}
            onChange={(e) => setChatName(e.target.value)}
            placeholder="Digite o nome aqui..."
            className="w-full px-4 py-2 mb-4 border rounded-lg bg-gray-100 focus:outline-none focus:border-gray-300"
            required
          />
        </div>

        {/* Área de upload de arquivos */}
        <div className="w-full border-2 border-dashed border-gray-300 rounded-lg p-6 text-center mb-4">
          <input 
            type="file" 
            onChange={handleFileChange} 
            className="hidden" 
            id="fileUpload" 
            multiple // Permite múltiplos arquivos
            accept=".pdf" // Limita às extensões PDF
            required
          />
          <label htmlFor="fileUpload" className="cursor-pointer text-gray-500 hover:text-gray-700">
            <svg className="w-10 h-10 mx-auto mb-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v4a2 2 0 002 2h12a2 2 0 002-2v-4m-4-4l-4-4m0 0l-4 4m4-4v12" />
            </svg>
            {files.length > 0 
              ? files.map((file) => file.name).join(', ')
              : 'Click or drag files to this area to upload'}
          </label>
        </div>

        {/* Botão para criar o novo chat */}
        <button
          onClick={handleCreateChat}
          className="w-2/5 py-2 self-center bg-black text-white rounded-lg font-semibold hover:bg-gray-800"
        >
          + Novo Chat
        </button>
      </div>
    </div>
  );
}

export default UploadModal;
