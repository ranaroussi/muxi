import React, { useState } from 'react';
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  Button,
  FormControl,
  FormLabel,
  Input,
  Textarea,
  Select,
  Switch,
  FormHelperText,
  VStack,
  useToast,
} from '@chakra-ui/react';
import { createAgent } from '../services/api';

function CreateAgentModal({ isOpen, onClose, onAgentCreated }) {
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    agent_id: '',
    model: 'gpt-4o',
    system_message: 'You are a friendly assistant',
    enable_web_search: true,
    enable_calculator: true,
    use_long_term_memory: false,
  });
  const toast = useToast();

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await createAgent(formData);

      toast({
        title: 'Agent created',
        description: `Agent "${formData.agent_id}" was created successfully.`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });

      // Reset form and close modal
      setFormData({
        agent_id: '',
        model: 'gpt-4o',
        system_message: 'You are a friendly assistant',
        enable_web_search: true,
        enable_calculator: true,
        use_long_term_memory: false,
      });

      // Notify parent component that an agent was created
      if (onAgentCreated) onAgentCreated();

      onClose();
    } catch (error) {
      toast({
        title: 'Error creating agent',
        description: String(error),
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <ModalOverlay />
      <ModalContent>
        <form onSubmit={handleSubmit}>
          <ModalHeader>Create New Agent</ModalHeader>
          <ModalCloseButton />

          <ModalBody>
            <VStack spacing={4} align="stretch">
              <FormControl isRequired>
                <FormLabel>Agent ID</FormLabel>
                <Input
                  name="agent_id"
                  value={formData.agent_id}
                  onChange={handleChange}
                  placeholder="Enter a unique identifier for the agent"
                />
                <FormHelperText>
                  This ID will be used to reference the agent in the API.
                </FormHelperText>
              </FormControl>

              <FormControl>
                <FormLabel>LLM Model</FormLabel>
                <Select
                  name="model"
                  value={formData.model}
                  onChange={handleChange}
                >
                  <option value="gpt-4o">GPT-4o</option>
                  <option value="gpt-4-turbo">GPT-4 Turbo</option>
                  <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                  <option value="claude-3-opus">Claude 3 Opus</option>
                  <option value="claude-3-sonnet">Claude 3 Sonnet</option>
                </Select>
                <FormHelperText>
                  Select the language model to power this agent.
                </FormHelperText>
              </FormControl>

              <FormControl>
                <FormLabel>System Message</FormLabel>
                <Textarea
                  name="system_message"
                  value={formData.system_message}
                  onChange={handleChange}
                  placeholder="Enter a system message to customize the agent's behavior"
                  rows={4}
                />
                <FormHelperText>
                  This message will guide the agent's behavior. Default is "You are a friendly assistant".
                </FormHelperText>
              </FormControl>

              <FormControl display="flex" alignItems="center">
                <FormLabel htmlFor="enable_web_search" mb="0">
                  Enable Web Search
                </FormLabel>
                <Switch
                  id="enable_web_search"
                  name="enable_web_search"
                  isChecked={formData.enable_web_search}
                  onChange={handleChange}
                />
              </FormControl>

              <FormControl display="flex" alignItems="center">
                <FormLabel htmlFor="enable_calculator" mb="0">
                  Enable Calculator
                </FormLabel>
                <Switch
                  id="enable_calculator"
                  name="enable_calculator"
                  isChecked={formData.enable_calculator}
                  onChange={handleChange}
                />
              </FormControl>

              <FormControl display="flex" alignItems="center">
                <FormLabel htmlFor="use_long_term_memory" mb="0">
                  Enable Long-Term Memory
                </FormLabel>
                <Switch
                  id="use_long_term_memory"
                  name="use_long_term_memory"
                  isChecked={formData.use_long_term_memory}
                  onChange={handleChange}
                />
              </FormControl>
            </VStack>
          </ModalBody>

          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              Cancel
            </Button>
            <Button
              type="submit"
              colorScheme="brand"
              isLoading={isLoading}
            >
              Create Agent
            </Button>
          </ModalFooter>
        </form>
      </ModalContent>
    </Modal>
  );
}

export default CreateAgentModal;
