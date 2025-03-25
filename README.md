# HodgkinAvatar

## How to run the code 
Within pyqt directory, create virtual environment (did not push to git to avoid unnecessary bloat)
```
python3 -m venv venv
```
or 
```
virtualenv -p python venv
```
Activate virtual environment 
```
source venv/bin/activate   # on mac/linux
venv\Scripts\activate      # On Windows (PowerShell)
venv\Scripts\activate.bat  # On Windows (CMD)
```

Install dependencies!
```
pip3 install -r requirements.txt
```


## Explanation of how the models work 

- The text model, TTS, and lipsyncing are all integrated within a single Colab notebook (llama3_70b).
- The files used for this integration are stored in drive, which are the following:

  1. FAISS index for the RAG Database
  2. The text to speech output is stored in drive, and pulled from drive in the Colab code
  3. The video used for lip syncing is stored in drive
  4. The mp4 output is currently stored in drive as well.
 
<img width="600" alt="Screenshot 2025-03-13 at 12 38 30 PM" src="https://github.com/user-attachments/assets/c2a87fac-8471-49a7-9b3e-764ee54c9968" />
<img width="600" alt="Screenshot 2025-03-13 at 12 38 51 PM" src="https://github.com/user-attachments/assets/99bfde1a-92a5-4efe-a84a-a40fad393327" />

---

## Some more background 
- Llama 3-70B accessed with Groq API
- FAISS accessed by Langchain
- Edge TTS (placeholder) using Python library
- Wav2Lip: Used GitHub's open source library (PREVIOUSLY USED)
- Sync API: Used sync's POST and GET requests to create the lip synced video. 
