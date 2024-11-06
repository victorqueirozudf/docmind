import axios from "axios";
import { useState } from "react";
import CryptoJS from "crypto-js";

export const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    const submit = async e => {
        e.preventDefault();

        // Obter as chaves do .env
        // Obtenha a chave e o IV das variáveis de ambiente
        const key = process.env.REACT_APP_KEY_CRYPTOGRAPHY;
        const iv = process.env.REACT_APP_IV_CRYPTOGRAPHY;

        const encryptPassword = (password) => {
            // Converte a chave e o IV para WordArray
            const keyWords = CryptoJS.enc.Utf8.parse(key);
            const ivWords = CryptoJS.enc.Utf8.parse(iv);

            // Encripta a senha
            const encrypted = CryptoJS.AES.encrypt(password, keyWords, {
                iv: ivWords,
                mode: CryptoJS.mode.CBC,
                padding: CryptoJS.pad.Pkcs7
            });

            // Retorna a senha encriptada em Base64
            return encrypted.toString();
        };

        const user = {
            username: username,
            password: encryptPassword(password)
        };

        try {
            console.log(user.password)
            const { data } = await axios.post('http://localhost:8000/authentication/login/', user, {
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            console.log("Meu token: " + data);
            localStorage.clear();
            localStorage.setItem('access_token', data.access);
            localStorage.setItem('refresh_token', data.refresh);
            axios.defaults.headers.common['Authorization'] = `Bearer ${data['access']}`;
            window.location.href = '/chat';

            alert('Logado!')
        } catch (error) {
            if (error.response && error.response.status === 401) {
                alert('Usuário não encontrado. Por favor, crie uma conta.');
            } else {
                console.error('Erro ao realizar login:', error);
                alert('Ocorreu um erro. Por favor, tente novamente.');
            }
        }
    };

    return (
        <div className="Auth-form-container">
            <form className="Auth-form" onSubmit={submit}>
                <div className="Auth-form-content">
                    <h3 className="Auth-form-title">Sign In</h3>
                    <div className="form-group mt-3">
                        <label>Username</label>
                        <input
                            className="form-control mt-1"
                            placeholder="Enter Username"
                            name='username'
                            type='text'
                            value={username}
                            required
                            onChange={e => setUsername(e.target.value)}
                        />
                    </div>
                    <div className="form-group mt-3">
                        <label>Password</label>
                        <input
                            name='password'
                            type="password"
                            className="form-control mt-1"
                            placeholder="Enter password"
                            value={password}
                            required
                            onChange={e => setPassword(e.target.value)}
                        />
                    </div>
                    <div className="d-grid gap-2 mt-3">
                        <button type="submit" className="btn btn-primary">
                            Submit
                        </button>
                    </div>
                </div>
            </form>
        </div>
    );
};