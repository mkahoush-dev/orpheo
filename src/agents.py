import functools
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
from llama_index.agent.openai import OpenAIAgent



from llama_index.core.agent import FunctionCallingAgent
from llama_index.core.tools import BaseTool
from llama_index.core.llms import LLM

from typing import Sequence, List
from llama_index.core.base.llms.types import ChatMessage, MessageRole
from llama_index.core.tools import BaseTool
from llama_index.llms.openai import OpenAI
import tqdm

class ToolCallingAgent: 
    def __init__(
        self,
        tools: Sequence[BaseTool] = [],
        chat_history: List[ChatMessage] = None,
        system_prompt: str = None,
        blueprint: BaseModel = None,
        llm=None,
    ) -> None:
        self._blueprint = PydanticOutputParser(blueprint) if blueprint else None
        self._llm = llm
        self._tools = {tool.metadata.name: tool for tool in tools}
        if chat_history:
            chat_history.append([ChatMessage(role="system", content=system_prompt)])
        else:
            chat_history = [ChatMessage(role="system", content=system_prompt)]
        self._chat_history = chat_history 
        
        
    def reset(self) -> None:
        self._chat_history = []
        
    def query(self, message: str) -> str:
        chat_history = self._chat_history
        if self._blueprint:
            formatted_message = self._blueprint.format(query=message)
        else:
            formatted_message = message
        chat_history.append(ChatMessage(role="user", content=formatted_message))
        tools = [tool.metadata.to_openai_tool() for _, tool in self._tools.items()]

        ai_message = self._llm.chat(chat_history, tools=tools).message
        additional_kwargs = ai_message.additional_kwargs
        chat_history.append(ai_message)

        tool_calls = additional_kwargs.get("tool_calls", None)
        # parallel function calling is now supported
        if tool_calls is not None:
            for tool_call in tool_calls:
                function_message = self._call_function(tool_call)
                chat_history.append(function_message)
                ai_message = self._llm.chat(chat_history).message
                chat_history.append(ai_message)
        self._chat_history.append(ChatMessage(role="assistant", content=ai_message.content))
        return ai_message.content
    
    def _call_function(self, tool_call: ChatCompletionMessageToolCall) -> ChatMessage:
        id_ = tool_call.id
        function_call = tool_call.function
        tool = self._tools[function_call.name]
        output = tool(**json.loads(function_call.arguments))
        return ChatMessage(
            name=function_call.name,
            content=str(output),
            role="tool",
            additional_kwargs={
                "tool_call_id": id_,
                "name": function_call.name,
            },
        )
        

class YoutubeAgent():
    """
    Based on Multi-Document Agents from llama-index:
    https://docs.llamaindex.ai/en/stable/examples/agent/multi_document_agents/
    """ 

    def __init__(
        self,
        out_dir: str,
        llm=None,
        embedding=None,
        image_embed_model: str = 'clip:ViT-B/32',
        system_prompt = None,
        file_paths: List = [],
        in_dir: str = '',
    ):
        self.document_keywords = None
        self.out_dir = out_dir
        self.file_paths = file_paths
        self.docs = {} 
        self.node_parser = SentenceSplitter()
        self.llm = llm
        self.embedding = embedding
        self.image_embed_model = image_embed_model
        Settings.llm = self.llm
        Settings.embed_model = self.embedding
        self.all_tools = []
        self.agents = {}
        self.query_engines = {}
        self.in_dir = in_dir
        if system_prompt:
            self.system_prompt = system_prompt
        else:
            self.system_prompt = """ \
            You are an agent designed to answer queries about a set of given documents. \
            Please always use ALL the provided tools to answer a given question. Do not rely on prior knowledge. Alwasy answer the question.\
            """

    def _reset(self):
        self.file_paths = []
        self.docs = {}
        self.all_tools = []
        self.agents = {}
        self.query_engines = {}
    
    def update_files(self):
        """Clears the tools and agents and rebuilds new agents with given files and keywords.
        Parameters: file_paths (List[str]): a list of paths to files document_keywords (str): a comma separated list of descriptive keywords about documents contents
        max_iterations (int): maximum number of iterations for the ReAct/top agent; eg, 10.Default is 5 times number of documents. """
        self._reset()
        self.num_docs = len(self.file_paths)
        self._compose_query_engines_and_agents()
    

    def get_top_agent(self):
        return self.top_agent
    
    def list_all_files(self, directory):
        file_list = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_list.append(os.path.join(root, file))
        return file_list

    def _compose_query_engines_and_agents(self):
        all_files = self.list_all_files(self.in_dir)
        self.file_paths = all_files
        print(self.file_paths)
        for file_path in self.file_paths:
            doc = SimpleDirectoryReader(input_files=[file_path]).load_data()
            self.docs[file_path] = doc
            nodes = self.node_parser.get_nodes_from_documents(doc)
            file_title = Path(file_path).stem
            file_title = file_title.replace('-', '_').replace(' ', '_')
            doc_index_dir = os.path.join(self.out_dir, file_title)
            vector_index = None
            if not os.path.exists(doc_index_dir):
                vector_index = VectorStoreIndex(nodes)
                vector_index.storage_context.persist(persist_dir=doc_index_dir)
            else:
                storage_context = StorageContext.from_defaults(persist_dir=doc_index_dir)
                vector_index = load_index_from_storage(storage_context=storage_context)
                # build summary index            
            summary_index = SummaryIndex(nodes)
            # define query engines            
            vector_query_engine = vector_index.as_query_engine(llm=Settings.llm)
            summary_query_engine = summary_index.as_query_engine(llm=Settings.llm)
            query_engine_tools = [
                QueryEngineTool(
                    query_engine=vector_query_engine,
                    metadata=ToolMetadata(
                        name=f"vector_tool_{file_title}",
                        description=("Useful for questions related to specific aspects of" f" {file_title}."),
                    ),
                ),
                QueryEngineTool(
                    query_engine=summary_query_engine,
                    metadata=ToolMetadata(
                        name=f"summary_tool_{file_title}",
                        description=(
                            "Useful for any requests that require a holistic summary"
                            f" of EVERYTHING about {file_title}. For questions about"
                            " more specific sections, please use the vector_tool."
                        ),
                    ),
                ),
            ]

            if self.document_keywords:
                metadata_extraction_query = f"Extract metadata from this document in the format {{metadata1: entity1, metadata2: entity2, ...}} that cover the metadata types: {self.document_keywords}"
                subagent_metadata = summary_query_engine.query(metadata_extraction_query).response
                file_description = f"Some of the information in this document include {subagent_metadata}."
            else:
                file_description = ""
            system_prompt = f"""You are a specialized agent designed to answer queries about document titled {file_title}. {file_description}. You must ALWAYS use ALL the provided tools when answering a question; do NOT rely on prior knowledge."""
            
            
            
            
            subagent = ReActAgent.from_tools(
                tools=query_engine_tools,
                llm=self.llm,
                system_prompt=system_prompt,
            )
            doc_tool = QueryEngineTool(
                query_engine=subagent,
                metadata=ToolMetadata(
                    name=f"agent_expert_in_document_{file_title}",
                    description=(
                        f"This document contains information about {file_title}. Use"
                        f" this tool if you want to answer any questions about the document {file_title}. {file_description}\n"
                    ),
                ),
            )
            self.all_tools.append(doc_tool)
            # record per document artifacts
            self.agents[file_title] = subagent
            self.query_engines[file_title] = vector_index.as_query_engine()
        if self.all_tools == []:
            raise Exception('no tools are available!')

        self.obj_index = ObjectIndex.from_objects(
            self.all_tools,
            index_cls=VectorStoreIndex,
        )
        self.top_agent = ReActAgent.from_tools(
            tool_retriever=self.obj_index.as_retriever(),
            system_prompt=self.system_prompt,
            verbose=True,
        )