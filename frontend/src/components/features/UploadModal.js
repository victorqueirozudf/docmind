import React, { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faSpinner } from '@fortawesome/free-solid-svg-icons'

function UploadModal({ showModal, onClose, onCreateChat }) {
  const [chatName, setChatName] = useState('');
  const [files, setFiles] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [isProcessing, setIsProcessing] = useState(false); // Estado de processamento

  const handleFiles = (selectedFiles) => {
    if (selectedFiles && selectedFiles.length > 0) {
      const fileArray = Array.from(selectedFiles);
      setFiles(fileArray);
    }
  };

  const handleCreateChat = async () => {
    if (!chatName.trim() || files.length === 0) {
      setErrorMessage('Por favor, forneça um nome para o chat e selecione pelo menos um arquivo.');
      return;
    }

    setIsProcessing(true); // Inicia o estado de processamento

    try {
      await onCreateChat(chatName, files); // Aguarda o backend processar
      setChatName('');
      setFiles([]);
      setErrorMessage('');
      window.alert("Seu chat foi criado com sucesso! ")
      onClose(); // Fecha a modal após o processamento
    } catch (error) {
      setErrorMessage('Erro ao processar o chat. Tente novamente.');
    } finally {
      setIsProcessing(false); // Finaliza o estado de processamento
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer && e.dataTransfer.files) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleFileChange = (e) => {
    if (e.target && e.target.files) {
      handleFiles(e.target.files);
    }
  };

  if (!showModal) return null;

  return (
    <div
      className={`fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 transition-opacity duration-300 ${
        showModal ? 'opacity-100' : 'opacity-0'
      }`}
    >
      <div className="flex flex-col gap-5 bg-white rounded-lg w-2/5 p-5 relative">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold">Novo Chat</h2>
          <button onClick={onClose} className="absolute top-3 right-3 text-gray-500 hover:text-black">
            <svg
              className="w-7 h-7"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="currentColor"
            >
              <path
                d="M18 6L6 18M6 6l12 12"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
        </div>

        <hr />

        <div className="flex flex-col gap-1">
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

        <div
          className={`w-full border-2 border-dashed rounded-lg p-6 text-center mb-4 ${
            isDragging ? 'border-black bg-blue-100' : 'border-gray-300'
          }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <input
            type="file"
            onChange={handleFileChange}
            className="hidden"
            id="fileUpload"
            multiple
            accept=".pdf"
          />
          <label htmlFor="fileUpload" className="cursor-pointer text-gray-500 hover:text-gray-700">
            <svg
              className="w-10 h-10 mx-auto mb-2"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 16v4a2 2 0 002 2h12a2 2 0 002-2v-4m-4-4l-4-4m0 0l-4 4m4-4v12"
              />
            </svg>
            {files.length > 0
              ? files.map((file) => file.name).join(', ')
              : 'Clique ou arraste arquivos para atualizar'}
          </label>
        </div>

        <p className="text-black mb-6">
          ATENÇÃO: o nosso sistema utiliza de sistema terceiros para realizar o processamento do
          documento. Portanto, caso seu documento possua dados sensíveis, recomendando não utilizar
          este sistema.
        </p>

        {errorMessage && <p className="text-red-500 text-sm mb-4">{errorMessage}</p>}

        <button
          onClick={handleCreateChat}
          className={`w-2/5 py-2 self-center rounded-lg font-semibold text-white flex justify-center items-center ${
            chatName.trim() && files.length > 0 ? 'bg-black hover:bg-gray-800' : 'bg-gray-500'
          }`}
          disabled={!chatName.trim() || files.length === 0 || isProcessing}
        >
          {isProcessing ? (
            <div className="flex items-center gap-2">
              <span>Processando...</span>
              <FontAwesomeIcon icon={faSpinner} spinPulse />
            </div>
          ) : (
            '+ Novo Chat'
          )}
        </button>
      </div>
    </div>
  );
}

export default UploadModal;