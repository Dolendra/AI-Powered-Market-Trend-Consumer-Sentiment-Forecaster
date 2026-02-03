"""
Custom Groq LLM wrapper for LangChain compatibility.
Since langchain_community doesn't include Groq in newer versions,
we create a custom wrapper using the groq package directly.
"""

import logging
from typing import Any, List, Optional
from groq import Groq

# Try to import LangChain LLM base class (location varies by version)
try:
    from langchain.llms.base import LLM
    from langchain.callbacks.manager import CallbackManagerForLLMRun
except ImportError:
    try:
        from langchain_core.language_models.llms import BaseLLM as LLM
        from langchain_core.callbacks.manager import CallbackManagerForLLMRun
    except ImportError:
        # Fallback for very new versions
        from langchain_core.language_models import BaseLLM as LLM
        from langchain_core.callbacks import CallbackManagerForLLMRun
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import GROQ_API_KEY, GROQ_MODEL

logger = logging.getLogger(__name__)


class GroqLLM(LLM):
    """Custom Groq LLM wrapper for LangChain."""
    
    groq_api_key: str = ""
    model_name: str = "llama-3.1-70b-versatile"
    temperature: float = 0.1
    
    def __init__(self, groq_api_key: str = None, model_name: str = None, temperature: float = 0.1, **kwargs):
        """Initialize Groq LLM."""
        super().__init__(**kwargs)
        self.groq_api_key = groq_api_key or GROQ_API_KEY
        self.model_name = model_name or GROQ_MODEL
        self.temperature = temperature
    
    @property
    def _llm_type(self) -> str:
        """Return type of LLM."""
        return "groq"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call the Groq API."""
        try:
            client = Groq(api_key=self.groq_api_key)
            
            # Prepare messages for chat completion
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            # Call Groq API
            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                stop=stop,
                **kwargs
            )
            
            # Extract text from response
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content.strip()
            else:
                return ""
                
        except Exception as e:
            logger.error(f"Error calling Groq API: {e}")
            raise
    
    @property
    def _identifying_params(self) -> dict:
        """Get identifying parameters."""
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
        }
