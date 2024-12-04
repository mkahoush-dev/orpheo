from llama_index.llms.ollama import Ollama
from llms import OrpheoOllama

llm = OrpheoOllama(model="llama3.2", request_timeout=120.0)

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from llama_index.core import Settings
from llama_index.embeddings.ollama import OllamaEmbedding
import os
from llama_index.core.agent import ReActAgent

from utils import merge_files, list_all_files, rename_files_remove_spaces

ollama_embedding = OllamaEmbedding(
    model_name="llama3.2",
    ollama_additional_kwargs={"mirostat": 0},
)

Settings.llm = llm
Settings.embed_model = ollama_embedding

from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
)

from llama_index.core.tools import QueryEngineTool, ToolMetadata


# Example usage:
if __name__ == "__main__":
    directory_path = './data/youtube'    
    rename_files_remove_spaces(directory_path)
    try:
        storage_context = StorageContext.from_defaults(
            persist_dir="./storage/youtube"
        )
        index = load_index_from_storage(storage_context)

        index_loaded = True
    except:
        index_loaded = False
    query_engine_tools = []

    # load data
    
    output_file = "merged_output.txt"
    merge_files(directory_path, output_file)
    
    all_files = list_all_files(directory_path)
    file_paths = all_files
    print(file_paths)
    for file_path in file_paths:
        print(file_path)
        docs = SimpleDirectoryReader(
            input_files=[file_path], recursive=True
        ).load_data()
        index = VectorStoreIndex.from_documents(docs)
        # persist index
        index.storage_context.persist(persist_dir="./storage/youtube")

        engine = index.as_query_engine()

        query_engine_tools.append(
            QueryEngineTool(
                query_engine=engine,
                metadata=ToolMetadata(
                    name=f"expert_tool_{file_path}",
                    description=(
                        f"Provides information about {file_path} video. "
                        "Use a detailed plain text question as input to the tool."
                    ),
                ),
            ),
        )

    system_prompt = """You are an agent designed to answer queries about a set of given \
                documents. Please always use ALL the provided tools to answer a \
                given question. Do not rely on prior knowledge.\
                - Only use Explicit Code From Tools: Under no circumstances should you generate programming code outside of what you find from your tools.\
                - Wide Range of Topics: Be prepared to respond to a broad spectrum of questions while maintaining a professional and respectful tone.\
                - No Hallucination: Ensure that all responses use information only from the provided context, and not from your own sources of information or model pre-training.\
                - Compliance: Ensure that all responses comply with company policies, legal regulations, and ethical standards.\n"
                - Accuracy: Provide precise and reliable information only from the provided context. When unsure, guide the user to the appropriate resources or personnel.\
                - Supportive: Be helpful and aim to resolve the user's query efficiently.\
                """

    agent = ReActAgent.from_tools(
        query_engine_tools,
        llm=llm,
        verbose=True,
        system_prompt=system_prompt
    )

    response = agent.chat("What was the summary of this video?")
    print(str(response))

