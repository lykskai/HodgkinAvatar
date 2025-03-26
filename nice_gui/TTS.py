import asyncio
import edge_tts
import base64

async def speak(text: str, voice: str = "en-GB-SoniaNeural") -> None:
    """
    Generate an HTML5 audio element for text-to-speech in web browser
    
    Args:
        text (str): Text to be spoken
        voice (str, optional): Voice to use. Defaults to British English female voice.
    
    Returns:
        str: HTML5 audio element with base64 encoded audio
    """
    try:
        # Generate audio using Edge TTS
        communicate = edge_tts.Communicate(text, voice)
        audio_data = bytearray()
        
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.extend(chunk["data"])
        
        # Convert audio to base64 for web playback
        base64_audio = base64.b64encode(audio_data).decode('utf-8')
        
        # Return HTML5 audio element
        return f'<audio autoplay><source src="data:audio/wav;base64,{base64_audio}" type="audio/wav"></audio>'
    
    except Exception as e:
        print(f"TTS Error: {e}")
        return None