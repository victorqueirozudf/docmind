import React, { useRef, useEffect } from 'react';

const ChatDropdown = ({ isOpen, onClose, onUpdate, onDelete }) => {
  const dropdownRef = useRef(null);

  // Fechar o dropdown ao clicar fora dele
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        onClose();
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [onClose]);

  if (!isOpen) return null;

  return (
    <div ref={dropdownRef} className="absolute bg-white border rounded-lg shadow-md left-6 top-1 mt-2 w-32 z-10">
      <button
        onClick={onUpdate}
        className="block w-full text-left px-4 py-2 text-sm hover:bg-gray-100"
      >
        Atualizar
      </button>
      <button
        onClick={onDelete}
        className="block w-full text-left px-4 py-2 text-sm hover:bg-gray-100"
      >
        Apagar
      </button>
    </div>
  );
};

export default ChatDropdown;
