from agents import MultiDocumentAgents
import os
from llama_index.embeddings.ollama import OllamaEmbedding
from llms import OrpheoOllama
from llama_index.core import Settings

llm = OrpheoOllama(model="llama3.2", request_timeout=120.0)


ollama_embedding = OllamaEmbedding(
    model_name="llama3.2",
    ollama_additional_kwargs={"mirostat": 0},
)
Settings.llm = llm
Settings.embed_model = ollama_embedding

def list_all_files(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list

directory_path = './data/youtube'
all_files = list_all_files(directory_path)
print(all_files)
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
            
summary_agent = MultiDocumentAgents(system_prompt=system_prompt,file_paths=all_files,llm=llm, embedding=ollama_embedding, out_dir="./results")
summary_agent.update_files()
agent = summary_agent.get_top_agent()
# import pdb; pdb.set_trace(
response = agent.chat("Summerize the conent of the documents")

print(str(response))


