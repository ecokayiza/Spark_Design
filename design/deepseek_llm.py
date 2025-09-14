from typing import Any, List, Mapping, Optional
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.outputs import ChatGeneration, ChatResult
import requests


class DeepSeekLLM(BaseChatModel):
    """
    DeepSeek LLM wrapper for LangChain
    """
    model: str = "deepseek-chat"
    api_key: str = ""
    temperature: float = 0.7
    max_tokens: int = 4096
    base_url: str = "https://api.deepseek.com/v1/chat/completions"

    @property
    def _llm_type(self) -> str:
        """Return type of language model."""
        return "deepseek"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate chat completions from a list of messages."""
        
        # Convert LangChain messages to DeepSeek format
        deepseek_messages = []
        for message in messages:
            if isinstance(message, SystemMessage):
                deepseek_messages.append({"role": "system", "content": message.content})
            elif isinstance(message, HumanMessage):
                deepseek_messages.append({"role": "user", "content": message.content})
            elif isinstance(message, AIMessage):
                deepseek_messages.append({"role": "assistant", "content": message.content})
            else:
                deepseek_messages.append({"role": "user", "content": str(message.content)})

        # Prepare the request payload
        payload = {
            "model": self.model,
            "messages": deepseek_messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": False
        }

        # Add any additional kwargs
        payload.update(kwargs)

        # Make the API request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                message = AIMessage(content=content)
                generation = ChatGeneration(message=message)
                return ChatResult(generations=[generation])
            else:
                raise ValueError("No valid response from DeepSeek API")
                
        except requests.exceptions.RequestException as e:
            raise ValueError(f"DeepSeek API request failed: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error processing DeepSeek response: {str(e)}")

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call the DeepSeek API with a simple prompt."""
        messages = [HumanMessage(content=prompt)]
        result = self._generate(messages, stop, run_manager, **kwargs)
        return result.generations[0].message.content

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

    def invoke(self, input_data, config=None, **kwargs):
        """Invoke method for compatibility with LangChain LCEL."""
        if isinstance(input_data, list):
            # List of messages
            result = self._generate(input_data, **kwargs)
            return result.generations[0].message.content
        elif isinstance(input_data, str):
            # Simple string prompt
            return self._call(input_data, **kwargs)
        else:
            # Assume it's a message
            return self._call(str(input_data), **kwargs)


# Convenience function to create DeepSeek LLM instance
def create_deepseek_llm(api_key: str, model: str = "deepseek-chat", temperature: float = 0.7, max_tokens: int = 1024) -> DeepSeekLLM:
    """Create a DeepSeek LLM instance with the given parameters."""
    return DeepSeekLLM(
        api_key=api_key,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens
    )