import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  Heading,
  Icon,
  Flex,
  Text,
  Divider,
  Button,
  useDisclosure
} from '@chakra-ui/react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  FiHome,
  FiMessageSquare,
  FiSettings,
  FiPlus,
  FiUser
} from 'react-icons/fi';
import CreateAgentModal from './CreateAgentModal';
import { fetchAgents } from '../services/api';

function Sidebar() {
  const [agents, setAgents] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const location = useLocation();
  const { isOpen, onOpen, onClose } = useDisclosure();

  // Fetch agents when component mounts
  useEffect(() => {
    loadAgents();
  }, []);

  const loadAgents = async () => {
    setIsLoading(true);
    try {
      const data = await fetchAgents();
      setAgents(data.agents || []);
    } catch (error) {
      console.error('Error loading agents:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Navigation items
  const navItems = [
    { name: 'Dashboard', path: '/', icon: FiHome },
    { name: 'Chat', path: '/chat', icon: FiMessageSquare },
    { name: 'Settings', path: '/settings', icon: FiSettings }
  ];

  return (
    <Box
      w="250px"
      h="100vh"
      bg="white"
      borderRightWidth="1px"
      overflowY="auto"
      py={4}
    >
      {/* Logo and title */}
      <Flex px={4} mb={6} align="center">
        <Heading size="md" fontWeight="600" color="brand.500">AI Agent</Heading>
      </Flex>

      {/* Navigation */}
      <VStack spacing={1} align="stretch" mb={6}>
        {navItems.map((item) => (
          <NavItem
            key={item.path}
            name={item.name}
            path={item.path}
            icon={item.icon}
            isActive={location.pathname === item.path}
          />
        ))}
      </VStack>

      <Divider mb={4} />

      {/* Agents section */}
      <Box px={4} mb={3}>
        <Flex justify="space-between" align="center">
          <Text fontWeight="600" fontSize="sm" color="gray.500">YOUR AGENTS</Text>
          <Button
            size="xs"
            colorScheme="brand"
            leftIcon={<FiPlus />}
            onClick={onOpen}
          >
            New
          </Button>
        </Flex>
      </Box>

      {/* Agents list */}
      <VStack spacing={1} align="stretch">
        {isLoading ? (
          <Box px={4}><Text fontSize="sm">Loading...</Text></Box>
        ) : agents.length === 0 ? (
          <Box px={4}><Text fontSize="sm">No agents found</Text></Box>
        ) : (
          agents.map((agent) => (
            <NavItem
              key={agent.agent_id}
              name={agent.agent_id}
              path={`/agents/${agent.agent_id}`}
              icon={FiUser}
              isActive={location.pathname === `/agents/${agent.agent_id}`}
              secondaryText={agent.is_default ? 'Default' : null}
              colorScheme={agent.is_default ? 'green' : 'gray'}
            />
          ))
        )}
      </VStack>

      {/* Create agent modal */}
      <CreateAgentModal
        isOpen={isOpen}
        onClose={onClose}
        onAgentCreated={loadAgents}
      />
    </Box>
  );
}

// Individual navigation item component
function NavItem({ name, path, icon, isActive, secondaryText, colorScheme = 'brand' }) {
  return (
    <Box
      as={NavLink}
      to={path}
      bg={isActive ? `${colorScheme}.50` : 'transparent'}
      color={isActive ? `${colorScheme}.600` : 'gray.700'}
      px={4}
      py={2}
      _hover={{ bg: `${colorScheme}.50`, textDecoration: 'none' }}
      borderLeftWidth={isActive ? "3px" : "0"}
      borderLeftColor={`${colorScheme}.500`}
    >
      <Flex align="center">
        <Icon as={icon} mr={3} />
        <Text>{name}</Text>
        {secondaryText && (
          <Text
            fontSize="xs"
            ml={2}
            px={1.5}
            py={0.5}
            borderRadius="full"
            bg={`${colorScheme}.100`}
            color={`${colorScheme}.700`}
          >
            {secondaryText}
          </Text>
        )}
      </Flex>
    </Box>
  );
}

export default Sidebar;
