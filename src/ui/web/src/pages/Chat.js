import React, { useState, useEffect, useRef } from 'react';
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
  useToast
} from '@chakra-ui/react';
import { useParams, useNavigate } from 'react-router-dom';
import { FiSend, FiInfo, FiRefreshCw } from 'react-icons/fi';
import { fetchAgents } from '../services/api';
import useWebSocket from '../hooks/useWebSocket';

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

  // WebSocket connection
  const {
    isConnected,
    isConnecting,
    agentIsThinking,
    sendMessage,
    subscribeToAgent
  } = useWebSocket({
    agentId: selectedAgentId,
    onMessage: handleWebSocketMessage,
  });

  // Handle incoming WebSocket messages
  function handleWebSocketMessage(data) {
    if (data.type === 'response') {
      // Add agent message to conversation
      setConversation(prev => [
        ...prev,
        {
          role: 'agent',
          content: data.message,
          toolsUsed: data.tools_used || []
        }
      ]);
    } else if (data.type === 'error') {
      // Add error message to conversation
      setConversation(prev => [
        ...prev,
        {
          role: 'error',
          content: data.message
        }
      ]);

      // Show toast notification
      toast({
        title: 'Error',
        description: data.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  }

  // Fetch agents on mount
  useEffect(() => {
    loadAgents();
  }, []);

  // Scroll to bottom of chat when conversation updates
  useEffect(() => {
    scrollToBottom();
  }, [conversation]);

  // Change agent when selectedAgentId changes
  useEffect(() => {
    if (selectedAgentId && isConnected) {
      subscribeToAgent(selectedAgentId);
      // Update URL
      navigate(`/chat/${selectedAgentId}`, { replace: true });
      // Clear conversation
      setConversation([]);
    }
  }, [selectedAgentId, isConnected, subscribeToAgent, navigate]);

  // Load agents from API
  const loadAgents = async () => {
    setIsLoadingAgents(true);
    try {
      const data = await fetchAgents();
      const agentsList = data.agents || [];
      setAgents(agentsList);

      // If no agent is selected yet, select the default agent or the first one
      if (!selectedAgentId) {
        const defaultAgent = agentsList.find(a => a.is_default);
        const firstAgent = agentsList[0];
        const agentToSelect = defaultAgent?.agent_id || firstAgent?.agent_id;

        if (agentToSelect) {
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
  };

  // Scroll to bottom of chat
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Handle sending a message
  const handleSendMessage = () => {
    if (!inputMessage.trim()) return;
    if (!selectedAgentId) {
      toast({
        title: 'No agent selected',
        description: 'Please select an agent to chat with',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    // Add user message to conversation
    setConversation(prev => [
      ...prev,
      { role: 'user', content: inputMessage }
    ]);

    // Send message via WebSocket
    sendMessage(inputMessage);

    // Clear input
    setInputMessage('');
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
              />
              <IconButton
                size="sm"
                variant="ghost"
                icon={<FiInfo />}
                as="a"
                href={selectedAgentId ? `/agents/${selectedAgentId}` : '/'}
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
          {!isConnected && (
            <Text color="red.500" fontSize="sm" mt={1}>
              Not connected to WebSocket. {isConnecting ? 'Connecting...' : 'Reconnecting...'}
            </Text>
          )}
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
                <MessageBubble key={index} message={msg} />
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
            placeholder="Type your message here..."
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={!isConnected || !selectedAgentId}
          />
          <Button
            colorScheme="brand"
            onClick={handleSendMessage}
            isDisabled={!isConnected || !selectedAgentId || !inputMessage.trim()}
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
  const { role, content, toolsUsed } = message;

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
          name={isUser ? 'User' : isError ? 'Error' : 'AI'}
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

        {toolsUsed && toolsUsed.length > 0 && (
          <Flex mt={2} wrap="wrap" gap={1}>
            {toolsUsed.map((tool, idx) => (
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
