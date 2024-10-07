import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ChatPage = () => {
    const [chats, setChats] = useState([]); // Estado para armazenar chats
    const [selectedChat, setSelectedChat] = useState(null); // Estado para armazenar chat selecionado
    const [newChatName, setNewChatName] = useState(''); // Estado para armazenar o nome do novo chat
    const [pdfFile, setPdfFile] = useState(null); // Estado para armazenar o arquivo PDF
    const [question, setQuestion] = useState(''); // Estado para armazenar a pergunta

    // Função para listar todos os chats ao carregar a página
    useEffect(() => {
        fetchChats();
    }, []);

    const fetchChats = async () => {
        try {
            const response = await axios.get('/api/chats'); // Endpoint para listar chats
            setChats(response.data.chats);
        } catch (error) {
            console.error('Erro ao buscar chats:', error);
        }
    };

    // Função para criar um novo chat com um PDF e uma pergunta
    const createChat = async () => {
        if (pdfFile && question) {
            const formData = new FormData();
            formData.append('pdfs', pdfFile);
            formData.append('question', question);

            try {
                const response = await axios.post('/api/chats', formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                    },
                });
                setChats([...chats, { id: response.data.answer.thread_id, name: newChatName }]);
                setNewChatName('');
                setPdfFile(null);
                setQuestion('');
            } catch (error) {
                console.error('Erro ao criar chat:', error);
            }
        } else {
            alert('Por favor, envie um PDF e faça uma pergunta.');
        }
    };

    // Função para selecionar um chat
    const selectChat = (chat) => {
        setSelectedChat(chat);
    };

    // Função para deletar um chat
    const deleteChat = async (chatId) => {
        try {
            await axios.delete('/api/chats', { data: { thread_id: chatId } });
            setChats(chats.filter((chat) => chat.id !== chatId));
            setSelectedChat(null);
        } catch (error) {
            console.error('Erro ao deletar chat:', error);
        }
    };

    return (
        <div style={{ display: 'flex', height: '100vh' }}>
            <div style={{ width: '30%', borderRight: '1px solid #ccc', padding: '10px' }}>
                <h2>Chats</h2>
                <input
                    type="text"
                    value={newChatName}
                    onChange={(e) => setNewChatName(e.target.value)}
                    placeholder="Nome do novo chat"
                />
                <input
                    type="file"
                    onChange={(e) => setPdfFile(e.target.files[0])}
                    accept="application/pdf"
                />
                <input
                    type="text"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="Faça uma pergunta sobre o PDF"
                />
                <button onClick={createChat}>Criar Chat</button>

                <ul>
                    {chats.map((chat) => (
                        <li key={chat.id} style={{ cursor: 'pointer' }}>
                            <span onClick={() => selectChat(chat)}>{chat.name}</span>
                            <button onClick={() => deleteChat(chat.id)}>Apagar</button>
                        </li>
                    ))}
                </ul>
            </div>
            <div style={{ flex: 1, padding: '10px' }}>
                {selectedChat ? (
                    <div>
                        <h2>{selectedChat.name}</h2>
                        <ul>
                            {selectedChat.messages?.map((msg, index) => (
                                <li key={index}>{msg}</li>
                            ))}
                        </ul>
                    </div>
                ) : (
                    <div>
                        <h2>Selecione um chat</h2>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ChatPage;