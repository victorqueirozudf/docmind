import React, { useState, useRef, useEffect } from 'react';
import '../../index.css';
import UploadModal from '../features/UploadModal';
import DeleteChatModal from '../features/DeleteModal'; 
import UpdateChatModal from '../features/UpdateChatModal'; 
import ChatDetailModal from '../features/ChatDetailModal'; 
import { authAPI, chatAPI } from '../../axios'; 
import { useNavigate } from 'react-router-dom'; 
import ReactMarkdown from "react-markdown";
import Navbar from '../layout/Navbar'

function ChatInterface() {
  const navigate = useNavigate(); // Hook para redirecionamento
  const dropdownRef = useRef(null); // Referência para detectar cliques fora do dropdown

  // Estados para gerenciar dados e UI
  const [user, setUser] = useState(null); // Dados do usuário logado
  const [chats, setChats] = useState([]); // Lista de chats
  const [selectedChat, setSelectedChat] = useState(null); // Chat selecionado
  const [dropdownOpen, setDropdownOpen] = useState(null); // ID do chat com dropdown aberto
  const [newMessage, setNewMessage] = useState(''); // Mensagem nova a ser enviada
  const [showModal, setShowModal] = useState(false); // Controle de visibilidade do modal de criação de chat
  const [showDeleteModal, setShowDeleteModal] = useState(false); // Controle de visibilidade do modal de exclusão de chat
  const [chatToDelete, setChatToDelete] = useState(null); // Chat selecionado para exclusão
  const messagesEndRef = useRef(null); // Referência para o final do container de mensagens
  const [isScrollable, setIsScrollable] = useState(false);
  const scrollRef = useRef(null);
  const [isAtBottom, setIsAtBottom] = useState(true); // Verifica se o scroll está no final
  const [showUpdateModal, setShowUpdateModal] = useState(false);
  const [chatToUpdate, setChatToUpdate] = useState(null);
  const [showChatDetailModal, setShowChatDetailModal] = useState(false);

  const handleOpenChatDetails = () => {
    setShowChatDetailModal(true);
  };

  const handleCloseChatDetails = () => {
    setShowChatDetailModal(false);
  };

  // Função para converter base64 para UTF-8
  const base64ToUtf8 = (base64) => {
    const binaryStr = atob(base64);
    const bytes = Uint8Array.from(binaryStr, char => char.charCodeAt(0));
    const decoder = new TextDecoder('utf-8');
    return decoder.decode(bytes);
  };
    
  /** 
   * Função para abrir o modal de criação de novo chat
   */
  const handleNewChat = () => {
    setShowModal(true);
  };

  /** 
   * Função para fechar o modal de criação de novo chat
   */
  const handleCloseModal = () => {
    setShowModal(false);
  };

  /** 
   * Função para criar um novo chat
   * @param {string} chatName - Nome do novo chat
   * @param {File} file - Arquivo opcional para upload
   */
  const handleCreateChat = async (chatName, files) => {
    try {
      const formData = new FormData();
      formData.append('chat_name', chatName);
    
      if (files && files.length > 0) {
        files.forEach((file) => {
          formData.append('pdfs', file); // Usar 'pdfs' para múltiplos arquivos
        });
      }
  
      const response = await chatAPI.createChat(formData); // Envia dados para o backend
      const newChat = response.data; // Recebe o chat criado do backend
      setChats([...chats, newChat]); // Atualiza a lista de chats
      setSelectedChat(newChat); // Seleciona o chat recém-criado
      setShowModal(false); // Fecha o modal
    } catch (error) {
      console.error('Erro ao criar chat:', error);
    }
  };

  /**
   * Função para selecionar um chat e buscar suas mensagens
   * @param {object} chat - Objeto do chat selecionado
  */
  const handleSelectChat = async (chat) => {
    setSelectedChat(chat); // Define o chat selecionado inicialmente

    try {
      const response = await chatAPI.getChatDetails(chat.thread_id); // Utiliza a função definida no chatAPI
      const messages = response.data.messages; // Obtém as mensagens do campo "messages"

      // Verifica e processa as mensagens recebidas
      if (!messages || !Array.isArray(messages)) {
        console.error('Não foram encontradas mensagens:', response.data);
        setSelectedChat((prevChat) => ({
          ...prevChat,
          messages: [], // Limpa as mensagens se não houverem
        }));
        return;
      }

      // Processa as mensagens para decodificar e filtrar o conteúdo
      const chatHistory = messages.map((message) => {
        let metadata;
        try {
          const metadataStr = base64ToUtf8(message.metadata);
          metadata = JSON.parse(metadataStr); // Converte para JSON
        } catch (error) {
          console.error('Erro ao processar metadata:', error);
          return { inputContent: '', outputContent: '' }; // Valores padrão em caso de erro
        }

        // Extrai conteúdos de entrada e saída
        const inputContent = metadata?.writes?.__start__?.messages?.[0]?.kwargs?.content || '';
        const outputContent = metadata?.writes?.model?.messages?.kwargs?.content || '';

        return { inputContent, outputContent }; // Retorna o conteúdo processado
      });

      // Filtra mensagens que tenham conteúdo válido
      const filteredChatHistory = chatHistory.filter(({ inputContent, outputContent }) => {
        return inputContent.trim() !== '' || outputContent.trim() !== '';
      });

      console.log('Histórico do Chat:', filteredChatHistory); // Log para depuração

      // Atualiza o estado com o histórico processado
      setSelectedChat((prevChat) => ({
        ...prevChat,
        messages: filteredChatHistory,
      }));
    } catch (error) {
      console.error('Erro ao buscar mensagens do chat:', error);
    }
  };
  
  /** 
 * Função para enviar uma nova mensagem no chat selecionado
 */
  const handleSendMessage = async () => {
    if (selectedChat && newMessage.trim()) {
      // Cria a mensagem do usuário localmente
      const userMessage = {
        id: Date.now(), // ID temporário
        inputContent: newMessage, // A mensagem enviada pelo usuário
        sender: 'user',
      };

      // Atualiza as mensagens localmente
      setSelectedChat((prevChat) => ({
        ...prevChat,
        messages: [...(prevChat.messages || []), userMessage],
      }));

      setNewMessage(''); // Limpa o campo de entrada

      try {
        // Envia a pergunta para o backend
        const response = await chatAPI.sendQuestionToChat(selectedChat.thread_id, {
          question: newMessage,
        });

        // Adiciona a resposta da API
        const apiMessage = {
          id: Date.now() + 1, // ID temporário para a resposta
          outputContent: response.data.answer, // Resposta da API
          sender: 'api',
        };

        // Atualiza as mensagens com a resposta do backend
        setSelectedChat((prevChat) => ({
          ...prevChat,
          messages: [...prevChat.messages, apiMessage],
        }));
      } catch (error) {
        console.error('Erro ao enviar mensagem:', error);
      }
    }
  };

  /** 
   * Função para alternar a visibilidade do dropdown de opções do chat
   * @param {number} id - ID do chat
   */
  const toggleDropdown = (id) => {
    setDropdownOpen(dropdownOpen === id ? null : id);
  };

  /** 
   * Função para fechar o dropdown ao clicar fora dele
   * @param {Event} event - Evento de clique
   */
  const handleClickOutside = (event) => {
    if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
      setDropdownOpen(null);
    }
  };

  /** 
   * Hook para adicionar/remover listener de clique para fechar dropdown
   */
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

  const handleUpdateChatOpen = (chat) => {
    setChatToUpdate(chat);
    setShowUpdateModal(true);
  };

  const handleUpdateModalClose = () => {
    setShowUpdateModal(false);
    setChatToUpdate(null);
  };

  const handleUpdateChat = async (threadId, formData) => {
    try {
      const response = await chatAPI.updateChat(threadId, formData); // Chama o método da API
      const updatedChat = response.data; // Obtenha o chat atualizado do backend

      // Atualiza a lista de chats no estado
      setChats((prevChats) =>
        prevChats.map((chat) =>
          chat.thread_id === threadId ? { ...chat, ...updatedChat } : chat
        )
      );

      // Atualiza o chat selecionado, se estiver editando o atual
      if (selectedChat && selectedChat.thread_id === threadId) {
        setSelectedChat((prevChat) => ({ ...prevChat, ...updatedChat }));
      }

      handleUpdateModalClose(); // Fecha o modal
    } catch (error) {
      console.error('Erro ao atualizar chat:', error);
    }
  };
    
  /** 
   * Função para confirmar a exclusão de um chat
   * @param {object} chat - Objeto do chat a ser excluído
   */
  const handleDeleteChatConfirm = (chat) => {
    setChatToDelete(chat);
    setShowDeleteModal(true);
  };

  /** 
   * Função para deletar um chat
   */
  const handleDeleteChat = async () => {
    try {
      await chatAPI.deleteChat(chatToDelete.thread_id); // Envia requisição de deleção para o backend
      setChats(chats.filter((chat) => chat.thread_id !== chatToDelete.thread_id)); // Atualiza a lista de chats
      setShowDeleteModal(false); // Fecha o modal de exclusão
      setChatToDelete(null); // Reseta o chat a ser deletado

      // Se o chat deletado estava selecionado, reseta a seleção
      if (selectedChat && selectedChat.thread_id === chatToDelete.thread_id) {
        setSelectedChat(null);
      }
    } catch (error) {
      console.error('Erro ao deletar chat:', error);
    }
  };

  /** 
   * Função para cancelar a exclusão de um chat
   */
  const handleDeleteChatCancel = () => {
    setShowDeleteModal(false);
    setChatToDelete(null);
  };

  /** 
   * Hook para buscar a lista de chats do backend ao montar o componente
   */
  useEffect(() => {
    const fetchChats = async () => {
      try {
        const response = await chatAPI.getChats(); // Busca chats do backend
        setChats(response.data); // Atualiza a lista de chats
      } catch (error) {
        console.error('Erro ao buscar chats:', error);
      }
    };
    fetchChats();
  }, []);

  /** 
   * Hook para buscar os dados do usuário logado ao montar o componente
   */
  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const response = await authAPI.getUserDetails(); // Busca dados do usuário
        setUser(response.data); // Atualiza os dados do usuário
      } catch (error) {
        console.error('Erro ao buscar dados do usuário:', error);
      }
    };
    fetchUserData();
  }, []);

  /** 
   * Função para realizar o logout do usuário
   */
  const handleLogout = () => {
    const refreshToken = localStorage.getItem('refresh'); // Obtém o token de refresh

    if (!refreshToken) {
      console.error('Token de refresh não encontrado.');
      // Remove tokens existentes e redireciona
      localStorage.removeItem('access');
      localStorage.removeItem('refresh');
      localStorage.removeItem('sessionid');
      navigate('/');
      return;
    }

    const logoutData = {
      refresh_token: refreshToken, // Dados para logout
    };

    authAPI
      .logout(logoutData) // Chama a API de logout
      .then((response) => {
        // Remove tokens do localStorage
        localStorage.removeItem('access');
        localStorage.removeItem('refresh');
        localStorage.removeItem('sessionid');

        // Redireciona para a página de login
        navigate('/');
      })
      .catch((error) => {
        // Mesmo se o logout falhar, remove tokens e redireciona
        localStorage.removeItem('access');
        localStorage.removeItem('refresh');
        localStorage.removeItem('sessionid');

        navigate('/');

        console.error('Erro ao fazer logout:', error);
      });
  };

  const handleManualScroll = () => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  };


  useEffect(() => {
    const handleScroll = () => {
      if (scrollRef.current) {
        const { scrollTop, scrollHeight, clientHeight } = scrollRef.current;
        const isAtBottom = scrollTop + clientHeight >= scrollHeight - (scrollHeight * 0.05); // 5% do final
        setIsAtBottom(isAtBottom); // Atualiza estado para controlar o botão
        const isContentScrollable = scrollHeight > clientHeight; // Verifica se o conteúdo é rolável
        setIsScrollable(isContentScrollable && !isAtBottom); // Mostra o botão apenas se não estiver no final
      }
    };
  
    const currentRef = scrollRef.current;
    if (currentRef) {
      currentRef.addEventListener("scroll", handleScroll);
    }
  
    return () => {
      if (currentRef) {
        currentRef.removeEventListener("scroll", handleScroll);
      }
    };
  }, [scrollRef]);
  
  useEffect(() => {
    if (scrollRef.current && isAtBottom) {
      // Role automaticamente para o final, mas somente se o usuário já estiver no final
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [selectedChat?.messages, isAtBottom]);

  return (
    <div className="flex flex-col min-h-screen">
      {/* Navbar */}
      <Navbar onLogout={handleLogout} user={user} />

      <div className="flex flex-1">
        {/* Sidebar */}
        <div className="sticky top-0 w-72 flex flex-col gap-5 bg-gray-100 p-5 border-r border-gray-300 caret-transparent">
          {/* Saudação ao usuário */}
          <div className="flex items-center">
            <span className="font-semibold text-lg">Olá, {user ? user.username : 'Usuário'} :)</span>
          </div>

          {/* Botão para criar novo chat */}
          <button
            onClick={handleNewChat}
            className="w-full py-2 bg-black text-white rounded-lg font-semibold hover:bg-gray-800"
          >
            + Novo Chat
          </button>

          {/* Listagem dos chats */}
          <div onClick={() => setDropdownOpen(null)}>
            <p className="text-gray-600 font-medium mb-3">Suas conversas</p>
            <ul>
              {chats.map((chat) => (
                <li
                  key={chat.thread_id}
                  onClick={(e) => e.stopPropagation()} 
                >
                  <div className={`relative w-full flex flex-col justify-center cursor-pointer rounded-lg group ${
                    selectedChat && selectedChat.thread_id === chat.thread_id ? 'bg-gray-300' : 'hover:bg-gray-200'
                  }`}>
                    {/* Área clicável para selecionar o chat */}
                    <div onClick={() => handleSelectChat(chat)} className="self-start w-full flex items-center p-2">
                      <svg className="h-5 w-5 mr-3 flex-shrink-0" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
                        <path d="M123.6 391.3c12.9-9.4 29.6-11.8 44.6-6.4c26.5 9.6 56.2 15.1 87.8 15.1c124.7 0 208-80.5 208-160s-83.3-160-208-160S48 160.5 48 240c0 32 12.4 62.8 35.7 89.2c8.6 9.7 12.8 22.5 11.8 35.5c-1.4 18.1-5.7 34.7-11.3 49.4c17-7.9 31.1-16.7 39.4-22.7zM21.2 431.9c1.8-2.7 3.5-5.4 5.1-8.1c10-16.6 19.5-38.4 21.4-62.9C17.7 326.8 0 285.1 0 240C0 125.1 114.6 32 256 32s256 93.1 256 208s-114.6 208-256 208c-37.1 0-72.3-6.4-104.1-17.9c-11.9 8.7-31.3 20.6-54.3 30.6c-15.1 6.6-32.3 12.6-50.1 16.1c-.8 .2-1.6 .3-2.4 .5c-4.4 .8-8.7 1.5-13.2 1.9c-.2 0-.5 .1-.7 .1c-5.1 .5-10.2 .8-15.3 .8c-6.5 0-12.3-3.9-14.8-9.9c-2.5-6-1.1-12.8 3.4-17.4c4.1-4.2 7.8-8.7 11.3-13.5c1.7-2.3 3.3-4.6 4.8-6.9l.3-.5z" />
                      </svg>
                      <span className="truncate">{chat.chat_name}</span>
                    </div>
                    
                    {/* Botão de opções do chat */}
                    <div className="absolute inline-flex items-center self-end">
                      <button
                        onClick={() => toggleDropdown(chat.thread_id)}
                        className={`p-1 text-gray-600  ${ selectedChat && selectedChat.thread_id === chat.thread_id ? 'text-black block bg-gray-300' : 'hidden'}`}
                        aria-haspopup="true"
                        aria-expanded={dropdownOpen === chat.thread_id}
                      >
                        <svg className="w-5 h-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
                          <path d="M8 256a56 56 0 1 1 112 0A56 56 0 1 1 8 256zm160 0a56 56 0 1 1 112 0 56 56 0 1 1 -112 0zm216-56a56 56 0 1 1 0 112 56 56 0 1 1 0-112z" />
                        </svg>
                      </button>
                      
                      {/* Dropdown com opções de atualizar e apagar chat */}
                      {dropdownOpen === chat.thread_id && (
                        <div ref={dropdownRef} className="absolute z-10 bg-white border rounded-lg shadow-md left-6 top-1 mt-2">
                          <button
                            onClick={() => handleUpdateChatOpen(chat)}
                            className="block w-full text-left px-4 py-2 text-sm hover:bg-gray-100 hover:underline"
                          >
                            Atualizar
                          </button>
                          <button
                            onClick={() => handleDeleteChatConfirm(chat)}
                            className="block text-red-500 w-full text-left px-4 py-2 text-sm hover:bg-gray-100 hover:underline"
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

        {/* Área do chat selecionado */}
        <div className="flex flex-col w-full h-full bg-white p-5">
          {/* Título do chat */}
          <div className="sticky top-0 flex items-center justify-between border-b pb-5">
            <h2 className="text-2xl font-extrabold caret-transparent">
              {selectedChat?.chatName || 'Sem conversa selecionada'}
            </h2>
            <div className={`${selectedChat ? 'block' : 'hidden'} caret-transparent`} >
              <button
                onClick={handleOpenChatDetails}
                className="text-black px-3 py-1 rounded hover:text-gray-800"
              >
                <svg className="w-5 h-7" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
                  <path d="M8 256a56 56 0 1 1 112 0A56 56 0 1 1 8 256zm160 0a56 56 0 1 1 112 0 56 56 0 1 1 -112 0zm216-56a56 56 0 1 1 0 112 56 56 0 1 1 0-112z" />
                </svg>
              </button>
            </div>
          </div>

          {/* Área de mensagens */}
          <div ref={scrollRef} className='overflow-y-auto'>
            <div className="flex-1 flex flex-col h-[calc(100vh-220px)] p-5">
              {selectedChat ? (
                selectedChat.messages && selectedChat.messages.length > 0 ? (
                  selectedChat.messages.map((message, index) => (
                    <React.Fragment key={index}>
                      {/* Mensagem do usuário */}
                      {message.inputContent && (
                        <div className="p-2 my-2 rounded-lg max-w-3xl bg-black text-white ml-auto text-right">
                          {message.inputContent}
                        </div>
                      )}
                      {/* Resposta da IA */}
                      {message.outputContent && (
                        <div className="p-2 my-2 rounded-lg max-w-3xl bg-gray-200 mr-auto text-left">
                          <ReactMarkdown>{message.outputContent}</ReactMarkdown>
                        </div>
                      )}
                    </React.Fragment>
                  ))
                ) : (
                  <div className="text-gray-500 text-center mt-8">Nenhuma mensagem ainda.</div>
                )
              ) : (
                <div className="text-center caret-transparent">
                  <h3 className="text-2xl font-bold text-black">Sem conversa selecionada</h3>
                  <p className="text-gray-500 mt-2">
                    Selecione uma conversa já criada, clique em Novo Chat, ou{' '}
                    <span
                      className="text-gray-700 cursor-pointer underline"
                      onClick={handleNewChat} // Certifique-se de ter esta função definida
                    >
                      clique aqui
                    </span>{' '}
                    para criar um novo chat.
                  </p>
                </div>
              )}

              {isScrollable && (
                <button
                  onClick={handleManualScroll}
                  className={`absolute ${isAtBottom ? "" : "visible"} bg-black text-white px-4 py-2 rounded-full shadow-lg hover:bg-gray-900 custom-bottom-scroll-to-end`}
                  title="Ir para o final"
                >
                  ↓
                </button>
              )}
            </div>
            <div ref={messagesEndRef} />
          </div>      
          

          {/* Input fixo para enviar nova mensagem */}
          {selectedChat && (
            <div className="sticky bottom-0 bg-white pt-5">
              <div className="relative flex items-center">
                <input
                  type="text"
                  placeholder="Digite sua mensagem..."
                  value={newMessage || ''}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && newMessage.trim()) {
                      handleSendMessage();
                    }
                  }}
                  className="h-12 flex-1 px-4 py-2 border rounded-xl focus:outline-none focus:border-gray-400"
                />
                <button onClick={handleSendMessage} className="absolute right-3 text-black hover:text-black" >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 512 512"
                    className="w-7 h-7"
                    fill="currentColor"
                  >
                    <path d="M0 256a256 256 0 1 0 512 0A256 256 0 1 0 0 256zM241 377c-9.4 9.4-24.6 9.4-33.9 0s-9.4-24.6 0-33.9l87-87-87-87c-9.4-9.4-9.4-24.6 0-33.9s24.6-9.4 33.9 0L345 239c9.4 9.4 9.4 24.6 0 33.9L241 377z" />
                  </svg>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Modal de Detalhes do Chat */}
      {selectedChat && (
        <ChatDetailModal
          showModal={showChatDetailModal}
          onClose={handleCloseChatDetails}
          chatDetails={selectedChat} // Passa os detalhes do chat selecionado
        />
      )}

      {/* Modal para criar novo chat */}
      <UploadModal
        showModal={showModal}
        onClose={handleCloseModal}
        onCreateChat={handleCreateChat}
      />

      {showUpdateModal && (
        <UpdateChatModal
          showModal={showUpdateModal}
          onClose={handleUpdateModalClose}
          onUpdateChat={handleUpdateChat}
          initialChatName={chatToUpdate?.chatName || ''}
          threadId={chatToUpdate?.thread_id}
        />
      )}
      
      {/* Modal para confirmar exclusão de chat */}
      {showDeleteModal && (
        <DeleteChatModal
          chatName={chatToDelete?.chatName}
          onClose={handleDeleteChatCancel}
          onDelete={handleDeleteChat}
        />
      )}
    </div>
  );
}

export default ChatInterface;
