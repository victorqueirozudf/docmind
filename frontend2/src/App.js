import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './components/pages/Login';
import Register from './components/pages/Register';
import Chat from './components/pages/Chat';
import ProtectedRoute from './ProtectedRoute';
import NotFound from './components/pages/NotFound'
import AdminDashboard from './components/pages/AdminDashboard';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/notFound" element={<NotFound/>}/>
        <Route
          path="/chat"
          element={
            <ProtectedRoute>
              <Chat/>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin"
          element={
            <ProtectedRoute>
              <AdminDashboard/>
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;

// App.js
/*import React, { useState } from 'react';

function App() {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const toggleDropdown = () => {
    setIsDropdownOpen(!isDropdownOpen);
  };

  const closeDropdown = () => {
    setIsDropdownOpen(false);
  };

  return (
    <ol>
      <li>
      <div className="flex flex-col justify-center relative w-full max-w-[320px] leading-1.5 p-6 border-gray-200 bg-gray-100 rounded-e-xl rounded-es-xl dark:bg-gray-700" onClick={closeDropdown}>
      <div className="self-start">
        <p>desgraça tube</p>
      </div>
      <div className='absolute inline-flex items-center self-end'>
        <button
          onClick={(e) => {
            e.stopPropagation(); // Prevents click event from closing the dropdown
            toggleDropdown();
          }}
          className="inline-flex self-center items-center ml-6 p-2 text-sm font-medium text-center text-gray-900 bg-white rounded-lg hover:bg-gray-100 focus:ring-4 focus:outline-none dark:text-white focus:ring-gray-50 dark:bg-gray-900 dark:hover:bg-gray-800 dark:focus:ring-gray-600"
          type="button"
        >
          <svg
            className="w-4 h-4 text-gray-500 dark:text-gray-400"
            aria-hidden="true"
            xmlns="http://www.w3.org/2000/svg"
            fill="currentColor"
            viewBox="0 0 4 15"
          >
            <path d="M3.5 1.5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0Zm0 6.041a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0Zm0 5.959a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0Z" />
          </svg>
        </button>
        {isDropdownOpen && (
          <div
            className="absolute z-10 bg-white divide-y divide-gray-100 rounded-lg shadow w-40 dark:bg-gray-700 dark:divide-gray-600"
            style={{ top: '100%', left: '48px' }}
          >
            <ul className="py-2 text-sm text-gray-700 dark:text-gray-200">
              <li>
                <a href="/" className="block px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white">
                  Atualizar
                </a>
              </li>
              <li>
                <a href="/" className="block px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white">
                  Apagar
                </a>
              </li>
            </ul>
          </div>
        )}
      </div>
    </div>
      </li>
    </ol>
  );
}

export default App;*/


