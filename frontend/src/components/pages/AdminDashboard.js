import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI, adminAPI } from '../../axios';
import Navbar from '../layout/Navbar'

function AdminDashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null); // Dados do superusuário
  const [users, setUsers] = useState([]); // Lista de usuários
  const [loading, setLoading] = useState(true); // Indica se os dados estão carregando

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
      // API para deletar o usuário (substitua por sua API de deleção)
      alert(`Usuário com ID ${userId} será excluído.`); // Placeholder para deletar
      setUsers(users.filter((u) => u.id !== userId)); // Remove da lista local
    } catch (error) {
      console.error('Erro ao excluir usuário:', error);
    }
  };

  const handleResetPassword = async (userId) => {
    try {
      // API para redefinir senha (substitua por sua API de redefinição)
      alert(`Senha do usuário com ID ${userId} será redefinida.`); // Placeholder para redefinir
    } catch (error) {
      console.error('Erro ao redefinir senha do usuário:', error);
    }
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">Carregando...</div>;
  }

   /** 
   * Função para realizar o logout do usuário
   */
   const handleLogout = () => {
    const refreshToken = localStorage.getItem('refresh'); // Obtém o token de refresh

    if (!refreshToken) {
      console.error('Token de refresh não encontrado.');
      // Remove tokens existentes e redireciona
      localStorage.removeItem('access');
      localStorage.removeItem('refresh');
      localStorage.removeItem('sessionid');
      navigate('/');
      return;
    }

    const logoutData = {
      refresh_token: refreshToken, // Dados para logout
    };

    authAPI
      .logout(logoutData) // Chama a API de logout
      .then((response) => {
        // Remove tokens do localStorage
        localStorage.removeItem('access');
        localStorage.removeItem('refresh');
        localStorage.removeItem('sessionid');

        // Redireciona para a página de login
        navigate('/');
      })
      .catch((error) => {
        // Mesmo se o logout falhar, remove tokens e redireciona
        localStorage.removeItem('access');
        localStorage.removeItem('refresh');
        localStorage.removeItem('sessionid');

        navigate('/');

        console.error('Erro ao fazer logout:', error);
      });
  };

  return (
  <>
    <Navbar onLogout={handleLogout} user={user} />

    <div className="min-h-screen flex flex-col bg-gray-100 p-5">
      <h1 className="text-3xl font-bold mb-5">Painel de Administrador</h1>
      <p className="text-gray-700">Bem-vindo, {user?.username}. Você é um superusuário!</p>

      <div className="mt-10">
        <h2 className="text-2xl font-bold mb-4">Usuários Cadastrados</h2>
        <div className="overflow-x-auto bg-white p-4 shadow rounded-lg">
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
                        onClick={() => handleDeleteUser(user.id)}
                        className="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600"
                      >
                        Excluir
                      </button>
                      <button
                        onClick={() => handleResetPassword(user.id)}
                        className="bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600"
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
  </>
  );
}

export default AdminDashboard;
