import React, { useState, useEffect } from 'react';
import axios from 'axios';

const App = () => {
    const [chats, setChats] = useState([]); // Estado para armazenar chats
    const [selectedChat, setSelectedChat] = useState(null); // Estado para armazenar chat selecionado
    const [newChatName, setNewChatName] = useState(''); // Estado para armazenar o nome do novo chat
    const [pdfFile, setPdfFile] = useState(null); // Estado para armazenar o arquivo PDF
    const [question, setQuestion] = useState(''); // Estado para armazenar a pergunta
    const [chatInput, setChatInput] = useState(''); // Estado para armazenar a mensagem do chat

    // Função para listar todos os chats ao carregar a página
    useEffect(() => {
        fetchChats();
    }, []);

    const fetchChats = async () => {
        try {
            const response = await axios.get('http://localhost:8000/api/message/');
            console.log('Chats recebidos:', response.data.chats); // Verifique a estrutura da resposta
            setChats(response.data.chats); // Atualiza o estado com os chats recebidos
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
                const response = await axios.post('http://localhost:8000/api/message/', formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                    },
                });
                setChats([...chats, { thread_id: response.data.answer.thread_id }]);
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

    // Função para selecionar um chat e buscar as mensagens do backend
    const selectChat = async (chatId) => {
        try {
            const response = await axios.get(`http://localhost:8000/api/message/?thread_id=${chatId}`, {
                headers: { 'Content-Type': 'application/json' }
            });
            console.log('Chat selecionado:', response.data); // Verifique a estrutura do chat selecionado
            setSelectedChat(response.data.chat); // Assume que o primeiro elemento do array é o chat com mensagens
            setChatInput(''); // Limpa o input do chat ao selecionar um chat
        } catch (error) {
            console.error('Erro ao buscar chat:', error);
        }
    };

    // Função para deletar um chat
    const deleteChat = async (chatId) => {
        try {
            await axios.delete('http://localhost:8000/api/message/', {
                headers: { 'Content-Type': 'application/json' },
                data: { thread_id: chatId }
            });
            setChats(chats.filter((chat) => chat.thread_id !== chatId));
            setSelectedChat(null);
        } catch (error) {
            console.error('Erro ao deletar chat:', error);
        }
    };

    // Função para enviar mensagem no chat
    const sendMessage = async (pdfFiles) => {
    if (chatInput.trim()) {
        const formData = new FormData();
        formData.append('question', chatInput);
        formData.append('thread_id', selectedChat.thread_id); // ID do chat
        pdfFiles.forEach((pdf, index) => formData.append(`pdfs`, pdf)); // Adiciona os PDFs

        try {
            const response = await axios.post('http://localhost:8000/api/message/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            if (response.data.status === 'success') {
                const { last_message } = response.data.answer;
                setSelectedChat((prevChat) => ({
                    ...prevChat,
                    messages: [...prevChat.messages, last_message],
                }));

                setChatInput(''); // Limpa o input
            }
        } catch (error) {
            console.error('Erro ao enviar a mensagem:', error);
            alert('Ocorreu um erro ao enviar a mensagem. Tente novamente.');
            }
        } else {
            alert('Por favor, digite uma mensagem.');
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
                        <li key={chat.thread_id} style={{ cursor: 'pointer' }}>
                            <span onClick={() => selectChat(chat.thread_id)}>{`Chat - ${chat.thread_id}`}</span>
                            <button onClick={() => deleteChat(chat.thread_id)}>Apagar</button>
                        </li>
                    ))}
                </ul>
            </div>
            <div style={{ flex: 1, padding: '10px' }}>
                {selectedChat ? (
                    <div>
                        <h2>{`Chat - ${selectedChat[0].thread_id}`}</h2>
                        <ul>
                            {selectedChat.map((msg, index) => (
                                <li key={index}>{msg.content ? msg.content : "Sem conteúdo para mostrar."}</li>
                            ))}
                        </ul>
                        <input
                            type="text"
                            value={chatInput}
                            onChange={(e) => setChatInput(e.target.value)}
                            placeholder="Digite sua mensagem..."
                        />
                        <button onClick={sendMessage}>Enviar</button>
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

export default App;

/*import React, { useState, useEffect } from 'react';
import axios from 'axios';

const App = () => {
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
            const response = await axios.get('http://localhost:8000/api/message/');
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
                const response = await axios.post('http://localhost:8000/api/message/', formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                    },
                });
                setChats([...chats, { thread_id: response.data.answer.thread_id }]);
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

    // Função para selecionar um chat e buscar as mensagens do backend
    const selectChat = async (chatId) => {
        try {
            const response = await axios.get(`http://localhost:8000/api/message/?thread_id=${chatId}`, {
                headers: { 'Content-Type': 'application/json' }
            });
            console.log(response.data);
            setSelectedChat(response.data.chat); // Aqui, assumindo que você está retornando um array de mensagens
        } catch (error) {
            console.error('Erro ao buscar chat:', error);
        }
    };

    // Função para deletar um chat
    const deleteChat = async (chatId) => {
        try {
            await axios.delete('http://localhost:8000/api/message/', {
                headers: { 'Content-Type': 'application/json' },
                data: { thread_id: chatId }
            });
            setChats(chats.filter((chat) => chat.thread_id !== chatId));
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
                        <li key={chat.thread_id} style={{ cursor: 'pointer' }}>
                            <span onClick={() => selectChat(chat.thread_id)}>{`Chat - ${chat.thread_id}`}</span>
                            <button onClick={() => deleteChat(chat.thread_id)}>Apagar</button>
                        </li>
                    ))}
                </ul>
            </div>
            <div style={{ flex: 1, padding: '10px' }}>
                {selectedChat ? (
                    <div>
                        <h2>{`Chat - ${selectedChat[0].thread_id}`}</h2>
                        <ul>
                            {selectedChat.map((msg, index) => (
                                <li key={index}>{msg.content ? msg.content : "Sem conteúdo para mostrar."}</li>
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

export default App;
*/



/*
import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';

function App() {
  const [pdfFiles, setPdfFiles] = useState(null);
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  // Função para enviar os PDFs e a pergunta ao backend
  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true);

    const formData = new FormData();
    if (pdfFiles) {
      for (let i = 0; i < pdfFiles.length; i++) {
        formData.append('pdfs', pdfFiles[i]);
      }
    }
    formData.append('question', question);

    fetch('http://localhost:8000/talkpdf/message/', {
      method: 'POST',
      body: formData,
    })
      .then(response => response.json())
      .then(data => {
        setResponse(data.answer.last_message); // Acessando a mensagem correta
        setLoading(false);
      })
      .catch(error => {
        console.error('Erro ao enviar os arquivos:', error);
        setLoading(false);
      });
  };

  return (
    <div>
      <h1>Envio de PDFs e Perguntas</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="file"
          multiple
          onChange={(e) => setPdfFiles(e.target.files)}
          accept="application/pdf"
        />
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Digite sua pergunta"
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Enviando...' : 'Enviar'}
        </button>
      </form>
      {loading && <p>Processando...</p>}
      {response && (
        <div>
          <h2>Resposta:</h2>
          <ReactMarkdown>{response}</ReactMarkdown>
        </div>
      )}
    </div>
  );
}

export default App;*/
