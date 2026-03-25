import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
// IMPORT YOUR INDEX FILE HERE (Adjust the path if it's not in the same folder)
import Index from './pages/Index';

// This is the gatekeeper. It checks for the token.
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const token = localStorage.getItem('token');

  if (!token) {
    // No token? Kick them back to login.
    return <Navigate to="/login" replace />;
  }

  // Has token? Let them through to the main index.
  return <>{children}</>;
};

const App = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Route */}
        <Route path="/login" element={<Login />} />

        {/* Protected Route (Your main application) */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              {/* WE USE INDEX HERE INSTEAD OF DASHBOARD */}
              <Index />
            </ProtectedRoute>
          }
        />

        {/* Catch-all: If they type a weird URL, send them home */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;