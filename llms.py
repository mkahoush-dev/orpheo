import pdb
import random
import string
import uuid
from datetime import timezone
from typing import Any, Dict, Optional, Sequence, Union

from dateutil import parser
from llama_index.core.base.llms.types import (
    ChatResponse,
    ChatResponseAsyncGen,
    CompletionResponse,
)
from llama_index.core.llms.callbacks import llm_chat_callback, llm_completion_callback
from llama_index.core.constants import DEFAULT_CONTEXT_WINDOW
from llama_index.core.llms import ChatMessage
from llama_index.llms.ollama import Ollama
from ollama import AsyncClient, Client
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.chat.chat_completion import Choice
from openai.types.completion_usage import CompletionUsage
from llama_index.llms.azure_openai import AzureOpenAI


DEFAULT_REQUEST_TIMEOUT = 30.0


def convert_to_total_seconds(time_string):
    """
    Converts an ISO 8601 formatted time string to total seconds.

    Args:
        time_string (str): A string representing the date and time in ISO 8601 format.

    Returns:
        int: The total number of seconds since the Unix epoch.
    """
    dt = parser.isoparse(time_string)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return int(dt.timestamp())


def generate_unique_id(length=35):
    """
    Generates a unique identifier of a specified length using a combination of UUID and base62 encoding.

    Args:
        length (int, optional): The desired length of the unique identifier. Default is 35.

    Returns:
        str: A unique identifier string of the specified length, consisting of alphanumeric characters.
    """
    characters = string.ascii_letters + string.digits
    raw_uuid = uuid.uuid4().hex
    uuid_int = int(raw_uuid, 16)
    base62_id = ''
    base = len(characters)
    while uuid_int > 0:
        uuid_int, remainder = divmod(uuid_int, base)
        base62_id = characters[remainder] + base62_id
    if len(base62_id) < length:
        choices = random.choices(characters, k=length - len(base62_id))
        base62_id = base62_id + ''.join(choices)
    elif len(base62_id) > length:
        base62_id = base62_id[:length]
    return base62_id


def format_ollama_response(response):
    """
    Formats a response from the Ollama API into structured chat and completion messages.

    The function extracts information from the given response, formats it into `ChatMessage` and `ChatCompletion`
    objects, and then wraps these objects into a `ChatResponse`.
    - `ChatMessage`: Contains the role and content of the message.
    - `ChatCompletionMessage`: Contains the raw content and role of the message.
    - `CompletionUsage`: Contains usage statistics from the response.
    - `ChatCompletion`: Contains the completion ID, choices, creation timestamp, model, object type, and usage.
    - `ChatResponse`: Contains the formatted `ChatMessage` and `ChatCompletion`.

    Args:
        response (OllamaResponse): A response object from the Ollama API containing both the message and raw data.

    Returns:
        ChatResponse: A structured response consisting of a formatted chat message and raw completion data.
    """
    if response.message.content == "":
        response.message.content = None

    if response.raw['message']['content'] == "":
        response.raw['message']['content'] = None

    message = ChatMessage(
        role=response.message.role,
        content=response.message.content,
        additional_kwargs={}
    )

    raw_message = ChatCompletionMessage(
        content=response.raw['message']['content'],
        role=response.raw['message']['role'],
    )

    usage = CompletionUsage(**response.raw['usage'])

    raw = ChatCompletion(
        id=f"chatcmpl-{generate_unique_id(26)}",
        choices=[
            Choice(
                finish_reason=response.raw['done_reason'],
                index=0,
                logprobs=None,
                message=raw_message,
            )
        ],
        created=convert_to_total_seconds(response.raw['created_at']),
        model=response.raw['model'],
        object='chat.completion',
        usage=usage,
    )
    return ChatResponse(message=message, raw=raw)


class OrpheoOllama(Ollama):
    """
    OrpheoOllama is a subclass of Ollama that provides additional functionality for chat and completion
    using a specified model.

    Args:
        model (str): The name of the model to use.
        base_url (str, optional): The base URL for the API. Defaults to "http://localhost:11434".
        temperature (float, optional): The temperature setting for the model. Defaults to 0.75.
        context_window (int, optional): The context window size. Defaults to DEFAULT_CONTEXT_WINDOW.
        request_timeout (float, optional): The request timeout in seconds. Defaults to DEFAULT_REQUEST_TIMEOUT.
        prompt_key (str, optional): The key for the prompt. Defaults to "prompt".
        json_mode (bool, optional): Whether to use JSON mode. Defaults to False.
        additional_kwargs (Dict[str, Any], optional): Additional keyword arguments for the model. Defaults to {}.
        client (Optional[Client], optional): The client for synchronous requests. Defaults to None.
        async_client (Optional[AsyncClient], optional): The client for asynchronous requests. Defaults to None.
        is_function_calling_model (bool, optional): Whether the model supports function calling. Defaults to True.
        keep_alive (Optional[Union[float, str]], optional): The keep-alive setting. Defaults to None.
        **kwargs (Any): Additional keyword arguments.
    """
    def __init__(
        self,
        model: str,
        temperature: float = 0.75,
        context_window: int = DEFAULT_CONTEXT_WINDOW,
        request_timeout: float = DEFAULT_REQUEST_TIMEOUT,
        prompt_key: str = "prompt",
        json_mode: bool = False,
        additional_kwargs: Dict[str, Any] = {},
        client: Optional[Client] = None,
        async_client: Optional[AsyncClient] = None,
        is_function_calling_model: bool = True,
        keep_alive: Optional[Union[float, str]] = None,
        **kwargs: Any,
    ) -> None:
        """Initializes the OrpheoOllama instance with the provided parameters."""
        super().__init__(
            model=model,
            temperature=temperature,
            context_window=context_window,
            request_timeout=request_timeout,
            prompt_key=prompt_key,
            json_mode=json_mode,
            additional_kwargs=additional_kwargs,
            client=client,
            async_client=async_client,
            is_function_calling_model=is_function_calling_model,
            keep_alive=keep_alive,
            kwargs=kwargs,
        )

    @llm_chat_callback()
    def chat(
        self,
        messages: Sequence[ChatMessage],
        **kwargs: Any,
    ) -> ChatResponse:
        """
        Connector to handle the chat requests with Ollama.

        Args:
            messages (Sequence[ChatMessage]): A sequence of chat messages.
            **kwargs (Any): Additional keyword arguments.

        Returns:
            ChatResponse: The response from the chat model.
        """
        response = super().chat(messages, **kwargs)
        response = format_ollama_response(response)
        return response

    @llm_completion_callback()
    def complete(
        self,
        prompt: str,
        formatted: bool = False,
        **kwargs: Any
    ) -> CompletionResponse:
        """
        Connector to handle the completion requests with Ollama.

        Args:
            prompt (str): The input prompt for completion.
            formatted (bool, optional): Whether the response should be formatted. Defaults to False.
            **kwargs (Any): Additional keyword arguments.

        Returns:
            CompletionResponse: The response from the completion model.
        """
        response = super().complete(prompt, formatted, **kwargs)
        return format_ollama_response(response)

    @llm_chat_callback()
    async def achat(
        self,
        messages: Sequence[ChatMessage],
        **kwargs: Any
    ) -> ChatResponseAsyncGen:
        """
        Connector to handle the asynchronous chat requests with Ollama.

        Args:
            messages (Sequence[ChatMessage]): A sequence of chat messages.
            **kwargs (Any): Additional keyword arguments.

        Returns:
            ChatResponse: The response from the chat model.
        """
        response = await super().achat(messages, **kwargs)
        return format_ollama_response(response)


if __name__ == "__main__":
    llm = OrpheoOllama(model="llama3.2")
    msg = [ChatMessage(role="user", content="Hello!")]
    resp = llm.chat(msg)
    print(resp)