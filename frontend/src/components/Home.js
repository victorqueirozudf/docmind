import { useEffect, useState } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";

export const Home = () => {
    const [userData, setUserData] = useState(null);
    const [pdfFile, setPdfFile] = useState(null);
    const [chatName, setChatName] = useState('');
    const [chats, setChats] = useState([]);
    const [selectedChat, setSelectedChat] = useState(null);
    const [userQuestion, setUserQuestion] = useState('');
    const [chatHistory, setChatHistory] = useState([]);
    const [loading, setLoading] = useState(true);

    // Função para listar os chats criados
    const fetchChats = async () => {
        const accessToken = localStorage.getItem('access_token'); // Pega o token do Local Storage

        if (!accessToken) {
            alert("Você não está logado. Faça login!");
            window.location.href = '/login';
            return;
        }

        try {
            const response = await axios.get('http://localhost:8000/api/chats/', {
                headers: {
                    'Authorization': `Bearer ${accessToken}`, // Inclui o token JWT no cabeçalho
                },
            });
            setChats(response.data);
        } catch (error) {
            console.error('Erro ao buscar chats:', error);
        }
    };

    useEffect(() => {
        const accessToken = localStorage.getItem('access_token');

        if (!accessToken) {
            alert("Você não está logado. Faça login!");
            window.location.href = '/login';
            return;
        }

        const fetchData = async () => {
            try {
                const { data } = await axios.get('http://localhost:8000/home/', {
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${accessToken}`,
                    },
                });
                setUserData(data); // Armazena os dados do usuário
            } catch (error) {
                console.log('Erro ao buscar dados: not auth', error);
                if (error.response && error.response.status === 401) {
                    alert("Sessão expirada. Faça login novamente.");
                    window.location.href = '/login';
                }
            } finally {
                setLoading(false);
            }
        };
        fetchData();
        fetchChats();
    }, []);

    if (loading) {
        return <h3>Carregando...</h3>;
    }

    // Função para criar um novo chat
    const createChat = async () => {
        if (pdfFile && chatName) {
            const formData = new FormData();
            formData.append('pdfs', pdfFile);
            formData.append('chatName', chatName);

            const accessToken = localStorage.getItem('access_token'); // Pega o token do Local Storage

            if (!accessToken) {
                alert("Você não está logado. Faça login!");
                window.location.href = '/login';
                return;
            }

            try {
                const response = await axios.post('http://localhost:8000/api/chats/', formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                        'Authorization': `Bearer ${accessToken}`, // Inclui o token JWT no cabeçalho
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

    const deleteChat = async (threadId) => {
        const confirmDelete = window.confirm("Tem certeza que deseja excluir este chat? Esta ação não pode ser desfeita.");

        if (confirmDelete) {
            try {
                const accessToken = localStorage.getItem('access_token');
                await axios.delete(`http://localhost:8000/api/chats/delete/${threadId}/`, {
                    headers: {
                        'Authorization': `Bearer ${accessToken}`,
                    },
                });
                // Atualiza a lista de chats, filtrando o chat excluído
                setChats(chats.filter(chat => chat.thread_id !== threadId));
                // Limpa o chat selecionado e o histórico
                if (selectedChat && selectedChat.thread_id === threadId) {
                    setSelectedChat(null);
                    setChatHistory([]); // Limpa o histórico do chat
                }
                alert("Chat excluído com sucesso!");
            } catch (error) {
                console.error('Erro ao excluir chat:', error);
                alert("Ocorreu um erro ao excluir o chat.");
            }
        }
    };

    return (
        <div>
            {userData ? ( // Verifica se os dados do usuário foram carregados
                <div>
                    <h3>Olá, {userData.username}!</h3>
                    <p>ID: {userData.id}</p>
                    <p>Email: {userData.email}</p>
                </div>
            ) : (
                <h3>Carregando...</h3> // Mensagem de carregamento
            )}

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
                {chats && chats.length > 0 ? (
                    chats.map((chat) => (
                        <li key={chat.thread_id} onClick={() => handleChatSelect(chat)}>
                            {chat.chatName} - {chat.created_at} - {chat.thread_id}
                            <button onClick={() => deleteChat(chat.thread_id)}>Excluir</button>
                            {/* Botão de exclusão */}
                        </li>
                    ))
                ) : (
                    <p>Nenhum chat encontrado.</p>
                )}
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
                        {chatHistory && chatHistory.length > 0 ? (
                            chatHistory.map((entry, index) => (
                                <li key={index}>
                                    {entry.inputContent && (
                                        <div>
                                            <strong>Pergunta:</strong> <br/><br/> {entry.inputContent} <br/> <br/>
                                        </div>
                                    )}
                                    {entry.outputContent && (
                                        <div>
                                            <strong>Resposta:</strong>
                                            <ReactMarkdown>{entry.outputContent}</ReactMarkdown>
                                        </div>
                                    )}
                                </li>
                            ))
                        ) : (
                            <p>Nenhuma conversa ainda.</p>
                        )}
                    </ul>
                </div>
            )}
        </div>
    );
};