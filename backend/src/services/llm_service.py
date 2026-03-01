import time
import asyncio
from typing import Optional, Dict, Any, List, Union, Callable
from dataclasses import dataclass
from enum import Enum

from openai import AzureOpenAI
from lib.logger import logging
from langchain_openai import AzureChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from configs.config import azure_gpt_settings, azure_openai_settings, azure_gpt4o_settings
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"


@dataclass
class LLMConfig:
    """Configuration for LLM calls."""
    provider: LLMProvider = LLMProvider.OPENAI
    model: str = "llama3:8b"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    api_key: Optional[str] = None
    api_version: Optional[str] = None
    api_endpoint: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 60
    max_retries: int = 3
    streaming: bool = False
    cache: bool = True
    verbose: bool = False


@dataclass
class LLMResponse:
    """Standardized LLM response."""
    content: str
    raw_response: Any
    tokens_used: Optional[Dict[str, int]] = None
    latency_ms: Optional[float] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    cached: bool = False


class LLMBrain:
    """Production-grade async LLM caller with comprehensive features."""
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """Initialize the LLM caller with configuration."""
        self.config = config or LLMConfig()
        self.llm = self._initialize_llm()
        self._call_count = 0
        self._total_tokens = 0
        self._cache: Dict[str, LLMResponse] = {}
        self._cache_lock = asyncio.Lock()
        
    def _initialize_llm(self):
        """Initialize the appropriate LLM based on provider."""
        common_params = {
            "temperature": self.config.temperature,
            "timeout": self.config.timeout,
            "model": self.config.model,
        }
            
        if self.config.streaming:
            common_params["streaming"] = True
        
        try:
            if self.config.provider == LLMProvider.OPENAI:
                if self.config.api_key:
                    common_params["api_key"] = self.config.api_key
                if self.config.max_tokens:
                    common_params["max_completion_tokens"] = self.config.max_tokens
                if self.config.api_endpoint:
                    common_params["azure_endpoint"] = self.config.api_endpoint
                if self.config.api_version:
                    common_params["api_version"] = self.config.api_version
                return AzureChatOpenAI(**common_params)
                
            elif self.config.provider == LLMProvider.ANTHROPIC:
                if self.config.api_key:
                    common_params["anthropic_api_key"] = self.config.api_key
                if self.config.max_tokens:
                    common_params["max_tokens"] = self.config.max_tokens
                return ChatAnthropic(**common_params)
                
            elif self.config.provider == LLMProvider.OLLAMA:
                ollama_params = {
                    "model": self.config.model,
                    "temperature": self.config.temperature,
                }
                if self.config.base_url:
                    ollama_params["base_url"] = self.config.base_url
                else:
                    ollama_params["base_url"] = "http://localhost:11434"  # Default Ollama URL
                    
                if self.config.max_tokens:
                    ollama_params["num_predict"] = self.config.max_tokens
                
                return ChatOllama(**ollama_params)
                
            else:
                raise ValueError(f"Unsupported provider: {self.config.provider}")
                
        except Exception as e:
            logging.error(f"Failed to initialize LLM: {e}")
            raise
    
    def _generate_cache_key(self, prompt: str, system_message: Optional[str]) -> str:
        """Generate a cache key for the request."""
        return f"{self.config.provider}:{self.config.model}:{system_message}:{prompt}"
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((Exception,)),
        reraise=True
    )
    async def _make_llm_call(self, messages: List[Union[HumanMessage, SystemMessage, AIMessage]]) -> Any:
        """Make the actual LLM call with retry logic."""
        return await self.llm.ainvoke(messages)
    
    async def call_invoke(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        context: Optional[List[Dict]] = None,
        stream_callback: Optional[Callable[[str], None]] = None,
        disable_cache: bool = False
    ) -> LLMResponse:
        """
        Make an async LLM call with comprehensive error handling and features.

        Args:
            prompt: The user prompt
            system_message: Optional system message
            context: Optional context dictionary for prompt templating
            stream_callback: Optional callback for streaming responses
            disable_cache: If True, bypass cache for this call

        Returns:
            LLMResponse object with the response and metadata
        """
        start_time = time.time()

        # Check cache if enabled and not disabled for this call
        if self.config.cache and not disable_cache:
            cache_key = self._generate_cache_key(prompt, system_message)
            async with self._cache_lock:
                if cache_key in self._cache:
                    logging.info("Returning cached response")
                    cached_response = self._cache[cache_key]
                    cached_response.cached = True
                    return cached_response
        
        try:
            # Prepare messages
            messages = []
            if system_message:
                messages.append(SystemMessage(content=system_message))
            
            # Apply context if provided
            if context:
                prompt = prompt.format(**context)
            
            messages.append(HumanMessage(content=prompt))
            
            # Log the call
            self._call_count += 1
            if self.config.verbose:
                logging.info(f"Making LLM call #{self._call_count}")
                logging.debug(f"Prompt: {prompt[:100]}...")
            
            # Handle streaming
            if self.config.streaming and stream_callback:
                response_content = ""
                async for chunk in self.llm.astream(messages):
                    if hasattr(chunk, 'content'):
                        response_content += chunk.content
                        if asyncio.iscoroutinefunction(stream_callback):
                            await stream_callback(chunk.content)
                        else:
                            stream_callback(chunk.content)
                
                raw_response = response_content
                content = response_content
            else:
                # Make the call with retry logic
                raw_response = await self._make_llm_call(messages)
                content = raw_response.content
            
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract token usage if available
            tokens_used = None
            if hasattr(raw_response, 'response_metadata'):
                usage = raw_response.response_metadata.get('token_usage', {})
                if usage:
                    tokens_used = {
                        'prompt_tokens': usage.get('prompt_tokens', 0),
                        'completion_tokens': usage.get('completion_tokens', 0),
                        'total_tokens': usage.get('total_tokens', 0)
                    }
                    self._total_tokens += tokens_used['total_tokens']
            
            # Create response object
            response = LLMResponse(
                content=content,
                raw_response=raw_response,
                tokens_used=tokens_used,
                latency_ms=latency_ms,
                provider=self.config.provider.value,
                model=self.config.model,
                cached=False
            )
            
            # Cache the response if enabled and not disabled for this call
            if self.config.cache and not disable_cache:
                cache_key = self._generate_cache_key(prompt, system_message)
                async with self._cache_lock:
                    self._cache[cache_key] = response
            
            if self.config.verbose:
                logging.info(f"LLM call completed in {latency_ms:.2f}ms")
                if tokens_used:
                    logging.info(f"Tokens used: {tokens_used['total_tokens']}")
            
            return response
            
        except Exception as e:
            logging.error(f"LLM call failed after retries: {e}")
            raise
    
    async def call_with_chain(
        self,
        prompt_template: str,
        input_variables: Dict[str, Any],
        output_parser: Optional[Any] = None
    ) -> Any:
        """
        Make an async LLM call using LangChain's chain syntax.
        
        Args:
            prompt_template: Template string with {variables}
            input_variables: Dictionary of variables to fill the template
            output_parser: Optional output parser (default: StrOutputParser)
            
        Returns:
            Parsed output from the LLM
        """
        try:
            prompt = ChatPromptTemplate.from_template(prompt_template)
            parser = output_parser or StrOutputParser()
            
            chain = prompt | self.llm | parser
            
            start_time = time.time()
            result = await chain.ainvoke(input_variables)
            latency_ms = (time.time() - start_time) * 1000
            
            if self.config.verbose:
                logging.info(f"Chain call completed in {latency_ms:.2f}ms")
            
            return result
            
        except Exception as e:
            logging.error(f"Chain call failed: {e}")
            raise
    
    async def batch_call(
        self,
        prompts: List[str],
        system_message: Optional[str] = None,
        concurrent: bool = True,
        max_concurrent: int = 5
    ) -> List[LLMResponse]:
        """
        Make batch LLM calls efficiently with optional concurrency.
        
        Args:
            prompts: List of prompts to process
            system_message: Optional system message for all prompts
            concurrent: Whether to process concurrently
            max_concurrent: Maximum concurrent requests
            
        Returns:
            List of LLMResponse objects
        """
        if not concurrent:
            # Sequential processing
            responses = []
            for i, prompt in enumerate(prompts):
                if self.config.verbose:
                    logging.info(f"Processing batch item {i+1}/{len(prompts)}")
                
                response = await self.call(prompt, system_message)
                responses.append(response)
            
            return responses
        
        # Concurrent processing with semaphore
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_with_semaphore(i: int, prompt: str):
            async with semaphore:
                if self.config.verbose:
                    logging.info(f"Processing batch item {i+1}/{len(prompts)}")
                return await self.call(prompt, system_message)
        
        tasks = [process_with_semaphore(i, prompt) for i, prompt in enumerate(prompts)]
        responses = await asyncio.gather(*tasks)
        
        return responses
    
    async def clear_cache(self):
        """Clear the response cache."""
        async with self._cache_lock:
            self._cache.clear()
            logging.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            "total_calls": self._call_count,
            "total_tokens": self._total_tokens,
            "cache_size": len(self._cache),
            "provider": self.config.provider.value,
            "model": self.config.model
        }


llm_config = LLMConfig(
    provider = LLMProvider.OPENAI,
    model = azure_gpt_settings.AZURE_OPENAI_GPT_DEPLOYMENT,
    api_key= azure_gpt_settings.AZURE_OPENAI_GPT_API_KEY,
    api_version= azure_gpt_settings.AZURE_OPENAI_GPT_API_VERSION,
    api_endpoint= azure_gpt_settings.AZURE_OPENAI_GPT_ENDPOINT,
    temperature = 0,
    verbose = True
)


brain = LLMBrain(config = llm_config)

# Separate brain for highlighting to avoid rate limit conflicts
highlight_llm_config = LLMConfig(
    provider = LLMProvider.OPENAI,
    model = azure_gpt4o_settings.AZURE_OPENAI_GPT4O_DEPLOYMENT,
    api_key= azure_gpt_settings.AZURE_OPENAI_GPT_API_KEY,
    api_version= azure_gpt_settings.AZURE_OPENAI_GPT_API_VERSION,
    api_endpoint= azure_gpt_settings.AZURE_OPENAI_GPT_ENDPOINT,
    temperature = 0,
    verbose = True
)

highlight_brain = LLMBrain(config = highlight_llm_config)

azure_embedding_client = AzureOpenAI(
            api_key=azure_openai_settings.AZURE_OPENAI_API_KEY,
            api_version=azure_openai_settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=azure_openai_settings.AZURE_OPENAI_ENDPOINT)