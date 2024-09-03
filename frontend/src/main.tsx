import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
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

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />

        <Route path="/confirm" element={<ConfirmPage />} />

        <Route path="/llmconfig" element={<ConfigPage></ConfigPage>}></Route>

        <Route path="/templates" element={<TemplatePage></TemplatePage>}></Route>

        <Route path="/events" element={<EventsPage></EventsPage>}></Route>

        <Route path="/welcome" element={<WelcomePage />} />

        <Route path="/agents" element={<AgentsPage />} />

        {/* Define the path for the DashboardPage */}
        <Route path="/dashboard" element={<DashboardPage />} />

        <Route path="/interact" element={<InteractPage></InteractPage>}></Route>

        {/* Define the path for the TabsDemo page */}
        <Route path="/tabs" element={<TabsDemo />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>,
);
