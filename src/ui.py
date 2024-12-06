import chainlit as cl
from utils import merge_files, list_all_files, rename_files_remove_spaces
from agents import YoutubeAgent, ToolCallingAgent
import os
from llama_index.embeddings.ollama import OllamaEmbedding
from llms import OrpheoOllama
from llama_index.core import Settings

def init(query: str):
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
    response = agent.chat(query)

    return response


@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Morning routine ideation",
            message="Can you help me create a personalized morning routine that would help increase my productivity throughout the day? Start by asking me about my current habits and what activities energize me in the morning.",
            icon="/public/idea.svg",
            ),

        cl.Starter(
            label="Explain superconductors",
            message="Explain superconductors like I'm five years old.",
            icon="/public/learn.svg",
            ),
        cl.Starter(
            label="Python script for daily email reports",
            message="Write a script to automate sending daily email reports in Python, and walk me through how I would set it up.",
            icon="/public/terminal.svg",
            ),
        cl.Starter(
            label="Text inviting friend to wedding",
            message="Write a text asking a friend to be my plus-one at a wedding next month. I want to keep it super short and casual, and offer an out.",
            icon="/public/write.svg",
            )
        ]



@cl.step(type="tool")
async def Orpheo(query: str):
    await cl.sleep(0.5)
    return init(query)


@cl.on_message
async def main(message: cl.Message):
    # Call the tool
    tool_res = await Orpheo(message.content)

    # Send the final answer.
    await cl.Message(content=tool_res).send()

