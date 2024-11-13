import React, { useState } from 'react';
import '../index.css';
import Logo from '../images/Logo.png';
import UploadModal from './UploadModal'; // Importe o modal
import DeleteModal from './DeleteModal'

function ChatInterface() {
  const [chats, setChats] = useState([
    { id: 1, title: 'Resumo sobre currículo' },
    { id: 2, title: 'Dúvidas sobre um documento' },
    { id: 3, title: 'Dúvidas sobre um documento' },
    { id: 4, title: 'Resumo sobre currículo' },
  ]);
  const [selectedChat, setSelectedChat] = useState(null);
  const [dropdownOpen, setDropdownOpen] = useState(null); 
  const [showModal, setShowModal] = useState(false); // Estado para controlar a visibilidade do modal
  const [showDeleteModal, setShowDeleteModal] = useState(false)

  const handleNewChat = () => {
    setShowModal(true); // Abre o modal
  };

  const handleCloseModal = () => {
    setShowModal(false); // Fecha o modal
  };

  const handleDeleteChat = () => {
    setShowDeleteModal(false); // Abre o modal
  };

  const handleCloseDeleteModal = () => {
    setShowDeleteModal(true); // Fecha o modal
  };

  const handleCreateChat = (chatName, file) => {
    // Lógica para criar um novo chat com o nome e arquivo
    const newChat = { id: chats.length + 1, title: chatName };
    setChats([...chats, newChat]);
    setSelectedChat(newChat);
    setShowModal(false); // Fecha o modal após criar o chat
  };

  const handleSelectChat = (chat) => {
    setSelectedChat(chat);
  };

  const toggleDropdown = (id) => {
    setDropdownOpen(dropdownOpen === id ? null : id);
  };

  const handleUpdateChat = (chat) => {
    alert(`Atualizar chat: ${chat.title}`);
  };

  return (
    <div className="flex flex-col min-h-screen">
      {/* Navbar */}
      <div className="flex items-center justify-between bg-black text-white p-4">
        <img src={Logo} alt="Logo" className="custom-navbar-logo-size" />
        <button className="material-icons text-white hover:text-gray-400">logout</button>
      </div>

      <div className="flex flex-1">
        {/* Sidebar */}
        <div className="w-72 bg-gray-100 p-5 border-r border-gray-300">
          <div className="flex items-center mb-8">
            <span className="font-semibold text-lg">Olá, {`{Nome do Usuário}`} :)</span>
          </div>
          <button
            onClick={handleNewChat} // Abre o modal ao clicar
            className="w-full py-2 mb-4 bg-black text-white rounded-lg font-semibold hover:bg-gray-800"
          >
            + Novo Chat
          </button>
          <div onClick={() => setDropdownOpen(null)}>
            <p className="text-gray-600 font-medium mb-2">Suas conversas</p>
            <ul>
              {chats.map((chat) => (
                <li
                  key={chat.id}
                  className={`flex items-center justify-between p-2 cursor-pointer rounded-lg mb-2 relative group ${
                    selectedChat && selectedChat.id === chat.id ? 'bg-gray-300' : 'hover:bg-gray-200'
                  }`}
                  onClick={(e) => e.stopPropagation()} 
                >
                  <div onClick={() => handleSelectChat(chat)} className="w-full flex items-center flex-1">
                    <svg className="h-5 m-3" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
                      <path d="M123.6 391.3c12.9-9.4 29.6-11.8 44.6-6.4c26.5 9.6 56.2 15.1 87.8 15.1c124.7 0 208-80.5 208-160s-83.3-160-208-160S48 160.5 48 240c0 32 12.4 62.8 35.7 89.2c8.6 9.7 12.8 22.5 11.8 35.5c-1.4 18.1-5.7 34.7-11.3 49.4c17-7.9 31.1-16.7 39.4-22.7zM21.2 431.9c1.8-2.7 3.5-5.4 5.1-8.1c10-16.6 19.5-38.4 21.4-62.9C17.7 326.8 0 285.1 0 240C0 125.1 114.6 32 256 32s256 93.1 256 208s-114.6 208-256 208c-37.1 0-72.3-6.4-104.1-17.9c-11.9 8.7-31.3 20.6-54.3 30.6c-15.1 6.6-32.3 12.6-50.1 16.1c-.8 .2-1.6 .3-2.4 .5c-4.4 .8-8.7 1.5-13.2 1.9c-.2 0-.5 .1-.7 .1c-5.1 .5-10.2 .8-15.3 .8c-6.5 0-12.3-3.9-14.8-9.9c-2.5-6-1.1-12.8 3.4-17.4c4.1-4.2 7.8-8.7 11.3-13.5c1.7-2.3 3.3-4.6 4.8-6.9l.3-.5z" />
                    </svg>
                    <span className="truncate">{chat.title}</span>
                  </div>
                  
                  {/* Botão de opções centralizado verticalmente no final do chat */}
                  <div className="absolute right-0 top-1/2 transform -translate-y-1/2"> {/* Alinha à direita e centraliza verticalmente */}
                    <button
                      onClick={() => toggleDropdown(chat.id)}
                      className="text-gray-600 hover:text-black ml-2 hidden group-hover:block"
                      aria-haspopup="true"
                      aria-expanded={dropdownOpen === chat.id}
                    >
                      <svg className="w-5 h-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512">
                        <path d="M8 256a56 56 0 1 1 112 0A56 56 0 1 1 8 256zm160 0a56 56 0 1 1 112 0 56 56 0 1 1 -112 0zm216-56a56 56 0 1 1 0 112 56 56 0 1 1 0-112z" />
                      </svg>
                    </button>
                    
                    {dropdownOpen === chat.id && (
                      <div className="absolute bg-white border rounded-lg shadow-md left-6 top-1 mt-2 w-32">
                        <button
                          onClick={() => handleUpdateChat(chat)}
                          className="block w-full text-left px-4 py-2 text-sm hover:bg-gray-100"
                        >
                          Atualizar
                        </button>
                        <button
                          onClick={() => handleDeleteChat(chat.id)}
                          className="block w-full text-left px-4 py-2 text-sm hover:bg-gray-100"
                        >
                          Apagar
                        </button>
                      </div>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex flex-col w-full bg-white p-8">
          <div className="flex items-center justify-between border-b pb-4 mb-4">
            <h2 className="text-2xl font-extrabold">
              {selectedChat ? selectedChat.title : 'Sem conversa selecionada'}
            </h2>
          </div>
          <div className="flex-1 flex items-center justify-center text-center">
            {selectedChat ? (
              <div className="w-full">
                <p className="text-gray-500">Converse com o chatbot...</p>
              </div>
            ) : (
              <div className="text-center">
                <h3 className="font-extrabold text-4xl mb-4 text-black">Sem conversa selecionada</h3>
                <p className="font-semibold text-base text-gray-500 mt-2">
                  Selecione uma conversa já criada, clique em Novo Chat, ou{' '}
                  <span className="cursor-pointer underline">clique aqui</span> para criar um novo chat.
                </p>
              </div>
            )}
          </div>
          <div className="mt-4 border-t pt-4 relative flex items-center">
            <input
              type="text"
              placeholder="Type your message..."
              className="h-12 flex-1 px-4 py-2 pr-12 border rounded-xl focus:outline-none focus:border-gray-400"
            />
            <button className="absolute right-3 text-black hover:text-black">
              <svg 
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 512 512"
                className="w-6 h-6"
                fill="currentColor"
              >
                <path d="M0 256a256 256 0 1 0 512 0A256 256 0 1 0 0 256zM241 377c-9.4 9.4-24.6 9.4-33.9 0s-9.4-24.6 0-33.9l87-87-87-87c-9.4-9.4-9.4-24.6 0-33.9s24.6-9.4 33.9 0L345 239c9.4 9.4 9.4 24.6 0 33.9L241 377z"/>
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Modal de Upload */}
      <UploadModal
        showModal={showModal}
        onClose={handleCloseModal}
        onCreateChat={handleCreateChat}
      />

      <DeleteModal
        showModal={showDeleteModal}
        onClose={handleCloseDeleteModal}
        
      />
    </div>
    
  );
}

export default ChatInterface;
