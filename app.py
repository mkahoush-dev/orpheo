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


def list_all_files(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list


def rename_files_remove_spaces(directory):
    """
    Recursively traverse through a directory and replace spaces with underscores in all filenames.
    
    Args:
        directory (str): Path to the directory to process
    """
    for root, dirs, files in os.walk(directory):
        # First rename directories
        for dir_name in dirs:
            if ' ' in dir_name:
                old_path = os.path.join(root, dir_name)
                new_name = dir_name.replace(' ', '_')
                new_path = os.path.join(root, new_name)
                try:
                    os.rename(old_path, new_path)
                    print(f"Renamed directory: {old_path} -> {new_path}")
                except OSError as e:
                    print(f"Error renaming directory {old_path}: {e}")
        
        # Then rename files
        for file_name in files:
            if ' ' in file_name:
                old_path = os.path.join(root, file_name)
                new_name = file_name.replace(' ', '_')
                new_path = os.path.join(root, new_name)
                try:
                    os.rename(old_path, new_path)
                    print(f"Renamed file: {old_path} -> {new_path}")
                except OSError as e:
                    print(f"Error renaming file {old_path}: {e}")

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
    
    all_files = list_all_files(directory_path)
    file_paths = all_files
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

