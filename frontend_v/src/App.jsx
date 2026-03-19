import React, { useState, useEffect } from 'react';
import ChatWindow from './components/ChatWindow';
import Sidebar from './components/Sidebar';
import { getSessions, deleteSession, renameSession } from './services/api';
import './index.css';

function App() {
  const [sessions, setSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [darkMode, setDarkMode] = useState(
    () => localStorage.getItem('darkMode') === 'true'
  );

  // Apply/remove dark class on <html>
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('darkMode', 'true');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('darkMode', 'false');
    }
  }, [darkMode]);

  const fetchSessions = async () => {
    try { setSessions(await getSessions()); }
    catch (e) { console.error('Error fetching sessions:', e); }
  };

  useEffect(() => { fetchSessions(); }, []);

  const handleRenameSession = async (id, title) => {
    try { await renameSession(id, title); fetchSessions(); }
    catch (e) { console.error(e); }
  };

  const handleDeleteSession = async (id) => {
    if (!window.confirm('Delete this chat?')) return;
    try {
      await deleteSession(id);
      if (currentSessionId === id) setCurrentSessionId(null);
      fetchSessions();
    } catch (e) { console.error(e); }
  };

  const currentSession = sessions.find(s => s.id === currentSessionId);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-white dark:bg-gray-950">
      <Sidebar
        sessions={sessions}
        currentSessionId={currentSessionId}
        onSelectSession={setCurrentSessionId}
        onNewSession={() => setCurrentSessionId(null)}
        onRenameSession={handleRenameSession}
        onDeleteSession={handleDeleteSession}
        darkMode={darkMode}
        onToggleDarkMode={() => setDarkMode(d => !d)}
      />
      <ChatWindow
        sessionId={currentSessionId}
        currentSession={currentSession}
        onSessionCreated={(id) => { setCurrentSessionId(id); fetchSessions(); }}
      />
    </div>
  );
}

export default App;
