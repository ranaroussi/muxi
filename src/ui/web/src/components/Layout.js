import React from 'react';
import { Outlet } from 'react-router-dom';
import { Box, Flex } from '@chakra-ui/react';
import Sidebar from './Sidebar';
import Header from './Header';

function Layout() {
  return (
    <Flex h="100vh" overflow="hidden">
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
  );
}

export default Layout;
