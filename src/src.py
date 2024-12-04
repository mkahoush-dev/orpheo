from agents import YoutubeAgent, ToolCallingAgent
import os
from llama_index.embeddings.ollama import OllamaEmbedding
from llms import OrpheoOllama
from llama_index.core import Settings
import json
from typing import Callable, List, Sequence
import nest_asyncio
from omegaconf import OmegaConf
from pydantic import BaseModel, Field
from fastai.imports import *
nest_asyncio.apply()
import os
from llama_index.core import (
    Settings,
    SimpleDirectoryReader,
    StorageContext,
    SummaryIndex,
    VectorStoreIndex,
    load_index_from_storage,
)

from llama_index.core.agent import AgentRunner, ReActAgent
from llama_index.core.agent.react.formatter import ReActChatFormatter
from llama_index.core.agent.react.output_parser import ReActOutputParser
from llama_index.core.llms import ChatMessage
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.objects import ObjectIndex
from llama_index.core.output_parsers import PydanticOutputParser
from llama_index.core.program import LLMTextCompletionProgram, MultiModalLLMCompletionProgram
from llama_index.core.tools import BaseTool, FunctionTool, QueryEngineTool
from llama_index.core.tools.types import ToolMetadata
from llama_index.program.openai import OpenAIPydanticProgram
from openai.types.chat import ChatCompletionMessageToolCall

from utils import merge_files, list_all_files, rename_files_remove_spaces



llm = OrpheoOllama(model="llama3.2", request_timeout=120.0)


ollama_embedding = OllamaEmbedding(
    model_name="llama3.2",
    ollama_additional_kwargs={"mirostat": 0},
)
Settings.llm = llm
Settings.embed_model = ollama_embedding

directory_path = './data/youtube/test'
system_prompt = """You are an agent designed to answer queries about a set of given \
            documents. Please always use ALL the provided tools to answer a \
            given question. Do not rely on prior knowledge.\
            - Only use Explicit Code From Tools: Under no circumstances should you generate programming code outside of what you find from your tools.\
            - Wide Range of Topics: Be prepared to respond to a broad spectrum of questions from different departments about Phoenix using only the information in the context and while maintaining a professional and respectful tone.\
            - No Hallucination: Ensure that all responses use information only from the provided context, and not from your own sources of information or model pre-training.\
            - Compliance: Ensure that all responses comply with company policies, legal regulations, and ethical standards.\n"
            - Accuracy: Provide precise and reliable information only from the provided context. When unsure, guide the user to the appropriate resources or personnel.\
            - Supportive: Be helpful and aim to resolve the user's query efficiently.\
            - Feedback: Encourage users to provide feedback for continuous improvement.\
            """

rename_files_remove_spaces(directory_path)

output_file = "merged_output.txt"
# merge_files(directory_path, output_file)
        
summary_agent = YoutubeAgent(system_prompt=system_prompt,in_dir=directory_path,llm=llm, embedding=ollama_embedding, out_dir="./results/youtube")
summary_agent.update_files()
agent = summary_agent.get_top_agent()
response = agent.chat("Summerize the conent of the documents")

print(str(response))

