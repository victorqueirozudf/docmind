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
        setResponse(data.answer);
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
        <button type="submit">Enviar</button>
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

export default App;
