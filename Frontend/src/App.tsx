import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
// IMPORT YOUR INDEX FILE HERE (Adjust the path if it's not in the same folder)
import Dashboard from './pages/Dashboard';
import Blog from './pages/Blog';
import { TooltipProvider } from "@/components/ui/tooltip";

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
    <TooltipProvider delayDuration={300}>
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <Routes>
          {/* Public Route */}
          <Route path="/login" element={<Login />} />

          {/* Protected Route (Your main application) */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />

          <Route
            path="/blog"
            element={
              <ProtectedRoute>
                <Blog />
              </ProtectedRoute>
            }
          />

          {/* Catch-all: If they type a weird URL, send them home */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  );
};

export default App;