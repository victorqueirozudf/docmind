import React, { useState } from 'react';
import ConfirmUpdateModal from './ConfirmUpdateModal';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faSpinner } from '@fortawesome/free-solid-svg-icons'

function UpdateChatModal({ showModal, onClose, onUpdateChat, initialChatName, threadId }) {
  const [chatName, setChatName] = useState(initialChatName || '');
  const [files, setFiles] = useState([]);
  const [showConfirmationModal, setShowConfirmationModal] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleFileChange = (event) => {
    const selectedFiles = Array.from(event.target.files);
    setFiles(selectedFiles);
  };

  const handleUpdateChat = async () => {
    if (!chatName.trim() || files.length === 0) return;
  
    setIsProcessing(true);
  
    try {
      const formData = new FormData();
      formData.append('chat_name', chatName);
      if (files.length > 0) {
        files.forEach((file) => formData.append('pdfs', file));
      }
  
      await onUpdateChat(threadId, formData); // Aguarda o backend processar
      setChatName('');
      setFiles([]);
      setShowConfirmationModal(false); // Fecha a modal de confirmação
      onClose(); // Fecha a modal principal após o processamento
    } catch (error) {
      console.error('Erro ao atualizar o chat:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  if (!showModal) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50">
      <div className="flex flex-col gap-5 bg-white rounded-lg w-2/5 p-5 relative">
        {/* Cabeçalho */}
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold">Atualizar Chat</h2>
          <button
            onClick={onClose}
            className="absolute top-3 right-3 text-gray-500 hover:text-black"
          >
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

        {/* Campo para o nome do chat */}
        <div className="flex flex-col gap-1">
          <label className="block text-gray-700 font-semibold mb-2">Nome do Chat:</label>
          <input
            type="text"
            value={chatName}
            onChange={(e) => setChatName(e.target.value)}
            placeholder="Atualize o nome do chat..."
            className="w-full px-4 py-2 mb-4 border rounded-lg bg-gray-100 focus:outline-none focus:border-gray-300"
          />
        </div>

        {/* Área de upload de arquivos */}
        <div className="w-full border-2 border-dashed border-gray-300 rounded-lg p-6 text-center mb-4">
          <input
            type="file"
            onChange={handleFileChange}
            className="hidden"
            id="fileUploadUpdate"
            multiple
            accept=".pdf"
          />
          <label
            htmlFor="fileUploadUpdate"
            className="cursor-pointer text-gray-500 hover:text-gray-700"
          >
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

        {/* Botão para confirmar a atualização */}
        <button
          onClick={() => setShowConfirmationModal(true)}
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
            'Atualizar Chat'
          )}
        </button>
      </div>

      {/* Modal de Confirmação */}
      {showConfirmationModal && (
        <ConfirmUpdateModal
          onConfirm={() => {
            handleUpdateChat(); // Chama a função de atualização
            setShowConfirmationModal(false); // Fecha a modal de confirmação explicitamente
          }}
          onCancel={() => setShowConfirmationModal(false)}
        />
      )}
    </div>
  );
}

export default UpdateChatModal;