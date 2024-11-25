import React, { useState, useEffect } from "react";
import { authAPI } from "../../axios";

function ChangePasswordModal({ showModal, onClose }) {
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleSubmit = async () => {
    setError(null);
    setSuccess(null);

    if (!currentPassword || !newPassword || !confirmPassword) {
      setError("Todos os campos são obrigatórios.");
      return;
    }

    if (newPassword !== confirmPassword) {
      setError("As senhas não coincidem.");
      return;
    }

    try {
      const response = await authAPI.changePassword({
        current_password: currentPassword,
        new_password: newPassword,
      });
      setSuccess(response.data.message);
      setCurrentPassword("");
      setNewPassword("");
      // Fecha a modal após o sucesso
      setTimeout(() => {
        onClose();
        setSuccess(null);
      }, 1000); // Opcional: Tempo para o usuário ver a mensagem de sucesso
    } catch (err) {
      setError(err.response?.data?.error || "Erro ao alterar a senha.");
    }
  };

  // Limpa as mensagens e os campos ao fechar a modal
  useEffect(() => {
    if (!showModal) {
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setError(null);
      setSuccess(null);
    }
  }, [showModal]);

  if (!showModal) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg w-1/3 p-6 relative shadow-lg">
        <button onClick={onClose} className="absolute top-4 right-4 text-gray-600 hover:text-black">
          ✖
        </button>
        <h2 className="text-2xl font-bold mb-4 text-black caret-transparent">Alterar Senha</h2>

        {error && <p className="text-red-500 mb-4 caret-transparent">{error}</p>}
        {success && <p className="text-green-500 mb-4 caret-transparent">{success}</p>}

        <div className="space-y-3">
          <div>
            <label className="block font-semibold mb-1 text-black caret-transparent">Senha Atual</label>
            <input
              type="password"
              placeholder="Digite sua senha atual..."
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              className="w-full px-4 py-2 border rounded-lg text-black caret-inherit"
              required
            />
          </div>

          <div>
            <label className="block font-semibold mb-1 text-black caret-transparent">Nova Senha</label>
            <input
              type="password"
              placeholder="Digite sua nova senha..."
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className="w-full px-4 py-2 border rounded-lg text-black caret-inherit"
              required
            />
          </div>

          <div>
            <label className="block font-semibold mb-1 text-black caret-transparent">Confirmar Nova Senha</label>
            <input
              type="password"
              placeholder="Digite a sua nova senha novamente..."
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="w-full px-4 py-2 border rounded-lg text-black caret-inherit"
              required
            />
          </div>

          <button
            onClick={handleSubmit}
            className="w-full py-2 bg-black text-white rounded-lg font-semibold caret-transparent hover:bg-gray-800"
          >
            Alterar Senha
          </button>
        </div>
      </div>
    </div>
  );
}

export default ChangePasswordModal;