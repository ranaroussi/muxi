"""
MemoryExtractor: Automatic user information extraction for MUXI Framework.

This module provides the MemoryExtractor class that analyzes conversations
to automatically extract important user information and store it in context memory.
"""

import json
import time
from typing import Set, Any


class MemoryExtractor:
    """
    A class for automatically extracting user information from conversations
    and storing it in context memory.

    The MemoryExtractor analyzes conversation history, identifies key facts
    about users, scores their importance and confidence, and updates the
    user's context memory.
    """

    def __init__(
        self,
        orchestrator,
        extraction_model=None,
        confidence_threshold=0.7,
        auto_extract=True,
        extraction_interval=1,  # Process every n messages
        max_history_tokens=1000,
        opt_out_users: Set[int] = None,
        whitelist_users: Set[int] = None,
        blacklist_users: Set[int] = None,
        retention_days: int = 365,  # Default to 1 year retention
    ):
        """
        Initialize the MemoryExtractor.

        Args:
            orchestrator: The MUXI orchestrator that manages memory
            extraction_model: Model for extraction (may differ from agent model)
            confidence_threshold: Minimum confidence level (0.0-1.0) to store info
            auto_extract: Whether to automatically extract after conversations
            extraction_interval: Process every n messages (1=every message)
            max_history_tokens: Maximum token count for conversation history
            opt_out_users: Set of user IDs that have opted out of extraction
            whitelist_users: If set, only these users will have extraction
            blacklist_users: These users will be excluded from extraction
            retention_days: Number of days to retain extracted information
        """
        self.orchestrator = orchestrator
        self.extraction_model = extraction_model
        self.confidence_threshold = confidence_threshold
        self.auto_extract = auto_extract
        self.extraction_interval = extraction_interval
        self.max_history_tokens = max_history_tokens
        self.opt_out_users = opt_out_users or set()
        self.whitelist_users = whitelist_users
        self.blacklist_users = blacklist_users or set()
        self.retention_days = retention_days

        # Add default privacy settings
        self._sensitive_key_patterns = {
            "password", "social_security", "ssn", "credit_card", "bank_account",
            "passport", "license", "secret", "private", "confidential"
        }

    async def process_conversation_turn(
        self,
        user_message,
        agent_response,
        user_id,
        message_count=1
    ):
        """
        Process a conversation turn and extract information if needed.

        Args:
            user_message: The message from the user
            agent_response: The response from the agent
            user_id: The user's ID
            message_count: Current message count for this user
        """
        if not self.auto_extract:
            return

        # Skip extraction for anonymous users (user_id=0)
        if user_id == 0:
            return

        # Skip extraction for users who have opted out
        if user_id in self.opt_out_users:
            return

        # Skip extraction for blacklisted users
        if self.blacklist_users and user_id in self.blacklist_users:
            return

        # Skip extraction for users not in whitelist (if whitelist is enabled)
        if self.whitelist_users is not None and user_id not in self.whitelist_users:
            return

        # Only process every n messages based on extraction_interval
        if message_count % self.extraction_interval != 0:
            return

        # Create conversation context from this turn
        conversation = f"User: {user_message}\nAssistant: {agent_response}"

        # Extract information
        extraction_results = await self._extract_user_information(conversation)

        # Process and store results if confidence threshold is met
        await self._process_extraction_results(extraction_results, user_id)

    def opt_out_user(self, user_id: int) -> bool:
        """
        Add a user to the opt-out list, preventing future extraction.

        Args:
            user_id: The user ID to opt out

        Returns:
            True if successful, False if already opted out
        """
        if user_id in self.opt_out_users:
            return False

        self.opt_out_users.add(user_id)
        return True

    def opt_in_user(self, user_id: int) -> bool:
        """
        Remove a user from the opt-out list, enabling future extraction.

        Args:
            user_id: The user ID to opt in

        Returns:
            True if successful, False if already opted in
        """
        if user_id not in self.opt_out_users:
            return False

        self.opt_out_users.remove(user_id)
        return True

    async def purge_user_data(self, user_id: int) -> bool:
        """
        Purge all automatically extracted data for a user.

        Args:
            user_id: The user ID to purge data for

        Returns:
            True if successful, False otherwise
        """
        # Skip for anonymous users
        if user_id == 0:
            return True

        # Get existing context to find auto-extracted entries
        context = await self.orchestrator.get_user_context_memory(user_id=user_id)

        # Look for keys that were created by automatic extraction
        to_delete = []

        for key, value in context.items():
            if isinstance(value, dict) and value.get("source") == "automatic_extraction":
                to_delete.append(key)

        # Clear these specific keys
        if to_delete:
            return await self.orchestrator.clear_user_context_memory(
                user_id=user_id,
                keys=to_delete
            )

        return True

    async def _extract_user_information(self, conversation):
        """
        Extract user information using the specified LLM.

        Args:
            conversation: The conversation text to analyze

        Returns:
            A dictionary of extracted information
        """
        # Use the specified extraction model if available, otherwise use orchestrator's default
        model = self.extraction_model or self.orchestrator.default_model

        # Create extraction prompt
        prompt = self._create_extraction_prompt(conversation)

        # Generate extraction results
        extraction_response = await model.generate(prompt)

        # Parse results into structured format
        try:
            # Parse JSON response (primary approach)
            extraction_results = json.loads(extraction_response)
        except json.JSONDecodeError:
            # Fallback parsing if LLM doesn't return valid JSON
            extraction_results = self._parse_fallback_extraction(extraction_response)

        return extraction_results

    def _create_extraction_prompt(self, conversation):
        """
        Create an optimized prompt for information extraction.

        Args:
            conversation: The conversation text to analyze

        Returns:
            A prompt string for the LLM
        """
        privacy_guidelines = (
            "IMPORTANT PRIVACY GUIDELINES:\n"
            "- DO NOT extract sensitive information like passwords, credit cards, SSNs, etc.\n"
            "- DO NOT extract personal contact information unless clearly relevant\n"
            "- Focus on preferences, interests, and non-sensitive personal details\n"
            "- Prefer general categories over specific identifiers\n\n"
        )

        return (
            "Based on the following conversation, extract important information about the user "
            "that should be remembered for future interactions. For each piece of information, "
            "include:\n"
            "1. The specific information (value)\n"
            "2. The category/key it belongs to (e.g., name, location, preference)\n"
            "3. A confidence score (0.0-1.0) indicating how certain you are\n"
            "4. An importance score (0.0-1.0) indicating how important this is to remember\n\n"
            "Format your response as a JSON object with the following structure:\n"
            "{\n"
            '  "extracted_info": [\n'
            '    {\n'
            '      "key": "category name",\n'
            '      "value": "the extracted information",\n'
            '      "confidence": 0.95,\n'
            '      "importance": 0.8\n'
            '    },\n'
            '    ...\n'
            '  ]\n'
            "}\n\n"
            + privacy_guidelines
            + f"Conversation:\n{conversation}\n\n"
            "If there is no relevant information to extract, return an empty array for "
            "extracted_info."
        )

    async def _process_extraction_results(self, extraction_results, user_id):
        """
        Process extraction results and update context memory.

        Args:
            extraction_results: Dictionary of extracted information
            user_id: The user's ID
        """
        if not extraction_results or "extracted_info" not in extraction_results:
            return

        # Get existing user context memory
        existing_context = await self.orchestrator.get_user_context_memory(user_id=user_id)

        # Process each extracted item
        knowledge_updates = {}
        for item in extraction_results["extracted_info"]:
            # Skip items below confidence threshold
            if item["confidence"] < self.confidence_threshold:
                continue

            key = item["key"]
            value = item["value"]
            importance = item["importance"]

            # Skip extraction of sensitive information
            if self._is_sensitive_information(key, value):
                continue

            # Handle conflicts with existing information
            if key in existing_context:
                # Determine if we should update based on confidence and importance
                if not self._should_update_existing(key, value, existing_context[key], importance):
                    continue

            # Add to updates with metadata
            knowledge_updates[key] = {
                "value": value,
                "importance": importance,
                "source": "automatic_extraction",
                "timestamp": time.time(),
                "confidence": item["confidence"]
            }

        # Store updates in context memory if any exist
        if knowledge_updates:
            await self.orchestrator.add_user_context_memory(
                user_id=user_id,
                knowledge=knowledge_updates,
                source="automatic_extraction",
                importance=0.85  # Default importance for automatic extraction
            )

    def _is_sensitive_information(self, key: str, value: Any) -> bool:
        """
        Check if the information appears to be sensitive.

        Args:
            key: The category key
            value: The value to check

        Returns:
            True if sensitive, False otherwise
        """
        key_lower = key.lower()

        # Check for sensitive key patterns
        for pattern in self._sensitive_key_patterns:
            if pattern in key_lower:
                return True

        # Check for common sensitive value patterns
        if isinstance(value, str):
            # Credit card pattern (sequence of digits)
            if len(value.replace(' ', '').replace('-', '')) >= 15:
                digits_only = ''.join(c for c in value if c.isdigit())
                if len(digits_only) >= 15:
                    return True

            # Check for email addresses if not in allowed keys
            if '@' in value and '.' in value and key_lower not in {'email', 'contact'}:
                return True

            # Phone number pattern if not in allowed keys
            if len(''.join(c for c in value if c.isdigit())) >= 10:
                if key_lower not in {'phone', 'contact', 'mobile'}:
                    return True

        return False

    def _should_update_existing(self, key, new_value, existing_value, importance):
        """
        Determine if existing information should be updated.

        Args:
            key: The key/category of the information
            new_value: The newly extracted value
            existing_value: The existing value in context memory
            importance: The importance score of the new value

        Returns:
            True if the existing information should be updated, False otherwise
        """
        # For complex updates like adding to lists, merging objects, etc.
        # Will need to implement category-specific logic

        # Simple version - higher importance items replace existing items
        if isinstance(existing_value, dict) and "importance" in existing_value:
            return importance > existing_value["importance"]

        # Default to updating
        return True

    def _parse_fallback_extraction(self, text):
        """
        Parse extraction results from text if JSON parsing fails.

        Args:
            text: The raw text response from the LLM

        Returns:
            A dictionary with extracted_info field
        """
        # Implement fallback parsing logic for when the LLM doesn't return valid JSON
        lines = text.strip().split('\n')
        extracted_info = []

        current_item = {}
        for line in lines:
            line = line.strip()
            if not line:
                if current_item and "key" in current_item and "value" in current_item:
                    # Add default values if missing
                    if "confidence" not in current_item:
                        current_item["confidence"] = 0.7
                    if "importance" not in current_item:
                        current_item["importance"] = 0.5
                    extracted_info.append(current_item)
                current_item = {}
            elif ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower()
                value = value.strip()

                if key in ["key", "category"]:
                    current_item["key"] = value
                elif key in ["value", "information"]:
                    current_item["value"] = value
                elif key == "confidence":
                    try:
                        current_item["confidence"] = float(value)
                    except ValueError:
                        current_item["confidence"] = 0.7
                elif key == "importance":
                    try:
                        current_item["importance"] = float(value)
                    except ValueError:
                        current_item["importance"] = 0.5

        # Add the last item if it exists
        if current_item and "key" in current_item and "value" in current_item:
            # Add default values if missing
            if "confidence" not in current_item:
                current_item["confidence"] = 0.7
            if "importance" not in current_item:
                current_item["importance"] = 0.5
            extracted_info.append(current_item)

        return {"extracted_info": extracted_info}
