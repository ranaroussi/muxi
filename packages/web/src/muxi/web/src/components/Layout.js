import React, { useEffect, useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Box, Flex, Text } from '@chakra-ui/react';
import Sidebar from './Sidebar';
import Header from './Header';
import { fetchVersion } from '../services/api';

function Layout() {
  const [version, setVersion] = useState('');

  useEffect(() => {
    const getVersion = async () => {
      try {
        const versionData = await fetchVersion();
        setVersion(versionData.version);
      } catch (error) {
        console.error('Failed to fetch version:', error);
      }
    };

    getVersion();
  }, []);

  return (
    <Flex h="100vh" overflow="hidden" direction="column">
      <Flex flex="1" overflow="hidden">
        {/* Sidebar */}
        <Sidebar />

        {/* Main content area */}
        <Flex direction="column" flex="1" overflow="hidden">
          <Header />
          <Box
            flex="1"
            p={4}
            overflowY="auto"
            bg="gray.50"
          >
            <Outlet />
          </Box>
        </Flex>
      </Flex>

      {/* Footer */}
      <Box
        py={2}
        px={4}
        bg="gray.100"
        borderTop="1px"
        borderColor="gray.200"
        textAlign="right"
      >
        <Text fontSize="sm" color="gray.500">
          MUXI Framework {version && `v${version}`}
        </Text>
      </Box>
    </Flex>
  );
}

export default Layout;
