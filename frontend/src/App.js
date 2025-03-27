import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FiSun, FiMoon, FiSettings } from 'react-icons/fi';
import ChatWindow from './components/ChatWindow';
import ChatInput from './components/ChatInput';
import SettingsPanel from './components/SettingsPanel';

const AppContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 1400px;
  margin: 0 auto;
  padding: 1rem;
  
  @media (min-width: 768px) {
    padding: 2rem;
  }
`;

const Header = styled.header`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
`;

const Logo = styled.div`
  display: flex;
  align-items: center;
  gap: 0.8rem;
  
  h1 {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--primary-color);
    
    @media (min-width: 768px) {
      font-size: 1.8rem;
    }
  }
  
  span {
    color: var(--text-secondary);
    font-size: 0.8rem;
    background: var(--surface-color);
    padding: 0.2rem 0.5rem;
    border-radius: 12px;
    font-weight: 500;
  }
`;

const Controls = styled.div`
  display: flex;
  gap: 0.8rem;
`;

const IconButton = styled.button`
  background: var(--surface-color);
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--text-primary);
  font-size: 1.2rem;
  box-shadow: var(--shadow);
  transition: all 0.2s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
  
  &:active {
    transform: translateY(0);
  }
`;

const Main = styled.main`
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--surface-color);
  border-radius: 12px;
  box-shadow: var(--shadow);
`;

function App() {
    const [messages, setMessages] = useState([]);
    const [darkMode, setDarkMode] = useState(false);
    const [showSettings, setShowSettings] = useState(false);
    const [settings, setSettings] = useState({
        temperature: 0.7,
        apiEndpoint: process.env.REACT_APP_API_URL || '/api/chat',
        modelName: 'gpt-4o-mini'
    });
    const [loading, setLoading] = useState(false);

    // Apply theme to document
    useEffect(() => {
        document.body.setAttribute('data-theme', darkMode ? 'dark' : 'light');
    }, [darkMode]);

    // Send message to API
    const sendMessage = async (content) => {
        if (!content.trim()) return;

        // Add user message to chat
        const userMessage = { role: 'user', content };
        setMessages(prev => [...prev, userMessage]);

        setLoading(true);

        try {
            // Prepare messages for API
            const messagesForApi = [...messages, userMessage].map(m => ({
                role: m.role,
                content: m.content
            }));

            // Call backend API
            const response = await fetch(settings.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    messages: messagesForApi,
                    temperature: settings.temperature
                }),
            });

            if (!response.ok) {
                throw new Error(`API returned status code ${response.status}`);
            }

            const data = await response.json();

            // Add assistant response to chat
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: data.response
            }]);

        } catch (error) {
            console.error('Error sending message:', error);

            // Add error message to chat
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: `Error: ${error.message}. Please check your API connection.`
            }]);

        } finally {
            setLoading(false);
        }
    };

    // Clear all messages
    const clearMessages = () => {
        setMessages([]);
    };

    // Update settings
    const updateSettings = (newSettings) => {
        setSettings(prev => ({ ...prev, ...newSettings }));
        setShowSettings(false);
    };

    return (
        <AppContainer>
            <Header>
                <Logo>
                    <h1>AI Chat Assistant</h1>
                    <span>{settings.modelName}</span>
                </Logo>
                <Controls>
                    <IconButton
                        onClick={() => setDarkMode(prev => !prev)}
                        aria-label={darkMode ? "Switch to light mode" : "Switch to dark mode"}
                    >
                        {darkMode ? <FiSun /> : <FiMoon />}
                    </IconButton>
                    <IconButton
                        onClick={() => setShowSettings(prev => !prev)}
                        aria-label="Settings"
                    >
                        <FiSettings />
                    </IconButton>
                </Controls>
            </Header>

            <Main>
                <ChatWindow
                    messages={messages}
                    loading={loading}
                />
                <ChatInput
                    onSendMessage={sendMessage}
                    disabled={loading}
                />
            </Main>

            {showSettings && (
                <SettingsPanel
                    settings={settings}
                    onSave={updateSettings}
                    onCancel={() => setShowSettings(false)}
                    onClearMessages={clearMessages}
                />
            )}
        </AppContainer>
    );
}

export default App; 