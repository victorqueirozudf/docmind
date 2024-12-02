import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI, adminAPI } from '../../axios';
import Navbar from '../layout/Navbar';

function AdminDashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null); // Dados do superusuário
  const [users, setUsers] = useState([]); // Lista de usuários
  const [loading, setLoading] = useState(true); // Indica se os dados estão carregando
  const [showCreateUserModal, setShowCreateUserModal] = useState(false); // Controla a modal de criação
  const [showConfirmationModal, setShowConfirmationModal] = useState(false); // Controla a modal de confirmação
  const [confirmationAction, setConfirmationAction] = useState(null); // Função para ação de confirmação
  const [confirmationMessage, setConfirmationMessage] = useState(''); // Mensagem da modal de confirmação
  const [confirmationText, setConfirmationText] = useState(''); // Mensagem da modal de confirmação
  const [selectedUserId, setSelectedUserId] = useState(null); // ID do usuário selecionado

  useEffect(() => {
    const fetchUserDetails = async () => {
      try {
        const response = await authAPI.getUserDetails(); // Busca detalhes do superusuário
        setUser(response.data);

        if (!response.data.is_superuser) {
          alert('Acesso restrito! Apenas superusuários podem acessar esta página.');
          navigate('/chat'); // Redireciona para o chat
        }
      } catch (error) {
        console.error('Erro ao verificar o usuário:', error);
        navigate('/login'); // Redireciona para o login se não autenticado
      } finally {
        setLoading(false);
      }
    };

    fetchUserDetails();
  }, [navigate]);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const response = await adminAPI.listUsers(); // Busca lista de usuários
        setUsers(response.data); // Atualiza a lista de usuários
      } catch (error) {
        console.error('Erro ao buscar lista de usuários:', error);
      }
    };

    if (user?.is_superuser) {
      fetchUsers(); // Busca usuários apenas se for superusuário
    }
  }, [user]);

  const handleDeleteUser = async (userId) => {
    try {
      console.log(userId)
      // Inclua o `userId` como parte da URL
      await authAPI.delete(`${userId}`); 
      alert(`Usuário com ID ${userId} foi excluído.`);
      setUsers(users.filter((u) => u.id !== userId)); // Remove da lista local
    } catch (error) {
      console.error('Erro ao excluir usuário:', error);
      alert('Não foi possível excluir o usuário. Tente novamente.');
    }
  };

  const handleResetPassword = async (userId) => {
    try {
      await authAPI.redefinePassword(`${userId}`); // Chama a API para redefinir a senha do usuário
      alert(`Senha do usuário com ID ${userId} foi redefinida para a senha padrão.`);
    } catch (error) {
      console.error('Erro ao redefinir senha do usuário:', error);
      alert('Não foi possível redefinir a senha do usuário. Tente novamente.');
    }
  };

  const openConfirmationModal = (action, message, text, userId) => {
    setConfirmationAction(() => action); // Define a ação de confirmação
    setConfirmationMessage(message); // Define a mensagem da modal
    setConfirmationText(text);
    setSelectedUserId(userId); // Define o ID do usuário
    setShowConfirmationModal(true); // Abre a modal
  };

  const confirmAction = () => {
    if (confirmationAction) {
      confirmationAction(selectedUserId);
    }
    setShowConfirmationModal(false); // Fecha a modal após a confirmação
  };

  const handleCreateUser = async (username, isSuperuser = false) => {
    try {
      const data = { username };
      console.log("Enviando dados para o backend:", data); // Log para verificar os dados enviados
      const response = await authAPI.registerUser(data);
      alert(`Usuário ${response.data.username} criado com sucesso!`);
      // Atualiza a lista de usuários
      const updatedUsers = await adminAPI.listUsers();
      setUsers(updatedUsers.data);
      setShowCreateUserModal(false); // Fecha o modal
    } catch (error) {
      console.error('Erro ao criar usuário:', error.response?.data || error.message);
      alert('Erro ao criar usuário. Verifique os dados e tente novamente.');
    }
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">Carregando...</div>;
  }

  return (
    <>
      <Navbar user={user} /> {/* Remova a prop onLogout */}

      <div className="h-full flex flex-col p-5">
        <h1 className="text-3xl font-bold mb-4 caret-transparent">Painel de Administrador</h1>

        <div className="mt-4 caret-transparent">
          <h2 className="text-2xl font-bold mb-4">Usuários Cadastrados</h2>

          <div className="flex justify-end mb-4">
            <button
              onClick={() => setShowCreateUserModal(true)}
              className="bg-black text-white px-4 py-2 rounded-lg hover:bg-gray-800"
            >
              + Criar Novo Usuário
            </button>
          </div>

          <div className="overflow-x-auto bg-white shadow rounded-lg">
            {users.length > 0 ? (
              <table className="min-w-full table-auto border-collapse">
                <thead>
                  <tr>
                    <th className="border px-4 py-2 text-left">ID</th>
                    <th className="border px-4 py-2 text-left">Nome</th>
                    <th className="border px-4 py-2 text-left">Superusuário</th>
                    <th className="border px-4 py-2 text-center">Ações</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user.id} className="hover:bg-gray-100">
                      <td className="border px-4 py-2">{user.id}</td>
                      <td className="border px-4 py-2">{user.username}</td>
                      <td className="border px-4 py-2">{user.is_superuser ? 'Sim' : 'Não'}</td>
                      <td className="border px-4 py-2 flex justify-center gap-2">
                        <button
                          onClick={() =>
                            openConfirmationModal(
                              handleDeleteUser, 
                              'Deseja excluir o usuário?', 
                              'Ao excluir o usuário, você excluir todo o histórico do chat dele?',
                              user.id
                            )
                          }
                          className=" text-black px-3 py-1 rounded hover:underline"
                        >
                          Excluir
                        </button>
                        <button
                          onClick={() =>
                            openConfirmationModal(
                              handleResetPassword,
                              'Deseja redefinir a senha do usuário?',
                              'Ao redefinir a senha do usuário, você define a senha padrão para ele.',
                              user.id
                            )
                          }
                          className="bg-black text-white px-3 py-1 rounded hover:bg-gray-800"
                        >
                          Redefinir Senha
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="text-gray-500">Nenhum usuário encontrado.</p>
            )}
          </div>
        </div>
      </div>

      {/* Modal de Confirmação */}
      {showConfirmationModal && (
        <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg w-1/3">
            <h2 className="text-xl font-bold mb-4 caret-transparent">{confirmationMessage}</h2>
            <p className="text-gray-700 mb-6">{confirmationText}</p>
            <div className="flex justify-center gap-2">
              <button
                onClick={() => setShowConfirmationModal(false)}
                className=" text-black px-4 py-2 rounded-lg hover:underline"
              >
                Cancelar
              </button>
              <button
                onClick={confirmAction}
                className="bg-black text-white px-4 py-2 rounded-lg hover:bg-gray-800"
              >
                Confirmar
              </button>
            </div>
          </div>
        </div>
      )}

      {showCreateUserModal && (
        <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg w-1/3">
            <h2 className="text-xl font-bold mb-4 caret-transparent">Criar Novo Usuário</h2>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                const username = e.target.username.value;
                handleCreateUser(username);
              }}
            >
              <div className="mb-4">
                <label className="block text-gray-700 mb-2 caret-inherit">Nome de Usuário</label>
                <input
                  type="text"
                  name="username"
                  placeholder="Digite o nome do usuário..."
                  required
                  className="w-full border px-3 py-2 rounded-lg"
                />
              </div>
              <p className='text-gray-700'>Este usuário virá com a senha padrão.</p>
              <div className="flex justify-end gap-2 caret-transparent">
                <button
                  type="button"
                  onClick={() => setShowCreateUserModal(false)}
                  className=" text-black px-4 py-2 rounded-lg hover:underline"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="bg-black text-white px-4 py-2 rounded-lg hover:bg-gray-800"
                >
                  Criar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}

export default AdminDashboard;
