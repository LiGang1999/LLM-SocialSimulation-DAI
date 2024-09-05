import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import App from './App.tsx';
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

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <SimContextProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={
            <Navigate to="/welcome" replace />
          } />
          <Route path="/confirm" element={<ConfirmPage />} />
          <Route path="/llmconfig" element={<ConfigPage />} />
          <Route path="/templates" element={<TemplatePage />} />
          <Route path="/events" element={<EventsPage />} />
          <Route path="/welcome" element={<WelcomePage />} />
          <Route path="/agents" element={<AgentsPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/interact" element={<InteractPage />} />
          <Route path="/tabs" element={<TabsDemo />} />
        </Routes>
      </BrowserRouter>
    </SimContextProvider>
  </StrictMode>
);