# How to run the code: 
## Pre-requisite 1: You need the config.py file. 
This is not uploaded due to the GroqAPI code. For access, please contact Elykah Tejol or provide your own Groq API key under a config.py file. 

## Pre-requisite 2: venv 
1) Within **nice_gui directory**, create virtual environment (did not push to git to avoid unnecessary bloat)
```
python3 -m venv venv
```
or 
```
virtualenv -p python venv
```
2) Activate virtual environment 
```
source venv/bin/activate   # on mac/linux
venv\Scripts\activate      # On Windows (PowerShell)
venv\Scripts\activate.bat  # On Windows (CMD)
```

3) Install dependencies!
```
pip3 install -r requirements.txt # you may need only pip not pip3, depending on your software
```

## Finally, running the code! 
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
- articles: Folder of all the articles used for the faiss database
- nice_gui: **Currently used directory**, to deploy a locally hosted website of our program
- pyqt: Folder of past implementation of the program within pyQT
- llama.ipynb: colab notebook of previous implementations of the LLM
- llama3_70b: colab notebook of previous implementation of the LLM. This notebook is the one the nice_gui code is based on.
- new_alchemist.ipynb: colab notebook of previous implementations of the LLM
