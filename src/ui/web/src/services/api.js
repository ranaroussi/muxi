import axios from 'axios';

// Create axios instance with base URL
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || '',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Error handling interceptor
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.message ||
      'Unknown error occurred';
    console.error('API Error:', message);
    return Promise.reject(message);
  }
);

// Agents API
export const fetchAgents = () => api.get('/agents');
export const createAgent = (agentData) => api.post('/agents', agentData);
export const deleteAgent = (agentId) => api.delete(`/agents/${agentId}`);
export const chatWithAgent = (message, agentId) =>
  api.post('/agents/chat', { message, agent_id: agentId });

// Memory API
export const searchMemory = (query, agentId, limit = 5, useLongTerm = true) =>
  api.post('/agents/memory/search', {
    query,
    agent_id: agentId,
    limit,
    use_long_term: useLongTerm
  });

// Tools API
export const fetchTools = () => api.get('/tools');

// WebSocket connection
export const createWebSocketConnection = (onMessage, onOpen, onClose, onError) => {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = process.env.REACT_APP_API_URL || window.location.host;
  const url = `${protocol}//${host}/ws`;

  const socket = new WebSocket(url);

  socket.onopen = (event) => {
    console.log('WebSocket connection established');
    if (onOpen) onOpen(event);
  };

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      if (onMessage) onMessage(data);
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  };

  socket.onclose = (event) => {
    console.log('WebSocket connection closed', event);
    if (onClose) onClose(event);
  };

  socket.onerror = (error) => {
    console.error('WebSocket error:', error);
    if (onError) onError(error);
  };

  return {
    socket,

    // Subscribe to an agent
    subscribeToAgent: (agentId) => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({
          type: 'subscribe',
          agent_id: agentId
        }));
      }
    },

    // Send a message to an agent
    sendMessage: (message, agentId) => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({
          type: 'chat',
          message,
          agent_id: agentId
        }));
      }
    },

    // Close the WebSocket connection
    close: () => {
      socket.close();
    }
  };
};
