import React from 'react';
import { Box, Heading, Text, Button, Flex, Icon } from '@chakra-ui/react';
import { FiAlertTriangle, FiHome } from 'react-icons/fi';
import { Link } from 'react-router-dom';

function NotFound() {
  return (
    <Flex
      direction="column"
      align="center"
      justify="center"
      h="70vh"
      textAlign="center"
    >
      <Icon as={FiAlertTriangle} boxSize={16} color="orange.500" mb={4} />
      <Heading size="xl" mb={2}>Page Not Found</Heading>
      <Text fontSize="lg" color="gray.600" mb={8}>
        The page you're looking for doesn't exist or has been moved.
      </Text>
      <Button
        as={Link}
        to="/"
        leftIcon={<FiHome />}
        colorScheme="brand"
        size="lg"
      >
        Back to Dashboard
      </Button>
    </Flex>
  );
}

export default NotFound;
