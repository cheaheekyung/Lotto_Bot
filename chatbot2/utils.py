from django.conf import settings
import os
from glob import glob
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough



OPENAI_API_KEY = settings.OPENAI_API_KEY


def load_documents():
    """
    Description: ../data 폴더에있는 모든 pdf문서를 로드하는 함수

    - PyPDFLoader를 사용해 로드
    - 벡터스토어에 저장할때 RecursiveCharacterTextSplitter 를 사용하니 load_and_split 말고 그냥 load 만 사용
    """
    file_paths = glob(os.path.join('data/', '*.pdf'))
    print(file_paths)
    documents = []
    
    for file_path in file_paths:
        loader = PyPDFLoader(file_path)
        documents += loader.load()
    return documents


def create_vectorstore():
    """
    Description: 문서를 임베딩한 후 벡터DB에 저장하는 함수
    
    - Chroma DB를 사용
    - 기존 벡터저장소가 있다면 불러오고 없다면 새로생성
    """
    persist_directory = os.path.join(settings.BASE_DIR, "vector_store")
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small",)
    
    if os.path.exists(persist_directory):
        print("✅ Using existing vector store.")
        return Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    else:
        documents = load_documents()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " "]
        )
        split_docs = text_splitter.split_documents(documents)
        
        vector_store = Chroma.from_documents(
            documents=split_docs,
            embedding=embeddings,
            persist_directory=persist_directory,
        )
        print("🔄 Creating new vector store...")
        return vector_store

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def create_response(message):
    """
    Description: message를 받으면 rag적용후 벡터DB에서 유사도높은문서에서 답변을 찾아 답변해주는 함수
    
    - LCEL 적용
    - 프롬프팅 방법 고쳐나가야함
    """
    
    vector_store = create_vectorstore()
    retriever = vector_store.as_retriever(search_kwargs={"k": 10})
    
    llm = ChatOpenAI(model="gpt-4o-mini",temperature=0)
    prompt = ChatPromptTemplate.from_template("""
        로또 관련 질문이 들어오면 아래 contexts를 참고해서 질문에 답변해.
        추천을 해달라고하면 설명과함께 당첨확률이 높은 번호를 답변해.
        답변을 할때에는 이유와 함께 설명해줘야해.
        이유는 간결하게 설명해줘.
        
        contexts: {context}
        질문: {question}
        답변: 
    """)
    
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    response = rag_chain.invoke(message)
    return response

