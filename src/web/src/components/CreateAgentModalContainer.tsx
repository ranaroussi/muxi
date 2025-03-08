/**
 * Container component for CreateAgentModal that handles logic and state
 */

import React, { useState } from 'react';
import { useToast } from '@chakra-ui/react';
import { createAgent } from '../services/api';
import { AgentFormData, CreateAgentModalProps } from '../types/agent';
import CreateAgentModalPresentation from './CreateAgentModalPresentation';

const DEFAULT_FORM_DATA: AgentFormData = {
  agent_id: '',
  model_name: 'gpt-4o',
  system_message: 'You are a friendly assistant',
  enable_web_search: true,
  enable_calculator: true,
  use_long_term_memory: false,
};

const CreateAgentModalContainer = ({
  isOpen,
  onClose,
  onAgentCreated
}: CreateAgentModalProps) => {
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState(DEFAULT_FORM_DATA);
  const [hasError, setHasError] = useState(false);
  const toast = useToast();

  const handleChange = (
    e: any
  ) => {
    const { name, value, type } = e.target;
    const checked = (e.target as HTMLInputElement).checked;

    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e: any) => {
    e.preventDefault();
    setIsLoading(true);
    setHasError(false);

    try {
      await createAgent(formData);

      toast({
        title: 'Agent created',
        description: `Agent "${formData.agent_id}" has been successfully created.`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });

      onAgentCreated();
      onClose();
      setFormData(DEFAULT_FORM_DATA);
    } catch (error) {
      setHasError(true);
      toast({
        title: 'Error creating agent',
        description: error instanceof Error ? error.message : 'An unknown error occurred',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Show a simple error UI if needed, but otherwise render the normal form
  if (hasError) {
    return (
      <div>
        <p>Something went wrong with the agent creation form.</p>
        <button onClick={() => setHasError(false)}>Try Again</button>
      </div>
    );
  }

  return (
    <CreateAgentModalPresentation
      isOpen={isOpen}
      onClose={onClose}
      isLoading={isLoading}
      formData={formData}
      handleChange={handleChange}
      handleSubmit={handleSubmit}
    />
  );
};

export default CreateAgentModalContainer;
