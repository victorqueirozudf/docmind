import { useState } from 'react';

function App() {
    const [pdfFile, setPdfFile] = useState(null);
    const [question, setQuestion] = useState('');
    const [answer, setAnswer] = useState('');

    const handleFileChange = (event) => {
        setPdfFile(event.target.files[0]);
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        const formData = new FormData();
        formData.append('pdf', pdfFile);
        formData.append('question', question);

        const response = await fetch('http://localhost:8000/talkpdf/ask/', {
            method: 'POST',
            body: formData,
        });

        const data = await response.json();
        setAnswer(data.answer);
    };

    return (
        <div>
            <form onSubmit={handleSubmit}>
                <input type="file" onChange={handleFileChange} />
                <input
                    type="text"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="Faça sua pergunta"
                />
                <button type="submit">Perguntar</button>
            </form>
            {answer && <p>Resposta: {answer}</p>}
        </div>
    );
}

export default App;
