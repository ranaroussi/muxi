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
  // Use the same WebSocket URL construction logic as the test HTML
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const port = 5050; // Hardcoded to 5050 for API server
  const wsUrl = `${protocol}//localhost:${port}/ws`;

  console.log('Connecting to WebSocket server at:', wsUrl);

  let socket = null;
  let subscribedAgentId = null;

  try {
    // Create a direct WebSocket connection
    socket = new WebSocket(wsUrl);

    socket.onopen = (event) => {
      console.log('WebSocket connection established successfully');
      if (onOpen) onOpen(event);
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('WebSocket message received:', data);

        // Track subscriptions
        if (data.type === 'subscribed') {
          subscribedAgentId = data.agent_id;
          console.log(`Successfully subscribed to agent: ${data.agent_id}`);
        }

        if (onMessage) onMessage(data);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    socket.onclose = (event) => {
      console.log(`WebSocket connection closed with code ${event.code}, reason: ${event.reason || 'No reason'}`);

      // Reset subscription state
      subscribedAgentId = null;

      if (onClose) onClose(event);
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      if (onError) onError(error);
    };
  } catch (error) {
    console.error('Error creating WebSocket:', error);
    if (onError) onError(error);
    return {
      socket: null,
      subscribeToAgent: () => false,
      sendMessage: () => false,
      close: () => {}
    };
  }

  return {
    socket,

    // Subscribe to an agent
    subscribeToAgent: (agentId) => {
      if (!agentId) {
        console.error('Cannot subscribe: No agent ID provided');
        return false;
      }

      if (socket && socket.readyState === WebSocket.OPEN) {
        console.log(`Subscribing to agent: ${agentId}`);
        try {
          socket.send(JSON.stringify({
            type: 'subscribe',
            agent_id: agentId
          }));
          return true;
        } catch (error) {
          console.error('Error sending subscription message:', error);
          return false;
        }
      } else {
        console.error(`Cannot subscribe to agent ${agentId}: WebSocket not connected (state: ${socket?.readyState})`);
        return false;
      }
    },

    // Send a message to an agent
    sendMessage: (message, agentId) => {
      if (!agentId) {
        console.error('Cannot send message: No agent ID provided');
        return false;
      }

      if (socket && socket.readyState === WebSocket.OPEN) {
        try {
          console.log(`Sending message to agent ${agentId}:`, message);
          socket.send(JSON.stringify({
            type: 'chat',
            message,
            agent_id: agentId
          }));
          return true;
        } catch (error) {
          console.error('Error sending chat message:', error);
          return false;
        }
      } else {
        console.error(`Cannot send message: WebSocket not connected (state: ${socket?.readyState})`);
        return false;
      }
    },

    // Close the WebSocket connection
    close: () => {
      if (socket) {
        try {
          socket.close(1000, 'Client closing connection');
        } catch (error) {
          console.error('Error closing WebSocket:', error);
        }
      }
    }
  };
};
