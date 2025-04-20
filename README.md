# How to run the code locally: 
## Pre-requisite 1: You need to update the config.py file. 
- Error seen will be: `ModuleNotFoundError: No module named 'config'`
- API key is not uploaded for privacy reasons. For access, please contact Elykah Tejol or provide your own Groq API key under the skeleton config.py file as follows:
     1. `"GROQ_API_KEY = "YOUR_API_CODE_HERE"` and replace the YOUR_API_CODE_HERE with your Groq API key. 

## Pre-requisite 2: venv 
1) Within the **nice_gui directory**, create a virtual environment to download the dependencies.
```
# MUST BE UNDER THE nice_gui DIRECTORY

python3 -m venv venv     # You may only need python not python3, depending on your software. 
```
or 
```
virtualenv -p python venv
```
2) Activate virtual environment 
```
source venv/bin/activate   # On Mac/Linux
venv\Scripts\activate      # On Windows (PowerShell)
venv\Scripts\activate.bat  # On Windows (CMD)
```

3) Install dependencies!
```
pip3 install -r requirements.txt # You may need only pip not pip3, depending on your software.
```

## Finally, running the code! This will be under the nice_gui directory
```
python3 dorothy_gui.py
# and then open http://localhost:8080/ for the local server.
```

---
## Background 
This project was created for BIOIN 401 at the University of Alberta (Winter 2025 term). 

## Softwares used 
- Llama 3-70B accessed with Groq API
- FAISS accessed by Langchain for the vector database
- NiceGUI for the website GUI
- Edge TTS for the voice using Python library

## Deprecated software, no longer used
- PyQT, formerly the software GUI 
- Wav2Lip: Used GitHub's open source library for lip syncing. 
- Sync API: Used sync's POST and GET requests to create the lip synced video. 

## Information about the files in GitHub
_Current directory (nice_gui)_
- nice_gui: Used to deploy a locally hosted website of our program.
- faiss_index: Has the vector database used for the RAG system
- static: All files used for the code (mp4 and jpg) since locally hosting for now.
   
_Data directory_
- articles: Folder of all the articles used for the faiss database
  
_Deprecated Directories_
- pyqt: Folder of past implementation of the program within pyQT
- llama.ipynb: Colab notebook of previous implementations of the LLM
- llama3_70b: Colab notebook of previous implementation of the LLM. This notebook is the one the nice_gui code is based on.
- new_alchemist.ipynb: Colab notebook of previous implementations of the LLM
