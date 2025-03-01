import React, { useState } from 'react';
import {
  Box,
  Heading,
  Text,
  FormControl,
  FormLabel,
  Input,
  Button,
  VStack,
  HStack,
  Switch,
  Divider,
  Badge,
  useToast,
  Card,
  CardHeader,
  CardBody,
} from '@chakra-ui/react';

function Settings() {
  const toast = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [settings, setSettings] = useState({
    apiUrl: process.env.BACKEND_API_URL || window.location.origin,
    enableNotifications: true,
    enableAutoReconnect: true,
    darkMode: false,
    debugMode: false,
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setSettings(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSave = () => {
    setIsLoading(true);

    // Simulate saving settings
    setTimeout(() => {
      setIsLoading(false);

      // Show success toast
      toast({
        title: 'Settings saved',
        description: 'Your settings have been saved successfully.',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });

      // In a real app, you would save these to local storage or a backend API
      localStorage.setItem('settings', JSON.stringify(settings));
    }, 1000);
  };

  return (
    <Box>
      <Heading size="lg" mb={6}>Settings</Heading>

      <Card mb={6} variant="outline">
        <CardHeader pb={2}>
          <Heading size="md">Connection Settings</Heading>
        </CardHeader>
        <CardBody>
          <VStack spacing={4} align="stretch">
            <FormControl>
              <FormLabel>API URL</FormLabel>
              <Input
                name="apiUrl"
                value={settings.apiUrl}
                onChange={handleChange}
                placeholder="Enter API URL"
              />
              <Text fontSize="sm" color="gray.500" mt={1}>
                URL of the AI Agent Framework API server
              </Text>
            </FormControl>

            <HStack justify="space-between">
              <FormControl display="flex" alignItems="center">
                <FormLabel htmlFor="enableAutoReconnect" mb="0">
                  Auto Reconnect
                </FormLabel>
                <Switch
                  id="enableAutoReconnect"
                  name="enableAutoReconnect"
                  isChecked={settings.enableAutoReconnect}
                  onChange={handleChange}
                />
              </FormControl>

              <Badge colorScheme="green">Connected</Badge>
            </HStack>
          </VStack>
        </CardBody>
      </Card>

      <Card mb={6} variant="outline">
        <CardHeader pb={2}>
          <Heading size="md">UI Settings</Heading>
        </CardHeader>
        <CardBody>
          <VStack spacing={4} align="stretch">
            <FormControl display="flex" alignItems="center">
              <FormLabel htmlFor="enableNotifications" mb="0">
                Enable Notifications
              </FormLabel>
              <Switch
                id="enableNotifications"
                name="enableNotifications"
                isChecked={settings.enableNotifications}
                onChange={handleChange}
              />
            </FormControl>

            <FormControl display="flex" alignItems="center">
              <FormLabel htmlFor="darkMode" mb="0">
                Dark Mode <Badge ml={2} colorScheme="purple">Coming Soon</Badge>
              </FormLabel>
              <Switch
                id="darkMode"
                name="darkMode"
                isChecked={settings.darkMode}
                onChange={handleChange}
                isDisabled
              />
            </FormControl>
          </VStack>
        </CardBody>
      </Card>

      <Card mb={6} variant="outline">
        <CardHeader pb={2}>
          <Heading size="md">Developer Settings</Heading>
        </CardHeader>
        <CardBody>
          <VStack spacing={4} align="stretch">
            <FormControl display="flex" alignItems="center">
              <FormLabel htmlFor="debugMode" mb="0">
                Debug Mode
              </FormLabel>
              <Switch
                id="debugMode"
                name="debugMode"
                isChecked={settings.debugMode}
                onChange={handleChange}
              />
            </FormControl>

            <Text fontSize="sm" color="gray.500">
              Debug mode enables additional logging and development features.
            </Text>
          </VStack>
        </CardBody>
      </Card>

      <Divider my={6} />

      <Box textAlign="right">
        <Button
          colorScheme="brand"
          onClick={handleSave}
          isLoading={isLoading}
        >
          Save Settings
        </Button>
      </Box>

      <Box mt={8} p={4} borderRadius="md" bg="gray.50">
        <Heading size="sm" mb={2}>About</Heading>
        <Text fontSize="sm">AI Agent Framework Dashboard v0.1.0</Text>
        <Text fontSize="sm" color="gray.500">
          © 2023 AI Agent Framework
        </Text>
      </Box>
    </Box>
  );
}

export default Settings;
