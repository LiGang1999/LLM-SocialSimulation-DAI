import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import DashboardPage from './pages/dashboard.tsx';
import { TabsDemo } from './pages/tabsdemo.tsx';
import './index.css';
import { WelcomePage } from './pages/welcome.tsx';
import { TemplatePage } from './pages/templates.tsx';
import { EventsPage } from './pages/events.tsx';
import { AgentsPage } from './pages/agents.tsx';
import { ConfigPage } from './pages/llmconfig.tsx';
import { ConfirmPage } from './pages/confirm.tsx';
import { InteractPage } from './pages/interact.tsx';
import { SimContextProvider } from './SimContext.tsx';
import { LoginPage } from './pages/login.tsx';
import { RegisterPage } from './pages/register.tsx';
import { AuthProvider } from './contexts/AuthContext.tsx';
import { ProtectedRoute } from './components/ProtectedRoute.tsx';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <SimContextProvider>
      <AuthProvider>
        <BrowserRouter basename={process.env.LISTEN_PREFIX}>
          <Routes>
            <Route path="/" element={
              <Navigate to="/welcome" replace />
            } />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/welcome" element={<WelcomePage />} />
            <Route path="/templates" element={<TemplatePage />} />

            {/* Protected Routes */}
            <Route path="/confirm" element={
              <ProtectedRoute>
                <ConfirmPage />
              </ProtectedRoute>
            } />
            <Route path="/llmconfig" element={
              <ProtectedRoute>
                <ConfigPage />
              </ProtectedRoute>
            } />
            <Route path="/events" element={
              <ProtectedRoute>
                <EventsPage />
              </ProtectedRoute>
            } />
            <Route path="/agents" element={
              <ProtectedRoute>
                <AgentsPage />
              </ProtectedRoute>
            } />
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            } />
            <Route path="/interact" element={
              <ProtectedRoute>
                <InteractPage />
              </ProtectedRoute>
            } />
            <Route path="/tabs" element={
              <ProtectedRoute>
                <TabsDemo />
              </ProtectedRoute>
            } />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </SimContextProvider>
  </StrictMode>
);
