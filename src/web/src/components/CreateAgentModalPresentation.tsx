/**
 * Presentation component for CreateAgentModal
 * This component is focused only on rendering the UI and delegating events to the container
 */

import React from 'react';
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
} from '@chakra-ui/react';
import { AgentFormData } from '../types/agent';

interface CreateAgentModalPresentationProps {
  isOpen: boolean;
  onClose: () => void;
  isLoading: boolean;
  formData: AgentFormData;
  handleChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => void;
  handleSubmit: (e: React.FormEvent) => Promise<void>;
}

const CreateAgentModalPresentation: React.FC<CreateAgentModalPresentationProps> = ({
  isOpen,
  onClose,
  isLoading,
  formData,
  handleChange,
  handleSubmit,
}) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <ModalOverlay />
      <ModalContent>
        <form onSubmit={handleSubmit}>
          <ModalHeader>Create New Agent</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={4}>
              <FormControl isRequired>
                <FormLabel>Agent ID</FormLabel>
                <Input
                  name="agent_id"
                  placeholder="assistant"
                  value={formData.agent_id}
                  onChange={handleChange}
                />
                <FormHelperText>A unique identifier for your agent</FormHelperText>
              </FormControl>

              <FormControl isRequired>
                <FormLabel>Language Model</FormLabel>
                <Select
                  name="model_name"
                  value={formData.model_name}
                  onChange={handleChange}
                >
                  <option value="gpt-4o">GPT-4o</option>
                  <option value="gpt-4-turbo">GPT-4 Turbo</option>
                  <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                  <option value="claude-3-opus">Claude 3 Opus</option>
                  <option value="claude-3-sonnet">Claude 3 Sonnet</option>
                </Select>
                <FormHelperText>The language model to use</FormHelperText>
              </FormControl>

              <FormControl isRequired>
                <FormLabel>System Message</FormLabel>
                <Textarea
                  name="system_message"
                  placeholder="You are a helpful assistant..."
                  value={formData.system_message}
                  onChange={handleChange}
                  rows={3}
                />
                <FormHelperText>Instructions for the agent's behavior</FormHelperText>
              </FormControl>

              <FormControl display="flex" alignItems="center">
                <FormLabel mb="0">Enable Web Search</FormLabel>
                <Switch
                  name="enable_web_search"
                  isChecked={formData.enable_web_search}
                  onChange={handleChange}
                />
              </FormControl>

              <FormControl display="flex" alignItems="center">
                <FormLabel mb="0">Enable Calculator</FormLabel>
                <Switch
                  name="enable_calculator"
                  isChecked={formData.enable_calculator}
                  onChange={handleChange}
                />
              </FormControl>

              <FormControl display="flex" alignItems="center">
                <FormLabel mb="0">Use Long-Term Memory</FormLabel>
                <Switch
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
              colorScheme="blue"
              type="submit"
              isLoading={isLoading}
              loadingText="Creating..."
            >
              Create Agent
            </Button>
          </ModalFooter>
        </form>
      </ModalContent>
    </Modal>
  );
};

export default CreateAgentModalPresentation;
