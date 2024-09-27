import React, { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';

function App() {
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState('');
  const [loading, setLoading] = useState(false); // Estado de loading

  // Função para buscar mensagens da API
  const fetchMessages = () => {
    fetch('http://localhost:8000/talkpdf/message/') // URL da sua API Django
      .then(response => response.json())
      .then(data => {
        if (data.status === 'success') {
          // Ordena as mensagens em ordem decrescente pela data
          const sortedMessages = data.MessageTalkPdf.sort((a, b) =>
            new Date(b.created_at) - new Date(a.created_at)
          );
          setMessages(sortedMessages); // Atualiza o estado com os dados ordenados
        }
      })
      .catch(error => console.error('Erro ao buscar dados:', error));
  };

  // Função para enviar mensagem do usuário
  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true); // Ativa o estado de loading
    const newMessage = { message: userInput }; // Prepara a nova mensagem para envio

    fetch('http://localhost:8000/talkpdf/message/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text: userInput }), // Envia o texto do usuário
    })
      .then(response => response.json())
      .then(data => {
        if (data.status === 'success') {
          // Busca as mensagens após enviar a nova
          fetchMessages();
          setUserInput(''); // Limpa o campo de entrada
        }
      })
      .catch(error => console.error('Erro ao enviar dados:', error))
      .finally(() => {
        setLoading(false); // Desativa o estado de loading
      });
  };

  useEffect(() => {
    fetchMessages(); // Busca as mensagens inicialmente
  }, []);

  return (
    <div>
      <h3>{messages.length} Mensagens</h3>
      <h1>Mensagens Aleatórias</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          placeholder="Digite sua mensagem"
        />
        <button type="submit">Enviar</button>
      </form>
      {messages.length > 0 ? (
        messages.map((messageObj, index) => (
          <div key={index}>
            <p><strong>Data:</strong> {new Date(messageObj.created_at).toLocaleString('pt-BR')}</p>
            {loading && index === messages.length ? ( // Verifica se está carregando e se é a última mensagem
              <p>Carregando...</p> // Mostra a mensagem de loading
            ) : (
              <ReactMarkdown>{messageObj.message}</ReactMarkdown> // Renderiza a mensagem formatada
            )}
          </div>
        ))
      ) : (
        <p>Carregando...</p>
      )}
    </div>
  );
}

export default App;