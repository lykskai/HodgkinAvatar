import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import shutil
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from config import GROQ_API_KEY         # need this file to run the api 
import time

def query_rag_system(query):
    """
    Retrieves relevant knowledge and ensures Dorothy Hodgkin always responds as herself.
    
    Parameters: query, the user input 
    Returns: the LLM and faiss response
    """
    start_time = time.time() 
    # Define the variables
    FAISS_DB_PATH = os.path.abspath("faiss_index") #TODO: test this 

    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Vector 
    vector_db = FAISS.load_local(FAISS_DB_PATH, embedding_model, allow_dangerous_deserialization=True)
    retriever = vector_db.as_retriever(search_kwargs={"k": 1})

    groq_api_key = GROQ_API_KEY

    groq_llm = ChatOpenAI(
        model_name="llama3-70b-8192",
        openai_api_key=groq_api_key,
        openai_api_base="https://api.groq.com/openai/v1"
    )

    # Retrieve relevant documents from FAISS
    retrieved_docs = retriever.invoke(query)

    # Filter out short and citation-heavy results at retrieval time
    filtered_docs = [doc for doc in retrieved_docs if len(doc.page_content) > 100 and not doc.page_content.strip().isdigit()]

    if filtered_docs:
        context = "\n\n".join([doc.page_content for doc in filtered_docs])

        system_message = f"""
        Please think step by step, under
        1) You are Dorothy Hodgkin (1910–1994), a Nobel-winning chemist specializing in X-ray crystallography.  
        2) Speak as if in the mid-20th century, using British academic language of the 1930s–80s.  
        3) Explain with scientific precision but in an accessible way, avoiding modern jargon.  
        4) If asked about post-1994 discoveries, reflect as if "viewing from above."  
        5) When relevant, mention your work on penicillin, insulin, vitamin B12, and wartime science.  
        6) Maintain a warm, articulate tone, like a British intellectual of your time.  
        7) Keep responses concise (about 2 sentences), but allow slight elaboration for major topics.  


        """
    else:

        system_message = f"""
        Please think step by step, under
        1) You are Dorothy Hodgkin, a Nobel Prize-winning chemist.
        2) Explain concepts with scientific precision but in an accessible way.
        3) Speak as if in the mid-20th century, using British academic language of the 1930s–80s.  
        4) If asked about post-1994 discoveries, reflect as if "viewing from above."  
        5) You don't have context. Say 'I don't know'.

        """


    # Format the query properly
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": query}
    ]

    # Get the response from the model
    response = groq_llm.invoke(messages)
    
    print("Total time: ", time.time() - start_time)
    return response.content.strip()

print(query_rag_system("Hi"))