import React, { useState, useEffect } from 'react';
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
            const response = await axios.get('http://localhost:8000/talkpdf/message/');
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
                const response = await axios.post('http://localhost:8000/talkpdf/message/', formData, {
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
        await axios.delete('http://localhost:8000/talkpdf/message/', {
            headers: { 'Content-Type': 'application/json' },
            data: { thread_id: chatId }
        });
        console.log(chatId)
        setChats(chats.filter((chat) => chat.id !== chatId));
        setSelectedChat(null);
    } catch (error) {
        console.log(chatId)
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
                        <li key={chat.thread_id} style={{cursor: 'pointer'}}>
                            <span onClick={() => selectChat(chat)}>{`Chat - ${chat.thread_id}`}</span>
                            <button onClick={() => deleteChat(chat.thread_id)}>Apagar</button>
                        </li>
                    ))}
                </ul>
            </div>
            <div style={{flex: 1, padding: '10px'}}>
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

export default App;

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
