import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Heading,
  Text,
  Flex,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  SimpleGrid,
  Button,
  useDisclosure,
  useToast,
  Spinner,
  Badge,
  Card,
  CardHeader,
  CardBody,
  CardFooter,
  Divider,
  HStack
} from '@chakra-ui/react';
import { FiPlus, FiMessageSquare, FiInfo, FiTool, FiUsers } from 'react-icons/fi';
import { Link } from 'react-router-dom';
import { fetchAgents, fetchTools } from '../services/api';
import CreateAgentModal from '../components/CreateAgentModal';

function Dashboard() {
  const [agents, setAgents] = useState([]);
  const [tools, setTools] = useState([]);
  const [isLoadingAgents, setIsLoadingAgents] = useState(true);
  const [isLoadingTools, setIsLoadingTools] = useState(true);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();

  // Fetch data on mount
  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    // Fetch agents
    setIsLoadingAgents(true);
    try {
      const agentData = await fetchAgents();
      setAgents(agentData.agents || []);
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

    // Fetch tools
    setIsLoadingTools(true);
    try {
      const toolData = await fetchTools();
      setTools(toolData.tools || []);
    } catch (error) {
      toast({
        title: 'Error fetching tools',
        description: String(error),
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoadingTools(false);
    }
  };

  return (
    <Box>
      <Flex justify="space-between" align="center" mb={6}>
        <Heading size="lg">Dashboard</Heading>
        <Button
          leftIcon={<FiPlus />}
          colorScheme="brand"
          onClick={onOpen}
        >
          New Agent
        </Button>
      </Flex>

      {/* Stats overview */}
      <SimpleGrid columns={{ base: 1, md: 3 }} spacing={5} mb={8}>
        <StatCard
          title="Agents"
          value={agents.length}
          description="Active AI agents"
          icon={FiUsers}
          isLoading={isLoadingAgents}
        />
        <StatCard
          title="Tools"
          value={tools.length}
          description="Available tools"
          icon={FiTool}
          isLoading={isLoadingTools}
        />
        <StatCard
          title="Default Agent"
          value={agents.find(a => a.is_default)?.agent_id || 'None'}
          description="Primary agent for API requests"
          icon={FiInfo}
          isLoading={isLoadingAgents}
        />
      </SimpleGrid>

      {/* Agents list */}
      <Box mb={8}>
        <Heading size="md" mb={4}>Your Agents</Heading>
        {isLoadingAgents ? (
          <Flex justify="center" py={8}>
            <Spinner size="lg" color="brand.500" />
          </Flex>
        ) : agents.length === 0 ? (
          <Box
            borderWidth="1px"
            borderRadius="lg"
            p={6}
            textAlign="center"
          >
            <Text mb={4}>No agents created yet.</Text>
            <Button
              leftIcon={<FiPlus />}
              colorScheme="brand"
              onClick={onOpen}
            >
              Create Your First Agent
            </Button>
          </Box>
        ) : (
          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={5}>
            {agents.map((agent) => (
              <AgentCard key={agent.agent_id} agent={agent} />
            ))}
          </SimpleGrid>
        )}
      </Box>

      {/* Create agent modal */}
      <CreateAgentModal
        isOpen={isOpen}
        onClose={onClose}
        onAgentCreated={fetchData}
      />
    </Box>
  );
}

// Stat card component
function StatCard({ title, value, description, icon, isLoading = false }) {
  return (
    <Box
      borderWidth="1px"
      borderRadius="lg"
      p={5}
      bg="white"
      shadow="sm"
    >
      <Stat>
        <Flex justify="space-between" align="center">
          <StatLabel fontSize="lg" fontWeight="500">{title}</StatLabel>
          <Box
            borderRadius="full"
            bg="brand.50"
            color="brand.500"
            p={2}
          >
            <Box as={icon} size="20px" />
          </Box>
        </Flex>
        {isLoading ? (
          <Spinner size="sm" mt={2} />
        ) : (
          <StatNumber fontSize="2xl" fontWeight="600" mt={2}>
            {value}
          </StatNumber>
        )}
        <StatHelpText>{description}</StatHelpText>
      </Stat>
    </Box>
  );
}

// Agent card component
function AgentCard({ agent }) {
  return (
    <Card borderRadius="lg" shadow="sm" overflow="hidden">
      <CardHeader bg="gray.50" py={3} px={4}>
        <Flex justify="space-between" align="center">
          <Heading size="sm">{agent.agent_id}</Heading>
          {agent.is_default && (
            <Badge colorScheme="green">Default</Badge>
          )}
        </Flex>
      </CardHeader>
      <CardBody p={4}>
        <Text color="gray.600" fontSize="sm" mb={3}>
          Tools: {agent.tools.length ? agent.tools.join(', ') : 'None'}
        </Text>
      </CardBody>
      <Divider />
      <CardFooter p={3}>
        <HStack spacing={2} width="100%">
          <Button
            as={Link}
            to={`/chat/${agent.agent_id}`}
            size="sm"
            leftIcon={<FiMessageSquare />}
            colorScheme="brand"
            variant="ghost"
            flex="1"
          >
            Chat
          </Button>
          <Button
            as={Link}
            to={`/agents/${agent.agent_id}`}
            size="sm"
            leftIcon={<FiInfo />}
            variant="outline"
            flex="1"
          >
            Details
          </Button>
        </HStack>
      </CardFooter>
    </Card>
  );
}

export default Dashboard;
