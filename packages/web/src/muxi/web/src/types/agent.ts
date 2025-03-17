/**
 * Types for agent-related components and data
 */

export interface AgentFormData {
  agent_id: string;
  model_name: string;
  system_message: string;
  enable_web_search: boolean;
  enable_calculator: boolean;
  use_long_term_memory: boolean;
}

export interface CreateAgentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAgentCreated: () => void;
}
