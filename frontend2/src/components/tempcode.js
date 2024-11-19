import React, { useState, useRef, useEffect } from 'react';
import '../index.css';
import Logo from '../images/Logo.png';
import UploadModal from './UploadModal'; // Importe o modal
import DeleteChatModal from './DeleteModal';
import { authAPI, chatAPI } from '../axios';
import { useNavigate } from 'react-router-dom'; // Certifique-se de importar useNavigate

function ChatInterface() {
  const navigate = useNavigate(); // Inicialize useNavigate
  const [chats, setChats] = useState([
    { id: 1, title: 'Resumo sobre currículo', messages: [] },
    { id: 2, title: 'Dúvidas sobre um documento', messages: [] },
    { id: 3, title: 'Dúvidas sobre um documento', messages: [] },
    { id: 5, title: 'Chat com IA', messages: [{ id: 1, text: 'Olá! Como posso ajudar você hoje?' }] }
  ]);
  const [selectedChat, setSelectedChat] = useState(null);
  const [dropdownOpen, setDropdownOpen] = useState(null); 
  const [newMessage, setNewMessage] = useState('');
  const [showModal, setShowModal] = useState(false); // Estado para controlar a visibilidade do modal
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [chatToDelete, setChatToDelete] = useState(null);

  const dropdownRef = useRef(null);

  const handleNewChat = () => {
    setShowModal(true); // Abre o modal
  };

  const handleCloseModal = () => {
    setShowModal(false); // Fecha o modal
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

  const handleClickOutside = (event) => {
    if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
      setDropdownOpen(null);
    }
  };

  const handleUpdateChat = (chat) => {
    alert(`Atualizar chat: ${chat.title}`);
  };

  const handleDeleteChatConfirm = (chat) => {
    setChatToDelete(chat);
    setShowDeleteModal(true);
  };

  const handleDeleteChat = () => {
    setChats(chats.filter((chat) => chat.id !== chatToDelete.id));
    setShowDeleteModal(false);
    setChatToDelete(null);
  };

  const handleDeleteChatCancel = () => {
    setShowDeleteModal(false);
    setChatToDelete(null);
  };

  const handleSendMessage = () => {
    if (selectedChat && newMessage.trim()) {
      const userMessage = { id: Date.now(), text: newMessage };
      const updatedChats = chats.map((chat) => {
        if (chat.id === selectedChat.id) {
          return {
            ...chat,
            messages: [...chat.messages, userMessage],
          };
        }
        return chat;
      });

      setChats(updatedChats);
      setNewMessage('');

      // Simular resposta da IA após uma pequena pausa
      setTimeout(() => {
        const aiResponse = generateAIResponse(newMessage);
        const updatedChatsWithResponse = updatedChats.map((chat) => {
          if (chat.id === selectedChat.id) {
            return {
              ...chat,
              messages: [...chat.messages, userMessage, aiResponse],
            };
          }
          return chat;
        });

        setChats(updatedChatsWithResponse);
        setSelectedChat(updatedChatsWithResponse.find(chat => chat.id === selectedChat.id));
      }, 1000);
    }
  };

  const generateAIResponse = (message) => {
    let responseText = "Desculpe, não entendi sua pergunta.";
    
    if (message.toLowerCase().includes('olá') || message.toLowerCase().includes('oi')) {
      responseText = 'Olá! Como posso ajudar você?';
    } else if (message.toLowerCase().includes('qual seu nome')) {
      responseText = 'Eu sou um assistente virtual. Como posso ajudar você?';
    } else if (message.toLowerCase().includes('ajuda') || message.toLowerCase().includes('informação')) {
      responseText = 'Claro! Estou aqui para responder suas perguntas.';
    }

    return { id: Date.now(), text: responseText };
  };

  useEffect(() => {
    if (dropdownOpen !== null) {
      document.addEventListener('click', handleClickOutside);
    } else {
      document.removeEventListener('click', handleClickOutside);
    }
    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  }, [dropdownOpen]);

  // Função de logout
  const handleLogout = () => {
    // Obter o token refresh do localStorage, se necessário
    const refreshToken = localStorage.getItem('refresh');

    // Dados para logout (se necessário pelo backend)
    const logoutData = {
      refresh: refreshToken,
    };

    // Chamar a API de logout
    authAPI
      .logout(logoutData)
      .then((response) => {
        // Remover tokens do localStorage
        localStorage.removeItem('access');
        localStorage.removeItem('refresh');
        localStorage.removeItem('sessionid');

        // Redirecionar para a página de login
        navigate('/login');
      })
      .catch((error) => {
        // Mesmo se o logout falhar, remover os tokens e redirecionar
        localStorage.removeItem('access');
        localStorage.removeItem('refresh');
        localStorage.removeItem('sessionid');

        // Redirecionar para a página de login
        navigate('/login');

        // Opcional: exibir mensagem de erro
        console.error('Erro ao fazer logout:', error);
      });
    };

  return (
    <div className="flex flex-col min-h-screen">
      {/* Navbar */}
      <div className="flex items-center justify-between bg-black text-white px-5 py-3 h-1/6">
        <img src={Logo} alt="Logo" className="custom-navbar-logo-size" />
        <div className="flex items-center">
          <button
            onClick={handleLogout}
            className="text-white hover:text-gray-400 ml-4"
            title="Logout"
          >
            <svg className='h-5 w-5' xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 512 512">
              <path d="M377.9 105.9L500.7 228.7c7.2 7.2 11.3 17.1 11.3 27.3s-4.1 20.1-11.3 27.3L377.9 406.1c-6.4 6.4-15 9.9-24 9.9c-18.7 0-33.9-15.2-33.9-33.9l0-62.1-128 0c-17.7 0-32-14.3-32-32l0-64c0-17.7 14.3-32 32-32l128 0 0-62.1c0-18.7 15.2-33.9 33.9-33.9c9 0 17.6 3.6 24 9.9zM160 96L96 96c-17.7 0-32 14.3-32 32l0 256c0 17.7 14.3 32 32 32l64 0c17.7 0 32 14.3 32 32s-14.3 32-32 32l-64 0c-53 0-96-43-96-96L0 128C0 75 43 32 96 32l64 0c17.7 0 32 14.3 32 32s-14.3 32-32 32z"/>
            </svg>
          </button>
        </div>
      </div>

      <div className="flex flex-1">
        {/* Sidebar */}
        <div className="w-72 flex flex-col gap-5 bg-gray-100 p-5 border-r border-gray-300">
          <div className="flex items-center">
            <span className="font-semibold text-lg">Olá, {`{Nome do Usuário}`} :)</span>
          </div>

          <button
            onClick={handleNewChat} // Abre o modal ao clicar
            className="w-full py-2 bg-black text-white rounded-lg font-semibold hover:bg-gray-800"
          >
            + Novo Chat
          </button>

          {/*Listagem do Chat*/}
          <div onClick={() => setDropdownOpen(null)}>
            <p className="text-gray-600 font-medium mb-3">Suas conversas</p>
            <ul>
              {chats.map((chat) => (
                <li
                  key={chat.id}
                  onClick={(e) => e.stopPropagation()} 
                >
                  <div className={`relative w-full flex flex-col justify-center cursor-pointer rounded-lg group ${
                    selectedChat && selectedChat.id === chat.id ? 'bg-gray-300' : 'hover:bg-gray-200'
                  }`}>
                    <div onClick={() => handleSelectChat(chat)} className="self-start w-full flex items-center p-2">
                      <svg className="h-5 w-5 mr-3 flex-shrink-0" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
                        <path d="M123.6 391.3c12.9-9.4 29.6-11.8 44.6-6.4c26.5 9.6 56.2 15.1 87.8 15.1c124.7 0 208-80.5 208-160s-83.3-160-208-160S48 160.5 48 240c0 32 12.4 62.8 35.7 89.2c8.6 9.7 12.8 22.5 11.8 35.5c-1.4 18.1-5.7 34.7-11.3 49.4c17-7.9 31.1-16.7 39.4-22.7zM21.2 431.9c1.8-2.7 3.5-5.4 5.1-8.1c10-16.6 19.5-38.4 21.4-62.9C17.7 326.8 0 285.1 0 240C0 125.1 114.6 32 256 32s256 93.1 256 208s-114.6 208-256 208c-37.1 0-72.3-6.4-104.1-17.9c-11.9 8.7-31.3 20.6-54.3 30.6c-15.1 6.6-32.3 12.6-50.1 16.1c-.8 .2-1.6 .3-2.4 .5c-4.4 .8-8.7 1.5-13.2 1.9c-.2 0-.5 .1-.7 .1c-5.1 .5-10.2 .8-15.3 .8c-6.5 0-12.3-3.9-14.8-9.9c-2.5-6-1.1-12.8 3.4-17.4c4.1-4.2 7.8-8.7 11.3-13.5c1.7-2.3 3.3-4.6 4.8-6.9l.3-.5z" />
                      </svg>
                      <span className="truncate">{chat.title}</span>
                    </div>
                    
                    {/* Botão de opções centralizado verticalmente no final do chat */}
                    <div className="absolute inline-flex items-center self-end"> {/* Alinha à direita e centraliza verticalmente */}
                      <button
                        onClick={() => toggleDropdown(chat.id)}
                        className={`p-1 text-gray-600  ${ selectedChat && selectedChat.id === chat.id ? 'text-black block bg-gray-300' : 'hover:text-black hidden group-hover:inline-flex group-hover:bg-gray-200'}`}
                        aria-haspopup="true"
                        aria-expanded={dropdownOpen === chat.id}
                      >
                        <svg className="w-5 h-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
                          <path d="M8 256a56 56 0 1 1 112 0A56 56 0 1 1 8 256zm160 0a56 56 0 1 1 112 0 56 56 0 1 1 -112 0zm216-56a56 56 0 1 1 0 112 56 56 0 1 1 0-112z" />
                        </svg>
                      </button>
                      
                      {dropdownOpen === chat.id && (
                        <div ref={dropdownRef} className="absolute z-10 bg-white border rounded-lg shadow-md left-6 top-1 mt-2 ">
                          <button
                            onClick={() => handleUpdateChat(chat)}
                            className="block w-full text-left px-4 py-2 text-sm hover:bg-gray-100"
                          >
                            Atualizar
                          </button>
                          <button
                            onClick={() => handleDeleteChatConfirm(chat)}
                            className="block w-full text-left px-4 py-2 text-sm hover:bg-gray-100"
                          >
                            Apagar
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex flex-col w-full bg-white p-8">
          <div className="flex items-center justify-between border-b pb-4 mb-4">
            <h2 className="text-2xl font-extrabold">
              {selectedChat?.title || 'Sem conversa selecionada'}
            </h2>
          </div>

          {/* Área de mensagens */}
          <div className="flex-1 overflow-y-auto">
            {selectedChat && selectedChat.messages.length > 0 ? (
              selectedChat.messages.map((message) => (
                <div key={message.id} className="p-2 bg-gray-100 my-2 rounded-lg">
                  {message.text}
                </div>
              ))
            ) : (
              <div className="text-gray-500 text-center mt-8">Nenhuma mensagem ainda.</div>
              /* - implementar quando não tiver nenhum chat selecionado
              <div className="text-center">
                <h3 className="font-extrabold text-4xl mb-4 text-black">Sem conversa selecionada</h3>
                <p className="font-semibold text-base text-gray-500 mt-2">
                  Selecione uma conversa já criada, clique em Novo Chat, ou{' '}
                  <span className="cursor-pointer underline">clique aqui</span> para criar um novo chat.
                </p>
              </div>*/
            )}
          </div>

          {/* Input de mensagem */}
          {selectedChat && (
            <div className="mt-4 border-t pt-4 relative flex items-center">
              <input
                type="text"
                placeholder="Digite sua mensagem..."
                value={newMessage || ''} // Define newMessage como uma string vazia caso esteja undefined
                onChange={(e) => setNewMessage(e.target.value)}
                className="h-12 flex-1 px-4 py-2 pr-12 border rounded-xl focus:outline-none focus:border-gray-400"
              />
              <button onClick={handleSendMessage} className="absolute right-3 text-black hover:text-black">
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
          )}
        </div>

      </div>

    {/* Modal de Upload */}
      <UploadModal
        showModal={showModal}
        onClose={handleCloseModal}
        onCreateChat={handleCreateChat}
      />
      
      {showDeleteModal && (
        <DeleteChatModal
          chatName={chatToDelete?.title}
          onClose={handleDeleteChatCancel}
          onDelete={handleDeleteChat}
        />
      )}

    </div>
  );
}

export default ChatInterface;
