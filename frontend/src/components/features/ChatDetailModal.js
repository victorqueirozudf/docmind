import React from "react";

function ChatDetailModal({ showModal, onClose, chatDetails }) {
  if (!showModal) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg w-1/3 p-6 relative shadow-lg">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-600 hover:text-black"
        >
          ✖
        </button>
        <h2 className="text-2xl font-bold mb-4">Detalhes do Chat</h2>

        <div className="space-y-3">
          <div>
            <p className="font-semibold">Nome do Chat:</p>
            <p className="text-gray-700">{chatDetails.chatName}</p>
          </div>

          <div>
            <p className="font-semibold">Data de Criação:</p>
            <p className="text-gray-700">
              {new Date(chatDetails.created_at).toLocaleString()}
            </p>
          </div>

          <div>
            <p className="font-semibold">Documentos:</p>
            {chatDetails.file_names?.length > 0 ? (
              <ul className="list-disc pl-5 text-gray-700">
                {chatDetails.file_names.map((file, index) => (
                  <li key={index}>{file}</li>
                ))}
              </ul>
            ) : (
              <p className="text-gray-500">Nenhum documento encontrado.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ChatDetailModal;