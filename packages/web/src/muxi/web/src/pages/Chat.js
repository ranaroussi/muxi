import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Box,
  Flex,
  Input,
  Button,
  Text,
  VStack,
  HStack,
  IconButton,
  Avatar,
  Select,
  Heading,
  Divider,
  Spinner,
  Badge,
  useToast,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Collapse,
  Card,
  CardHeader,
  CardBody,
} from '@chakra-ui/react';
import { useParams, useNavigate } from 'react-router-dom';
import { FiSend, FiInfo, FiRefreshCw, FiAlertCircle, FiZap, FiAlertTriangle, FiList, FiCheckCircle } from 'react-icons/fi';
import { fetchAgents, createAgent } from '../services/api';

function Chat() {
  const { agentId } = useParams();
  const navigate = useNavigate();
  const [agents, setAgents] = useState([]);
  const [selectedAgentId, setSelectedAgentId] = useState(agentId || '');
  const [isLoadingAgents, setIsLoadingAgents] = useState(true);
  const [inputMessage, setInputMessage] = useState('');
  const [conversation, setConversation] = useState([]);
  const messagesEndRef = useRef(null);
  const toast = useToast();
  const [agentError, setAgentError] = useState(null);
  const [agentIsThinking, setAgentIsThinking] = useState(false);

  // Simple WebSocket implementation
  const [isConnected, setIsConnected] = useState(false);
  const [wsError, setWsError] = useState(null);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [debugEvents, setDebugEvents] = useState([]);
  const [showDebug, setShowDebug] = useState(false);
  const [isReconnecting, setIsReconnecting] = useState(false);

  // WebSocket ref
  const socketRef = useRef(null);

  // Function to add a debug event - kept for future debugging needs
  // eslint-disable-next-line no-unused-vars
  const addDebugEvent = useCallback((event) => {
    const timestamp = new Date().toLocaleTimeString();
    setDebugEvents(prev => [...prev, { time: timestamp, event }]);
    console.log(`[${timestamp}] ${event}`);
  }, []);

  // Handle socket onmessage
  const onSocketMessage = useCallback((event) => {
    try {
      const data = JSON.parse(event.data);
      console.log('WebSocket message received:', data);

      if (data.type === 'connected') {
        // Server sent a welcome message
        console.log('Connected with WebSocket ID:', data.connection_id);
      } else if (data.type === 'subscribed') {
        // Successfully subscribed to an agent
        setIsSubscribed(true);
        console.log('Successfully subscribed to agent:', data.agent_id);
        setAgentError(null); // Clear any agent errors
      } else if (data.type === 'error') {
        // Handle error message
        console.error('Error from server:', data.error || data.message);
        setAgentError(data.error || data.message);

        // If this is a subscription error, make sure we're marked as not subscribed
        if (data.message && data.message.includes('subscribing')) {
          setIsSubscribed(false);
        }

        setAgentIsThinking(false);
      } else if (data.type === 'response') {
        // Handle agent response
        console.log('Received agent response:', data);
        const newMessage = {
          id: data.id || `msg-${Date.now()}`,
          content: data.message,
          role: 'assistant',
          timestamp: new Date().toISOString(),
          agentId: data.agent_id,
          metadata: data.metadata || {}
        };

        setConversation(prev => [...prev, newMessage]);
        setAgentIsThinking(false);
      } else if (data.type === 'agent_thinking' || data.type === 'thinking') {
        // Agent is thinking
        setAgentIsThinking(true);
        console.log('Agent is thinking...');
      }
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  }, []);

  // Connect to WebSocket
  const connectWs = useCallback(() => {
    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const port = 5050; // API server port
      const wsUrl = `${protocol}//localhost:${port}/ws`;

      console.log(`Connecting to WebSocket at ${wsUrl}`);

      // Close existing connection if any
      if (socketRef.current && socketRef.current.readyState !== WebSocket.CLOSED) {
        console.log('Closing existing WebSocket connection');
        socketRef.current.close();
      }

      const socket = new WebSocket(wsUrl);
      socketRef.current = socket;

      socket.onopen = () => {
        console.log('WebSocket connection established');
        setIsConnected(true);
        setWsError(null);
      };

      socket.onmessage = onSocketMessage;

      socket.onclose = (event) => {
        console.log(`WebSocket connection closed: Code=${event.code}, Reason=${event.reason || 'None'}`);
        setIsConnected(false);
        setIsSubscribed(false);
      };

      socket.onerror = (error) => {
        console.error('WebSocket error occurred', error);
        setWsError('Connection error occurred');
      };

      return true;
    } catch (error) {
      console.error('Error creating WebSocket:', error);
      setWsError(`Failed to connect: ${error.message}`);
      return false;
    }
  }, [onSocketMessage]);

  // Subscribe to an agent
  const subscribeToAgent = useCallback((agentId) => {
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      console.log('Cannot subscribe: WebSocket not ready');
      return false;
    }

    if (!agentId) {
      console.log('Cannot subscribe: No agent ID provided');
      return false;
    }

    console.log(`Subscribing to agent: ${agentId}`);

    try {
      const subscribeMessage = {
        type: 'subscribe',
        agent_id: agentId
      };

      console.log('Sending subscription message:', subscribeMessage);
      socketRef.current.send(JSON.stringify(subscribeMessage));

      // Don't set isSubscribed here, wait for the confirmation from server
      return true;
    } catch (error) {
      console.error('Error subscribing to agent:', error);
      return false;
    }
  }, []);

  // Send a chat message
  const sendChatMessage = useCallback((message, agentId) => {
    console.log('Attempting to send message:', { message, agentId });

    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      console.log('Cannot send: WebSocket not open');
      return false;
    }

    if (!isSubscribed) {
      console.log('Cannot send: Not subscribed to agent');
      return false;
    }

    try {
      const messageData = {
        type: 'chat',
        message: message,
        agent_id: agentId
      };

      console.log('Sending message:', messageData);
      socketRef.current.send(JSON.stringify(messageData));
      return true;
    } catch (error) {
      console.error('Error sending message:', error);
      return false;
    }
  }, [isSubscribed]);

  // Handle manual reconnection
  const handleManualReconnect = useCallback(() => {
    setIsReconnecting(true);

    if (socketRef.current) {
      socketRef.current.close();
    }

    setTimeout(() => {
      connectWs();
      setIsReconnecting(false);
    }, 1000);
  }, [connectWs]);

  // Connect on component mount
  useEffect(() => {
    connectWs();

    // Cleanup on unmount
    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [connectWs]);

  // Subscribe when agent changes and connection is established
  useEffect(() => {
    if (isConnected && selectedAgentId) {
      subscribeToAgent(selectedAgentId);
    }
  }, [isConnected, selectedAgentId, subscribeToAgent]);

  // Load agents from API
  const loadAgents = useCallback(async () => {
    setIsLoadingAgents(true);
    try {
      const data = await fetchAgents();
      const agentsList = data.agents || [];
      setAgents(agentsList);

      // If no agent is selected yet, try to select test_agent or fall back to default agent or first one
      if (!selectedAgentId) {
        // Try to find test_agent first
        const testAgent = agentsList.find(a => a.agent_id === "test_agent");
        const defaultAgent = agentsList.find(a => a.is_default);
        const firstAgent = agentsList[0];
        const agentToSelect = testAgent?.agent_id || defaultAgent?.agent_id || firstAgent?.agent_id;

        if (agentToSelect) {
          console.log(`Selected agent: ${agentToSelect}`);
          setSelectedAgentId(agentToSelect);
          navigate(`/chat/${agentToSelect}`, { replace: true });
        }
      }
    } catch (error) {
      toast({
        title: 'Error fetching agents',
        description: String(error),
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoadingAgents(false);
    }
  }, [navigate, selectedAgentId, toast]);

  // Create a new agent if one doesn't exist
  const handleCreateAgent = useCallback(async () => {
    if (!selectedAgentId) return;

    try {
      // Create the agent
      await createAgent({
        agent_id: selectedAgentId,
        model: "gpt-4o",
        system_message: "You are a helpful AI assistant."
      });

      toast({
        title: 'Agent created',
        description: `Agent "${selectedAgentId}" has been created.`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      });

      // Refresh the agents list
      await loadAgents();

      // Reconnect to WebSocket and subscribe to the new agent
      if (isConnected) {
        subscribeToAgent(selectedAgentId);
      } else {
        connectWs();
      }
    } catch (error) {
      toast({
        title: 'Error creating agent',
        description: String(error),
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  }, [selectedAgentId, toast, loadAgents, connectWs, isConnected, subscribeToAgent]);

  // Handle sending a chat message
  const handleSendMessage = useCallback(() => {
    console.log('handleSendMessage called');

    if (!inputMessage.trim() || !selectedAgentId || !isConnected || !isSubscribed) {
      console.log('Message send prevented - conditions not met:', {
        hasMessage: !!inputMessage.trim(),
        hasAgentId: !!selectedAgentId,
        isConnected,
        isSubscribed
      });
      return;
    }

    const message = inputMessage.trim();
    setInputMessage('');

    // Add message to conversation immediately
    const userMessage = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
      agentId: selectedAgentId
    };

    console.log('Adding user message to conversation:', userMessage);
    setConversation(prev => [...prev, userMessage]);

    // Send the message
    console.log('About to send message via WebSocket');
    const success = sendChatMessage(message, selectedAgentId);

    console.log('Message send result:', success);
    if (!success) {
      toast({
        title: "Failed to send message",
        description: "Please check your connection and try again",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    } else {
      // Message sent successfully, show the agent is thinking
      setAgentIsThinking(true);
    }
  }, [inputMessage, selectedAgentId, isConnected, isSubscribed, sendChatMessage, toast]);

  // Fetch agents on initial mount
  useEffect(() => {
    loadAgents();
  }, [loadAgents]);

  // Scroll to bottom of chat
  useEffect(() => {
    scrollToBottom();
  }, [conversation]);

  // Scroll to bottom of chat
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Handle input keypress (Enter to send)
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Handle agent change
  const handleAgentChange = (e) => {
    setSelectedAgentId(e.target.value);
  };

  // Update the connection status display
  const renderConnectionStatus = () => {
    if (isConnected) {
      return (
        <div className="text-green-600 text-sm flex items-center space-x-1">
          <FiCheckCircle />
          <span>Connected</span>
        </div>
      );
    }

    if (wsError) {
      return (
        <div className="bg-red-50 p-4 rounded-md border border-red-200 mb-4">
          <div className="text-red-700 text-sm font-medium flex items-center">
            <FiAlertCircle className="mr-2" />
            <span>Connection Error</span>
          </div>
          <p className="text-sm text-red-600 mt-1">{wsError}</p>
          <button
            onClick={handleManualReconnect}
            disabled={isReconnecting}
            className="mt-2 px-3 py-1 bg-red-100 hover:bg-red-200 text-red-800 text-sm rounded-md transition-colors"
          >
            {isReconnecting ? 'Reconnecting...' : 'Reconnect'}
          </button>
        </div>
      );
    }

    return (
      <div className="bg-yellow-50 p-4 rounded-md border border-yellow-200 mb-4">
        <div className="text-amber-700 text-sm font-medium flex items-center">
          <FiAlertTriangle className="mr-2" />
          <span>Connecting...</span>
        </div>
        <button
          onClick={handleManualReconnect}
          disabled={isReconnecting}
          className="mt-2 px-3 py-1 bg-amber-100 hover:bg-amber-200 text-amber-800 text-sm rounded-md transition-colors"
        >
          {isReconnecting ? 'Reconnecting...' : 'Try Reconnecting'}
        </button>
      </div>
    );
  };

  return (
    <Box h="calc(100vh - 140px)">
      <Flex direction="column" h="100%">
        {/* Header with agent selector */}
        <Box mb={4}>
          <HStack justify="space-between" align="center" mb={2}>
            <Heading size="md">Chat</Heading>
            <HStack>
              <IconButton
                size="sm"
                variant="ghost"
                icon={<FiRefreshCw />}
                onClick={loadAgents}
                aria-label="Refresh agents"
              />
              <IconButton
                size="sm"
                variant="ghost"
                icon={<FiInfo />}
                as="a"
                href={selectedAgentId ? `/agents/${selectedAgentId}` : '/'}
                aria-label="Agent info"
              />
            </HStack>
          </HStack>
          <Select
            placeholder={isLoadingAgents ? "Loading agents..." : "Select an agent"}
            value={selectedAgentId}
            onChange={handleAgentChange}
            isDisabled={isLoadingAgents || agents.length === 0}
          >
            {agents.map(agent => (
              <option key={agent.agent_id} value={agent.agent_id}>
                {agent.agent_id} {agent.is_default ? '(Default)' : ''}
              </option>
            ))}
          </Select>

          {/* Connection status */}
          {renderConnectionStatus()}

          {/* Agent error display */}
          {agentError && (
            <Alert status="error" mb={4}>
              <AlertIcon />
              <Box flex="1">
                <AlertTitle>Agent Error</AlertTitle>
                <AlertDescription display="block">
                  {agentError}
                </AlertDescription>
                {agentError.includes('not exists') && (
                  <Button
                    mt={2}
                    colorScheme="blue"
                    size="sm"
                    onClick={handleCreateAgent}
                  >
                    Create Agent "{selectedAgentId}"
                  </Button>
                )}
              </Box>
            </Alert>
          )}

          {/* Empty state with create button */}
          {agents.length === 0 && !isLoadingAgents && (
            <Alert status="info" mb={4}>
              <AlertIcon />
              <Box flex="1">
                <AlertTitle>No Agents Found</AlertTitle>
                <AlertDescription display="block">
                  Create an agent to start chatting
                </AlertDescription>
                <Button
                  mt={2}
                  colorScheme="blue"
                  size="sm"
                  onClick={() => {
                    setSelectedAgentId("agent");
                    handleCreateAgent();
                  }}
                >
                  Create Default Agent
                </Button>
              </Box>
            </Alert>
          )}

          {/* Connection Debug Panel */}
          <Box mb={4}>
            <Button
              size="sm"
              onClick={() => setShowDebug(!showDebug)}
              leftIcon={showDebug ? <FiList /> : <FiAlertTriangle />}
              colorScheme={showDebug ? "blue" : "gray"}
            >
              {showDebug ? "Hide Debug Info" : "Show Debug Info"}
            </Button>

            <Collapse in={showDebug}>
              <Card mt={2}>
                <CardHeader pb={2}>
                  <Heading size="sm">WebSocket Debug</Heading>
                  <HStack spacing={2} mt={1}>
                    <Badge colorScheme={isConnected ? "green" : "red"}>
                      {isConnected ? "Connected" : "Disconnected"}
                    </Badge>
                    <Badge colorScheme={isSubscribed ? "green" : "yellow"}>
                      {isSubscribed ? "Subscribed" : "Not Subscribed"}
                    </Badge>
                  </HStack>
                </CardHeader>
                <CardBody pt={2}>
                  <VStack align="stretch" spacing={1}>
                    <HStack>
                      <Button size="xs" onClick={connectWs} leftIcon={<FiRefreshCw />}>
                        Connect
                      </Button>
                      <Button
                        size="xs"
                        onClick={() => {
                          if (socketRef.current) socketRef.current.close();
                        }}
                        leftIcon={<FiZap />}
                        isDisabled={!isConnected}
                      >
                        Disconnect
                      </Button>
                    </HStack>

                    <Divider my={2} />

                    <Text fontSize="xs" fontWeight="bold">Connection Details:</Text>
                    <Text fontSize="xs" color="blue.500">WebSocket URL: ws://localhost:5050/ws</Text>
                    {wsError && <Text fontSize="xs" color="red.500">Error: {wsError}</Text>}

                    <Divider my={2} />

                    <Text fontSize="xs" fontWeight="bold">Event Log:</Text>
                    <Box maxH="200px" overflowY="auto">
                      {debugEvents.map((event, idx) => (
                        <Text key={idx} fontSize="xs" color="gray.600">
                          [{event.time}] {event.event}
                        </Text>
                      ))}
                      {debugEvents.length === 0 && (
                        <Text fontSize="xs" color="gray.400">No events logged</Text>
                      )}
                    </Box>
                  </VStack>
                </CardBody>
              </Card>
            </Collapse>
          </Box>
        </Box>

        <Divider mb={4} />

        {/* Chat messages */}
        <Box
          flex="1"
          overflowY="auto"
          borderWidth="1px"
          borderRadius="md"
          p={4}
          bg="white"
          mb={4}
        >
          {conversation.length === 0 ? (
            <Flex
              direction="column"
              justify="center"
              align="center"
              h="100%"
              color="gray.500"
            >
              <Text mb={2}>No messages yet</Text>
              <Text fontSize="sm">Send a message to start the conversation</Text>
            </Flex>
          ) : (
            <VStack align="stretch" spacing={4}>
              {conversation.map((msg, index) => (
                <MessageBubble
                  key={msg.id || index}
                  message={msg}
                />
              ))}
              {agentIsThinking && (
                <Flex align="center">
                  <Avatar
                    size="sm"
                    bg="brand.500"
                    color="white"
                    name="AI"
                    mr={2}
                  />
                  <Spinner size="sm" mr={2} />
                  <Text fontSize="sm">Thinking...</Text>
                </Flex>
              )}
              <div ref={messagesEndRef} />
            </VStack>
          )}
        </Box>

        {/* Message input */}
        <HStack>
          <Input
            placeholder={
              !isConnected
                ? "Waiting for connection..."
                : agentError && agentError.includes('not found')
                  ? "Agent not found. Create it first."
                  : "Type your message here..."
            }
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={!isConnected || !selectedAgentId || (agentError && agentError.includes('not found'))}
          />
          <Button
            colorScheme="brand"
            onClick={handleSendMessage}
            isDisabled={!isConnected || !selectedAgentId || !inputMessage.trim() || (agentError && agentError.includes('not found'))}
            leftIcon={<FiSend />}
          >
            Send
          </Button>
        </HStack>
      </Flex>
    </Box>
  );
}

// Message bubble component
function MessageBubble({ message }) {
  const { role, content, tools = [] } = message;

  // Different styling based on message role
  const isUser = role === 'user';
  const isError = role === 'error';

  return (
    <Box>
      <HStack align="start" mb={1}>
        <Avatar
          size="sm"
          bg={isUser ? 'gray.500' : isError ? 'red.500' : 'brand.500'}
          color="white"
          name={isUser ? 'You' : isError ? 'Error' : 'AI'}
        />
        <Text fontWeight="bold" fontSize="sm">
          {isUser ? 'You' : isError ? 'Error' : 'Agent'}
        </Text>
      </HStack>
      <Box
        ml={10}
        p={3}
        borderRadius="md"
        bg={isUser ? 'blue.50' : isError ? 'red.50' : 'gray.50'}
        maxW="90%"
      >
        <Text whiteSpace="pre-wrap">{content}</Text>

        {tools && tools.length > 0 && (
          <Flex mt={2} wrap="wrap" gap={1}>
            {tools.map((tool, idx) => (
              <Badge key={idx} colorScheme="purple" fontSize="xs">
                {tool}
              </Badge>
            ))}
          </Flex>
        )}
      </Box>
    </Box>
  );
}

export default Chat;
