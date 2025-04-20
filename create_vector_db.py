""" 
This file is part of the deprecated colab notebook: llama3_70b. 
For organizational purposes, I have decided to keep a copy of the function that creates my vector database for context. 
This way of making a vector database needs to be connected to google drive. 
"""
import shutil
from google.colab import drive
import os

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")    # This is the model that converts chunks of texts to numerical vectors AKA embeddings for comparison of semantic similarity

def process_and_store_files():
    """
    Processes text files from Google Drive and fully rebuilds FAISS/Vector Database
    """

    # Mount Google Drive
    drive.mount('/content/drive')

    # Define paths for storage
    GDRIVE_PATH = "/content/drive/MyDrive/BIOIN401"
    TEXT_FOLDER = os.path.join(GDRIVE_PATH, "dorothy_science_text")
    FAISS_DB_PATH = os.path.join(GDRIVE_PATH, "faiss_index")

    # Step 1: Delete the old FAISS index (removes deleted documents from storage). 
    if os.path.exists(FAISS_DB_PATH):
        shutil.rmtree(FAISS_DB_PATH)  # Delete old FAISS index
        os.makedirs(FAISS_DB_PATH, exist_ok=True)

    docs = []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

    # Convert all the articles to embeddings and store in vector database 
    for file in os.listdir(TEXT_FOLDER):
        file_path = os.path.join(TEXT_FOLDER, file)

        if file.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        elif file.endswith(".txt"):
            loader = TextLoader(file_path)
        else:
            print(f"Skipping unsupported file: {file}")
            continue

        document = loader.load()
        split_docs = text_splitter.split_documents(document)

        # Filter out citation-heavy content: helps discard unnecessary digits 
        cleaned_docs = [
            doc for doc in split_docs if len(doc.page_content) > 100 and not doc.page_content.strip().isdigit()
        ]

        docs.extend(cleaned_docs)

    # Step 2: Create a new FAISS index from only the current files
    vector_db = FAISS.from_documents(docs, embedding_model)
    vector_db.save_local(FAISS_DB_PATH)
    print(f"FAISS database rebuilt and saved at {FAISS_DB_PATH}")

