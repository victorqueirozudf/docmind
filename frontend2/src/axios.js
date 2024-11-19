import axios from 'axios';

// Create an axios instance with default configurations
const API = axios.create({
  baseURL: 'http://localhost:8000/', // Replace with your API base URL
});

let isRefreshing = false; // Controle para evitar múltiplas requisições de renovação
let failedQueue = []; // Requisições aguardando o novo token

/**
 * Adiciona as requisições à fila enquanto o token está sendo renovado
 */
const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });

  failedQueue = [];
};

/**
 * Interceptor de requisição: Adiciona o token de acesso ao cabeçalho
 */
API.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access'); // Token de acesso
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

/**
 * Interceptor de resposta: Lida com tokens expirados
 */
API.interceptors.response.use(
  (response) => response, // Retorna a resposta normalmente
  async (error) => {
    const originalRequest = error.config;

    // Verifica se o erro é devido ao token expirado
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      if (isRefreshing) {
        // Adiciona a requisição atual à fila e aguarda
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers['Authorization'] = `Bearer ${token}`;
            return API(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      isRefreshing = true;

      const refreshToken = localStorage.getItem('refresh'); // Obtém o refresh token

      if (!refreshToken) {
        // Se não há refresh token, redireciona para login
        alert('Sessão expirada. Faça login novamente.');
        localStorage.removeItem('access');
        localStorage.removeItem('refresh');
        window.location.href = '/'; // Redireciona para a página de login
        return Promise.reject(error);
      }

      try {
        // Tenta renovar o token de acesso
        const response = await axios.post('http://localhost:8000/api/token/refresh/', {
          refresh: refreshToken,
        });

        const newAccessToken = response.data.access;

        // Salva o novo token no localStorage
        localStorage.setItem('access', newAccessToken);

        // Atualiza o cabeçalho do Axios com o novo token
        API.defaults.headers.common['Authorization'] = `Bearer ${newAccessToken}`;

        isRefreshing = false;

        // Processa as requisições na fila
        processQueue(null, newAccessToken);

        // Retenta a requisição original com o novo token
        originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
        return API(originalRequest);
      } catch (refreshError) {
        // Se a renovação falhar, limpa os tokens e redireciona
        processQueue(refreshError, null);
        localStorage.removeItem('access');
        localStorage.removeItem('refresh');
        alert('Sessão expirada. Faça login novamente.');
        window.location.href = '/';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Authentication API endpoints
export const authAPI = {
  // Login user
  login: (data) => API.post('authentication/login/', data),

  // Get user details
  getUserDetails: () => API.get('authentication/user/'),

  // Sign up new user
  signup: (data) => API.post('authentication/signup/', data),

  // Logout user
  logout: (data) => API.post('authentication/logout/', data),

  // Verify JWT token
  verifyToken: (data) => API.post('authentication/verify-token', data),
};

// Admin API endpoints
export const adminAPI = {
  // List all users (accessible only by superuser)
  listUsers: () => API.get('authentication/list-users/'),
};

// Chat API endpoints
export const chatAPI = {
  // Get all chats for the authenticated user
  getChats: () => API.get('api/chats/'),

  // Create a new chat with a PDF file
  createChat: (data) =>
    API.post('api/chats/', data, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }),

  // Delete a chat by thread_id
  deleteChat: (thread_id) => API.delete(`api/chats/delete/${thread_id}/`),

  // Update an existing chat by thread_id
  updateChat: (thread_id, data) =>
    API.put(`api/chats/put/${thread_id}/`, data, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }),

  // Get chat details and history by thread_id
  getChatDetails: (thread_id) => API.get(`api/chats/${thread_id}/`),

  // Send a question to the chat and receive an answer
  sendQuestionToChat: (thread_id, data) => API.put(`api/chats/${thread_id}/`, data),
};

export default API;
