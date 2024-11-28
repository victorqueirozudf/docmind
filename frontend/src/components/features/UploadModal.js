import React, { useState } from 'react';

function UploadModal({ showModal, onClose, onCreateChat }) {
  const [chatName, setChatName] = useState('');
  const [files, setFiles] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  // Lida com arquivos selecionados ou arrastados
  const handleFiles = (selectedFiles) => {
    if (selectedFiles && selectedFiles.length > 0) {
      const fileArray = Array.from(selectedFiles);
      setFiles(fileArray); // Substitui os arquivos existentes pelos novos
    }
  };

  const handleCreateChat = () => {
    // Verifica se o nome do chat e arquivos foram fornecidos
    if (!chatName.trim() || files.length === 0) {
      setErrorMessage('Por favor, forneça um nome para o chat e selecione pelo menos um arquivo.');
      return;
    }

    // Se tudo estiver correto, chama a função e fecha a modal
    onCreateChat(chatName, files);
    onClose();
    setChatName('');
    setFiles([]);
    setErrorMessage(''); // Limpa a mensagem de erro
  };

  // Eventos de drag-and-drop
  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true); // Estilo ao arrastar
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false); // Remove o estilo ao sair
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false); // Remove o estilo ao soltar
    if (e.dataTransfer && e.dataTransfer.files) {
      handleFiles(e.dataTransfer.files); // Lida com arquivos arrastados
    }
  };

  const handleFileChange = (e) => {
    if (e.target && e.target.files) {
      handleFiles(e.target.files); // Lida com arquivos selecionados via input
    }
  };

  if (!showModal) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50">
      <div className="flex flex-col gap-5 bg-white rounded-lg w-2/5 p-5 relative">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold">Novo Chat</h2>
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

        <p className=" text-black mb-6">ATENÇÃO: o nosso sistema utiliza de sistema terceiros para realizar o processamento do documento. Portanto, caso seu documento possua dados sensíveis, recomendando não utilizar este sistema.</p>

        {/* Exibe mensagem de erro, se houver */}
        {errorMessage && (
          <p className="text-red-500 text-sm mb-4">{errorMessage}</p>
        )}

        {/* Botão para criar o novo chat */}
        <button
          onClick={handleCreateChat}
          className={`w-2/5 py-2 self-center rounded-lg font-semibold text-white ${
            chatName.trim() && files.length > 0
              ? 'bg-black hover:bg-gray-800'
              : 'bg-black hover:bg-gray-800'
          }`}
          disabled={!chatName.trim() || files.length === 0} // Desativa se não atender os requisitos
        >
          + Novo Chat
        </button>
      </div>
    </div>
  );
}

export default UploadModal;
