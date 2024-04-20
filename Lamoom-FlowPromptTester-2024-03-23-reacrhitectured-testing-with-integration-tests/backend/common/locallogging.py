import logging
from dataclasses import dataclass

# Assuming AIModelResponse is a dataclass, if not, it should be defined accordingly.
@dataclass
class AIModelResponse:
    content: str

def log_interaction(prompt_data: str, context_data: str, ai_model_response: AIModelResponse):
    """
    Logs the interaction with the AI Model including request and response data.

    :param prompt_data: The prompt data sent to the AI Model.
    :param context_data: The context data sent to the AI Model.
    :param ai_model_response: The response received from the AI Model.
    """
    # Log the prompt data, ensuring sensitive information is redacted or truncated if necessary.
    logger.info(f"AI Model Interaction - Prompt Data: {prompt_data[:100]}... (truncated for brevity)")

    # Log the context data, ensuring sensitive information is redacted or truncated if necessary.
    logger.info(f"AI Model Interaction - Context Data: {context_data[:100]}... (truncated for brevity)")

    # Log the AI Model's response content.
    logger.info(f"AI Model Interaction - Model Response: {ai_model_response.content[:100]}... (truncated for brevity)")

    # Additional logging can be added here if needed, such as performance metrics or other relevant information.