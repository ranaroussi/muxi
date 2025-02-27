import { useState, useEffect, useCallback, useRef } from 'react';
import { createWebSocketConnection } from '../services/api';

/**
 * Custom hook for WebSocket communication with agents
 * @param {Object} options Configuration options
 * @param {string} options.agentId The agent ID to subscribe to
 * @param {Function} options.onMessage Callback for incoming messages
 * @param {Function} options.onOpen Callback for when connection opens
 * @param {Function} options.onClose Callback for when connection closes
 * @param {Function} options.onError Callback for connection errors
 * @param {boolean} options.autoReconnect Whether to automatically reconnect
 * @param {number} options.reconnectInterval Interval in ms between reconnect attempts
 * @param {number} options.maxReconnectAttempts Maximum number of reconnect attempts
 * @returns {Object} WebSocket connection utilities
 */
function useWebSocket({
  agentId = null,
  onMessage = null,
  onOpen = null,
  onClose = null,
  onError = null,
  autoReconnect = true,
  reconnectInterval = 3000,
  maxReconnectAttempts = 5
}) {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const [agentIsThinking, setAgentIsThinking] = useState(false);
  const connectionRef = useRef(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef(null);

  // Handle incoming messages
  const handleMessage = useCallback((data) => {
    setLastMessage(data);

    // Update agent thinking state
    if (data.type === 'agent_thinking') {
      setAgentIsThinking(true);
    } else if (data.type === 'agent_done' || data.type === 'response' || data.type === 'error') {
      setAgentIsThinking(false);
    }

    // Call user-provided handler
    if (onMessage) onMessage(data);
  }, [onMessage]);

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (isConnecting) return;

    setIsConnecting(true);

    // Close existing connection if it exists
    if (connectionRef.current) {
      connectionRef.current.close();
    }

    // Create new connection
    const connection = createWebSocketConnection(
      // Handle message
      handleMessage,

      // Handle open
      (event) => {
        setIsConnected(true);
        setIsConnecting(false);
        reconnectAttemptsRef.current = 0;

        // Subscribe to agent if agentId is provided
        if (agentId) {
          connection.subscribeToAgent(agentId);
        }

        if (onOpen) onOpen(event);
      },

      // Handle close
      (event) => {
        setIsConnected(false);
        setIsConnecting(false);

        // Attempt to reconnect if not a clean close and autoReconnect is enabled
        if (autoReconnect && event.code !== 1000 && event.code !== 1001) {
          scheduleReconnect();
        }

        if (onClose) onClose(event);
      },

      // Handle error
      (error) => {
        setIsConnecting(false);

        if (onError) onError(error);
      }
    );

    connectionRef.current = connection;
  }, [agentId, autoReconnect, handleMessage, isConnecting, onOpen, onClose, onError]);

  // Schedule reconnect
  const scheduleReconnect = useCallback(() => {
    if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
      console.log(`Max reconnect attempts (${maxReconnectAttempts}) reached.`);
      return;
    }

    // Clear any existing timeout
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    // Schedule reconnect
    reconnectTimeoutRef.current = setTimeout(() => {
      reconnectAttemptsRef.current += 1;
      console.log(`Reconnecting... Attempt ${reconnectAttemptsRef.current} of ${maxReconnectAttempts}`);
      connect();
    }, reconnectInterval);
  }, [connect, maxReconnectAttempts, reconnectInterval]);

  // Send a message to the agent
  const sendMessage = useCallback((message) => {
    if (!connectionRef.current || !isConnected) {
      console.error('Cannot send message: Not connected to WebSocket');
      return false;
    }

    connectionRef.current.sendMessage(message, agentId);
    return true;
  }, [agentId, isConnected]);

  // Subscribe to an agent
  const subscribeToAgent = useCallback((newAgentId) => {
    if (!connectionRef.current || !isConnected) {
      console.error('Cannot subscribe: Not connected to WebSocket');
      return false;
    }

    connectionRef.current.subscribeToAgent(newAgentId);
    return true;
  }, [isConnected]);

  // Close the connection
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    if (connectionRef.current) {
      connectionRef.current.close();
      connectionRef.current = null;
    }
  }, []);

  // Connect when the hook is first used
  useEffect(() => {
    connect();

    // Clean up on unmount
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  // Resubscribe when agentId changes
  useEffect(() => {
    if (isConnected && agentId) {
      subscribeToAgent(agentId);
    }
  }, [agentId, isConnected, subscribeToAgent]);

  return {
    isConnected,
    isConnecting,
    lastMessage,
    agentIsThinking,
    sendMessage,
    subscribeToAgent,
    connect,
    disconnect
  };
}

export default useWebSocket;
