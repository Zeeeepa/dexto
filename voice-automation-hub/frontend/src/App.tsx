import { useState, useEffect } from 'react';
import './App.css';
import { useVoiceRecognition } from './hooks/useVoiceRecognition';
import { config } from './lib/config';

interface Workflow {
  id: string;
  task: string;
  status: string;
  progress: number;
  agents?: Array<{
    name: string;
    status: string;
    role?: string;
  }>;
}

function App() {
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState<Array<{ role: string; content: string }>>([]);
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);

  const {
    isListening,
    transcript,
    startListening,
    stopListening,
    supported: voiceSupported,
    error: voiceError,
  } = useVoiceRecognition();

  // Update message when voice transcript changes
  useEffect(() => {
    if (transcript) {
      setMessage(transcript);
    }
  }, [transcript]);

  // Load workflows on mount
  useEffect(() => {
    loadWorkflows();
  }, []);

  const loadWorkflows = async () => {
    try {
      const response = await fetch(`${config.backendUrl}${config.apiEndpoints.workflows}`);
      const data = await response.json();
      setWorkflows(data.workflows || []);
    } catch (error) {
      console.error('Failed to load workflows:', error);
    }
  };

  const handleSendMessage = async () => {
    if (!message.trim()) return;

    const userMessage = message.trim();
    setMessage('');
    setIsProcessing(true);

    // Add user message to chat
    setChatHistory(prev => [...prev, { role: 'user', content: userMessage }]);

    try {
      // Send to backend
      const response = await fetch(`${config.backendUrl}${config.apiEndpoints.workflows}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task: userMessage }),
      });

      const workflow = await response.json();
      
      // Add assistant response
      setChatHistory(prev => [
        ...prev,
        {
          role: 'assistant',
          content: `✅ Created workflow: ${workflow.id}\n\nTask: ${workflow.task}\nStatus: ${workflow.status}`,
        },
      ]);

      // Refresh workflows
      await loadWorkflows();
    } catch (error) {
      console.error('Failed to send message:', error);
      setChatHistory(prev => [
        ...prev,
        { role: 'assistant', content: '❌ Failed to process request. Please try again.' },
      ]);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🎤 Voice Automation Hub</h1>
        <p className="subtitle">AI-Powered Multi-Agent Workflows</p>
      </header>

      <div className="container">
        {/* Chat Panel */}
        <div className="chat-panel">
          <div className="chat-header">
            <h2>💬 Conversation</h2>
            {voiceSupported && (
              <div className="voice-status">
                {isListening ? (
                  <span className="listening">🎤 Listening...</span>
                ) : (
                  <span className="ready">🎤 Ready</span>
                )}
              </div>
            )}
          </div>

          <div className="chat-messages">
            {chatHistory.length === 0 ? (
              <div className="welcome-message">
                <h3>👋 Welcome!</h3>
                <p>Start by giving a voice command or typing a task:</p>
                <ul>
                  <li>"Research the latest AI developments"</li>
                  <li>"Create a data processing pipeline"</li>
                  <li>"Run tests for the authentication module"</li>
                </ul>
              </div>
            ) : (
              chatHistory.map((msg, idx) => (
                <div key={idx} className={`message ${msg.role}`}>
                  <div className="message-role">
                    {msg.role === 'user' ? '👤 You' : '🤖 Assistant'}
                  </div>
                  <div className="message-content">{msg.content}</div>
                </div>
              ))
            )}
            {isProcessing && (
              <div className="message assistant">
                <div className="message-role">🤖 Assistant</div>
                <div className="message-content">
                  <span className="typing-indicator">Processing...</span>
                </div>
              </div>
            )}
          </div>

          <div className="chat-input-container">
            {voiceError && <div className="voice-error">{voiceError}</div>}
            
            <div className="chat-input">
              <textarea
                value={message}
                onChange={e => setMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your command or use voice..."
                disabled={isProcessing}
                rows={2}
              />
              
              <div className="input-actions">
                {voiceSupported && (
                  <button
                    onClick={isListening ? stopListening : startListening}
                    className={`voice-button ${isListening ? 'listening' : ''}`}
                    disabled={isProcessing}
                  >
                    {isListening ? '🛑 Stop' : '🎤 Voice'}
                  </button>
                )}
                
                <button
                  onClick={handleSendMessage}
                  className="send-button"
                  disabled={!message.trim() || isProcessing}
                >
                  ✉️ Send
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Workflows Panel */}
        <div className="workflows-panel">
          <div className="workflows-header">
            <h2>⚙️ Active Workflows</h2>
            <button onClick={loadWorkflows} className="refresh-button">
              🔄 Refresh
            </button>
          </div>

          <div className="workflows-list">
            {workflows.length === 0 ? (
              <div className="no-workflows">
                <p>No active workflows yet.</p>
                <p className="hint">Create your first workflow by sending a command!</p>
              </div>
            ) : (
              workflows.map(workflow => (
                <div key={workflow.id} className="workflow-card">
                  <div className="workflow-header">
                    <h3>{workflow.id}</h3>
                    <span className={`status-badge ${workflow.status}`}>
                      {workflow.status}
                    </span>
                  </div>
                  
                  <p className="workflow-task">{workflow.task}</p>
                  
                  <div className="workflow-progress">
                    <div className="progress-bar">
                      <div
                        className="progress-fill"
                        style={{ width: `${workflow.progress}%` }}
                      />
                    </div>
                    <span className="progress-text">{workflow.progress}%</span>
                  </div>

                  {workflow.agents && workflow.agents.length > 0 && (
                    <div className="workflow-agents">
                      <h4>🤖 Agents:</h4>
                      {workflow.agents.map((agent, idx) => (
                        <div key={idx} className="agent-item">
                          <span className="agent-name">{agent.name}</span>
                          <span className={`agent-status ${agent.status}`}>
                            {agent.status}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      <footer className="app-footer">
        <p>
          Powered by ChatKit & OpenAI • Backend: {config.backendUrl}
        </p>
      </footer>
    </div>
  );
}

export default App;

