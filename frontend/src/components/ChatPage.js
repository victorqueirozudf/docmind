import React, { useState } from 'react';

const ChatPage = () => {
    const [chats, setChats] = useState([]); // Estado para armazenar chats
    const [selectedChat, setSelectedChat] = useState(null); // Estado para armazenar chat selecionado
    const [newChatName, setNewChatName] = useState(''); // Estado para armazenar o nome do novo chat

    // Função para adicionar um novo chat
    const createChat = () => {
        if (newChatName) {
            const newChat = { id: Date.now(), name: newChatName, messages: [] };
            setChats([...chats, newChat]);
            setNewChatName('');
        }
    };

    // Função para selecionar um chat
    const selectChat = (chat) => {
        setSelectedChat(chat);
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
                <button onClick={createChat}>Criar Chat</button>
                <ul>
                    {chats.map((chat) => (
                        <li key={chat.id} onClick={() => selectChat(chat)} style={{ cursor: 'pointer' }}>
                            {chat.name}
                        </li>
                    ))}
                </ul>
            </div>
            <div style={{ flex: 1, padding: '10px' }}>
                {selectedChat ? (
                    <div>
                        <h2>{selectedChat.name}</h2>
                        <ul>
                            {selectedChat.messages.map((msg, index) => (
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
