import chainlit as cl
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_community.vectorstores.faiss import FAISS
from langchain.chains.qa_with_sources.retrieval import RetrievalQAWithSourcesChain
from langchain_openai import OpenAIEmbeddings
from langchain_openai import OpenAI


qa = None

MAX_FILES = 10
MAX_SIZE_MB = 10


@cl.on_chat_start
async def chat_start():
    files = None
    while files == None:
        files = await cl.AskFileMessage(
            content="Upload PDF file",
            accept=["application/pdf"],
            max_files=MAX_FILES,
            max_size_mb=MAX_SIZE_MB,
        ).send()
    await embed_files(files)


@cl.on_message
async def on_message(message: cl.Message):
    question = message.content
    global qa
    answer = qa(question)
    print(f"{answer=}")
    await cl.Message(content=answer["answer"]).send()


async def embed_files(files: list) -> None:
    docs = list()
    for f in files:
        loader = PyPDFLoader(f.path)
        pages = loader.load_and_split()
        docs.extend(pages)
    embeddings = OpenAIEmbeddings()
    faiss = FAISS.from_documents(docs, embedding=embeddings)
    llm = OpenAI()
    global qa
    qa = RetrievalQAWithSourcesChain.from_chain_type(
        llm=llm, chain_type="map_reduce", retriever=faiss.as_retriever()
    )
    await cl.Message(content="Embedding done").send()
