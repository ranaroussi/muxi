import React, { useState, useEffect } from 'react';
import {
  Box,
  Flex,
  Heading,
  Text,
  Button,
  HStack,
  VStack,
  Badge,
  Divider,
  Card,
  CardHeader,
  CardBody,
  Spinner,
  Input,
  InputGroup,
  InputRightElement,
  IconButton,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  SimpleGrid,
  useToast,
  useDisclosure,
  AlertDialog,
  AlertDialogBody,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogContent,
  AlertDialogOverlay,
} from '@chakra-ui/react';
import { useParams, useNavigate } from 'react-router-dom';
import { FiSearch, FiMessageSquare, FiTrash2 } from 'react-icons/fi';
import { fetchAgents, deleteAgent, searchMemory } from '../services/api';

function AgentDetails() {
  const { agentId } = useParams();
  const navigate = useNavigate();
  const toast = useToast();
  const [agent, setAgent] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [memories, setMemories] = useState([]);
  const [isSearchingMemory, setIsSearchingMemory] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const { isOpen, onOpen, onClose } = useDisclosure();
  const cancelRef = React.useRef();

  // Fetch agent data
  useEffect(() => {
    if (agentId) {
      loadAgentData();
    }
  }, [agentId]);

  const loadAgentData = async () => {
    setIsLoading(true);
    try {
      // Fetch all agents and find the one matching agentId
      const data = await fetchAgents();
      const agentsList = data.agents || [];
      const foundAgent = agentsList.find(a => a.agent_id === agentId);

      if (foundAgent) {
        setAgent(foundAgent);
      } else {
        toast({
          title: 'Agent not found',
          description: `Agent with ID "${agentId}" was not found.`,
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
        navigate('/');
      }
    } catch (error) {
      toast({
        title: 'Error fetching agent',
        description: String(error),
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Search agent memory
  const handleSearchMemory = async () => {
    if (!searchQuery.trim()) return;

    setIsSearchingMemory(true);
    setMemories([]);

    try {
      const results = await searchMemory(searchQuery, agentId);
      setMemories(results.results || []);

      if ((results.results || []).length === 0) {
        toast({
          title: 'No memories found',
          description: 'No matching memories found for your query.',
          status: 'info',
          duration: 3000,
          isClosable: true,
        });
      }
    } catch (error) {
      toast({
        title: 'Error searching memory',
        description: String(error),
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsSearchingMemory(false);
    }
  };

  // Handle memory search input key press
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearchMemory();
    }
  };

  // Handle agent deletion
  const handleDeleteAgent = async () => {
    try {
      await deleteAgent(agentId);

      toast({
        title: 'Agent deleted',
        description: `Agent "${agentId}" was successfully deleted.`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });

      navigate('/');
    } catch (error) {
      toast({
        title: 'Error deleting agent',
        description: String(error),
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      onClose();
    }
  };

  if (isLoading) {
    return (
      <Flex justify="center" align="center" h="200px">
        <Spinner size="xl" color="brand.500" />
      </Flex>
    );
  }

  if (!agent) {
    return (
      <Box textAlign="center" py={10}>
        <Heading size="md">Agent not found</Heading>
        <Text mt={4}>The agent you're looking for does not exist.</Text>
        <Button
          mt={6}
          colorScheme="brand"
          onClick={() => navigate('/')}
        >
          Return to Dashboard
        </Button>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Flex justify="space-between" align="center" mb={6}>
        <Box>
          <Heading size="lg">{agent.agent_id}</Heading>
          <HStack mt={1}>
            {agent.is_default && (
              <Badge colorScheme="green">Default</Badge>
            )}
          </HStack>
        </Box>
        <HStack>
          <Button
            leftIcon={<FiMessageSquare />}
            colorScheme="brand"
            variant="outline"
            onClick={() => navigate(`/chat/${agentId}`)}
          >
            Chat
          </Button>
          <Button
            leftIcon={<FiTrash2 />}
            colorScheme="red"
            variant="ghost"
            onClick={onOpen}
          >
            Delete
          </Button>
        </HStack>
      </Flex>

      {/* Agent stats */}
      <SimpleGrid columns={{ base: 1, md: 3 }} spacing={5} mb={8}>
        <StatCard
          title="Tools"
          value={agent.tools.length}
          description="Active tools"
        />
        <StatCard
          title="Type"
          value={agent.is_default ? 'Default' : 'Secondary'}
          description="Agent type"
        />
        {/* You can add more stats here as your API provides them */}
      </SimpleGrid>

      <Divider my={6} />

      {/* Memory search */}
      <Box mb={8}>
        <Heading size="md" mb={4}>Memory Search</Heading>
        <InputGroup size="md" mb={4}>
          <Input
            placeholder="Search agent's memory..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={handleKeyPress}
          />
          <InputRightElement width="4.5rem">
            <IconButton
              h="1.75rem"
              size="sm"
              icon={isSearchingMemory ? <Spinner size="sm" /> : <FiSearch />}
              onClick={handleSearchMemory}
              isDisabled={isSearchingMemory || !searchQuery.trim()}
              aria-label="Search memories"
            />
          </InputRightElement>
        </InputGroup>

        {/* Memory results */}
        {memories.length > 0 && (
          <VStack spacing={3} align="stretch">
            {memories.map((memory, index) => (
              <Card key={index} variant="outline">
                <CardHeader py={2} px={4} bg="gray.50">
                  <Flex justify="space-between" align="center">
                    <Text fontSize="sm" fontWeight="bold">
                      Memory from {memory.source}
                    </Text>
                    <Badge colorScheme="blue">
                      Score: {Math.round((1 - memory.distance) * 100)}%
                    </Badge>
                  </Flex>
                </CardHeader>
                <CardBody py={3} px={4}>
                  <Text fontSize="sm">{memory.text}</Text>
                </CardBody>
              </Card>
            ))}
          </VStack>
        )}
      </Box>

      {/* Tools section */}
      <Box mb={6}>
        <Heading size="md" mb={4}>Available Tools</Heading>
        {agent.tools.length === 0 ? (
          <Text>No tools enabled for this agent.</Text>
        ) : (
          <VStack align="stretch" spacing={2}>
            {agent.tools.map((tool, index) => (
              <HStack key={index} p={3} borderWidth="1px" borderRadius="md">
                <Badge colorScheme="purple" fontSize="sm">{tool}</Badge>
                <Text fontSize="sm" flex="1">Tool for {tool.toLowerCase()} operations</Text>
              </HStack>
            ))}
          </VStack>
        )}
      </Box>

      {/* Delete agent confirmation dialog */}
      <AlertDialog
        isOpen={isOpen}
        leastDestructiveRef={cancelRef}
        onClose={onClose}
      >
        <AlertDialogOverlay>
          <AlertDialogContent>
            <AlertDialogHeader fontSize="lg" fontWeight="bold">
              Delete Agent
            </AlertDialogHeader>

            <AlertDialogBody>
              Are you sure you want to delete agent "{agentId}"? This action cannot be undone.
              {agent.is_default && (
                <Text color="red.500" mt={2}>
                  Warning: This is your default agent.
                </Text>
              )}
            </AlertDialogBody>

            <AlertDialogFooter>
              <Button ref={cancelRef} onClick={onClose}>
                Cancel
              </Button>
              <Button colorScheme="red" onClick={handleDeleteAgent} ml={3}>
                Delete
              </Button>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialogOverlay>
      </AlertDialog>
    </Box>
  );
}

// Stat card component
function StatCard({ title, value, description }) {
  return (
    <Box
      borderWidth="1px"
      borderRadius="lg"
      p={5}
      bg="white"
      shadow="sm"
    >
      <Stat>
        <StatLabel fontSize="lg" fontWeight="500">{title}</StatLabel>
        <StatNumber fontSize="2xl" fontWeight="600" mt={2}>
          {value}
        </StatNumber>
        <StatHelpText>{description}</StatHelpText>
      </Stat>
    </Box>
  );
}

export default AgentDetails;
