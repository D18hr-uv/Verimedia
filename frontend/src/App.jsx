import { useState, useEffect } from 'react';
import axios from 'axios';
import reactLogo from './assets/react.svg';
import viteLogo from '/vite.svg';
import './App.css';

function App() {
  const [backendMessage, setBackendMessage] = useState('Connecting to backend...');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchBackendMessage = async () => {
      try {
        const response = await axios.get('http://localhost:8000');
        setBackendMessage(response.data.message);
      } catch (error) {
        console.error('Error fetching data from backend:', error);
        setBackendMessage('Failed to connect to backend. Is the server running?');
      } finally {
        setIsLoading(false);
      }
    };

    fetchBackendMessage();
  }, []);

  return (
    <>
      <div>
        <a href="https://vitejs.dev" target="_blank" rel="noopener noreferrer">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank" rel="noopener noreferrer">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>VeriMedia</h1>
      <div className="card">
        <p>
          <strong>Backend Status:</strong> {isLoading ? 'Loading...' : backendMessage}
        </p>
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
    </>
  );
}

export default App;