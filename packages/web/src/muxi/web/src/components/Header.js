import React from 'react';
import { Box, Flex, Heading, Button, IconButton, useColorMode, HStack, Text } from '@chakra-ui/react';
import { FiMoon, FiSun, FiRefreshCw } from 'react-icons/fi';
import { useLocation } from 'react-router-dom';

function Header() {
  const { colorMode, toggleColorMode } = useColorMode();
  const location = useLocation();

  // Determine title based on current route
  const getTitle = () => {
    const path = location.pathname;
    if (path === '/') return 'Dashboard';
    if (path.startsWith('/agents/')) return 'Agent Details';
    if (path.startsWith('/chat')) return 'Chat';
    if (path === '/settings') return 'Settings';
    return 'MUXI Framework';
  };

  return (
    <Box
      as="header"
      borderBottomWidth="1px"
      bg="white"
      py={3}
      px={6}
      boxShadow="sm"
    >
      <Flex justify="space-between" align="center">
        <Heading as="h1" size="md" fontWeight="600">{getTitle()}</Heading>
        <HStack spacing={3}>
          <Button
            size="sm"
            variant="outline"
            leftIcon={<FiRefreshCw />}
            onClick={() => window.location.reload()}
          >
            Refresh
          </Button>
          <IconButton
            size="sm"
            variant="ghost"
            aria-label={`Switch to ${colorMode === 'light' ? 'dark' : 'light'} mode`}
            icon={colorMode === 'light' ? <FiMoon /> : <FiSun />}
            onClick={toggleColorMode}
          />
          <Text fontSize="sm" color="gray.500">v0.1.0</Text>
        </HStack>
      </Flex>
    </Box>
  );
}

export default Header;
