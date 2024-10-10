import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from "react-markdown";

const App = () => {
    const [pdfFile, setPdfFile] = useState(null);
    const [chatName, setChatName] = useState('');
    const [chats, setChats] = useState([]);
    const [selectedChat, setSelectedChat] = useState(null);
    const [userQuestion, setUserQuestion] = useState('');
    const [chatHistory, setChatHistory] = useState([]);

    // Função para listar os chats criados
    const fetchChats = async () => {
        try {
            const response = await axios.get('http://localhost:8000/api/chats/');
            setChats(response.data);
        } catch (error) {
            console.error('Erro ao buscar chats:', error);
        }
    };

    // UseEffect para carregar os chats ao carregar a página
    useEffect(() => {
        fetchChats();
    }, []);

    // Função para criar um novo chat
    const createChat = async () => {
        if (pdfFile && chatName) {
            const formData = new FormData();
            formData.append('pdfs', pdfFile);
            formData.append('chatName', chatName);

            try {
                const response = await axios.post('http://localhost:8000/api/chats/', formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                    },
                });
                // Atualiza a lista de chats
                setChats([...chats, response.data]);
                // Limpa os campos
                setChatName('');
                setPdfFile(null);
            } catch (error) {
                console.error('Erro ao criar chat:', error);
            }
        } else {
            alert('Por favor, envie um PDF e insira um nome para o chat.');
        }
    };

    // Função para selecionar um chat
    const handleChatSelect = (chat) => {
        setSelectedChat(chat);
        fetchChatHistory(chat.thread_id); // Carregar histórico do chat selecionado
    };

    // Função para buscar histórico do chat selecionado
    const fetchChatHistory = async (threadId) => {
        try {
            const response = await axios.get(`http://localhost:8000/api/chats/${threadId}/`);
            // Verifica se há mensagens na resposta
            if (!response.data.messages || !Array.isArray(response.data.messages)) {
                console.error('Não foram encontradas mensagens:', response.data);
                return; // Retorna se não houver mensagens
            }

            // Mapeia as mensagens para extrair os conteúdos desejados
            const chatHistory = response.data.messages.map((message) => {
                // Faz o parse da string de metadata
                let metadata;
                try {
                    metadata = JSON.parse(message.metadata); // Converte a string JSON em um objeto
                } catch (error) {
                    console.error('Erro ao fazer parse da metadata:', error);
                    return { inputContent: '', outputContent: '' }; // Retorna valores vazios se houver erro
                }

                // Extraindo conteúdo de entrada
                const inputContent = metadata?.writes?.__start__?.messages?.[0]?.kwargs?.content || '';

                // Extraindo conteúdo de saída
                const outputContent = metadata?.writes?.model?.messages?.kwargs?.content || '';

                return { inputContent, outputContent }; // Retorna um objeto com os conteúdos
            });

            // Filtra para ignorar mensagens onde ambos os conteúdos são vazios
            const filteredChatHistory = chatHistory.filter(({ inputContent, outputContent }) => {
                return inputContent.trim() !== '' || outputContent.trim() !== '';
            });

            console.log('Histórico do Chat:', filteredChatHistory); // Log para verificar o histórico filtrado
            setChatHistory(filteredChatHistory); // Atualiza o estado com as mensagens filtradas
        } catch (error) {
            console.error('Erro ao buscar histórico do chat:', error);
        }
    };

    // Função para enviar uma pergunta ao chat
    const sendQuestion = async () => {
        if (userQuestion && selectedChat) {
            const formData = new FormData();
            formData.append('question', userQuestion);
            formData.append('thread_id', selectedChat.thread_id); // Envia o ID do chat selecionado
            formData.append('path_file', selectedChat.path); // Adiciona o caminho do PDF

            try {
                const response = await axios.put(`http://localhost:8000/api/chats/${selectedChat.thread_id}/`, formData);

                // Debug para verificar a resposta
                console.log('Resposta da API:', response.data);

                // Após o envio, busca o histórico atualizado
                fetchChatHistory(selectedChat.thread_id);

                setUserQuestion(''); // Limpa o campo de entrada
            } catch (error) {
                console.error('Erro ao enviar pergunta:', error);
            }
        } else {
            alert('Por favor, insira uma pergunta.');
        }
    };

    return (
        <div>
            <h2>Criar Novo Chat</h2>
            <div>
                <label>Nome do Chat:</label>
                <input
                    type="text"
                    value={chatName}
                    onChange={(e) => setChatName(e.target.value)}
                    placeholder="Digite o nome do chat"
                />
            </div>
            <div>
                <label>PDF:</label>
                <input
                    type="file"
                    accept="application/pdf"
                    onChange={(e) => setPdfFile(e.target.files[0])}
                />
            </div>
            <button onClick={createChat}>Criar Chat</button>

            <h2>Chats Criados</h2>
            <ul>
                {chats.map((chat) => (
                    <li key={chat.thread_id} onClick={() => handleChatSelect(chat)}>
                        {chat.chatName} - {chat.created_at}
                    </li>
                ))}
            </ul>

            {selectedChat && (
                <div>
                    <h2>Chat Selecionado: {selectedChat.chatName}</h2>
                    <div>
                        <input
                            type="text"
                            value={userQuestion}
                            onChange={(e) => setUserQuestion(e.target.value)}
                            placeholder="Digite sua pergunta"
                        />
                        <button onClick={sendQuestion}>Enviar Pergunta</button>
                    </div>

                    <h3>Histórico de Perguntas e Respostas:</h3>
                    <ul>
                        {chatHistory.map((entry, index) => (
                            <li key={index}>
                                {entry.inputContent && (
                                    <div>
                                        <strong>Pergunta:</strong> <br/><br/> {entry.inputContent} <br/> <br/>
                                    </div>
                                )}
                                {entry.outputContent && (
                                    <div>
                                        <strong>Resposta:</strong> <ReactMarkdown>{entry.outputContent}</ReactMarkdown>
                                    </div>
                                )}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
};

export default App;