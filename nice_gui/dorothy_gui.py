import os
import asyncio
from nicegui import ui
from LLM import query_rag_system
from TTS import speak
from helper import extract_response_and_mood

class DorothyChatbot:
    """Sets up the NiceGUI chatbot with TTS and soundwave visualization."""
    
    def __init__(self):
        self.setup_ui()

    def setup_ui(self):
        ui.page('/')

        # Global styles
        ui.colors(primary='#A1DAD7')
        ui.add_head_html('''
        <style>
            :root {
            --light-gray: #2E2E2E;
            --dark-gray: #1E1E1E;
            --primary-color: #A1DAD7;
            }
            body, .nicegui-app, html { 
                background-color: var(--dark-gray) !important; 
                color: white;
            }
            .q-page {
                background-color: var(--dark-gray) !important;
            }
        </style>
        ''')

        # Keep everything CENTERED in the UI
        with ui.column().style('width: 100%; display: flex; justify-content: center; align-items: center; padding-top: 100px;'):
            
            # Video Container
            self.video_container = ui.video('dorothy_longloop.mp4', 
                controls=False, autoplay=True, muted=True, loop=True
            ).props('autoplay loop').style(
                'width: 640px; height: 360px; border-radius: 50px; overflow: hidden; margin-bottom: 20px'
            )

            # Video emotion-based. Default is longloop.mp4
            self.video_emotion = ui.video('dorothy_longloop.mp4', 
            controls=False, autoplay=True, muted=True, loop=True
            ).props('autoplay loop').style('position: absolute; '  # Absolute positioning inside the container
                'top: 100px; '  
                'left: 300px; '  
                'width: 150px; '  # Ensuring a perfect square
                'height: 150px; '  
                'border-radius: 50%; '  # Perfectly circular
                'overflow: hidden; '
                'object-fit: cover; '  # Ensures video fills the circular frame
                'box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3); '  # Adds a soft shadow for visibility
                'z-index: 10; '  # Ensures it appears on top of other elements
            )

            # Hide emotion video for now 
            self.video_emotion.set_visibility(False)
            
            # Response row
            with ui.row().style('width: 640px; height: 360px; border-radius: 50px; overflow: hidden; margin-bottom: 20px; background-color: transparent; border: 3px solid white; display: flex; justify-content: center; align-items: center;') as self.response_row:
                self.response_label = ui.label('').style(
                    'text-align: center; '
                    'justify-content: center; '
                    'align-items: center; '
                    'font-family: Arial, sans-serif; '
                    'font-weight: bold;'
                    'color: white; '
                    'padding: 20px; '
                    'line-height: 1.5; '
                    'font-size: 20px;'
                    'overflow-y: auto; '  # Handles overflow with scrolling
                    'max-height: 100%; '  # Ensure it doesn't exceed container height
                    'width: 100%;'  # Ensure full width within container
                )

            self.response_row.set_visibility(False)

            # The spinner and the label (shown while LLM is processing)
            self.spinner = ui.spinner(size='30px', color='primary')
            self.spinner.set_visibility(False)

            self.label = ui.label('Dorothy is thinking of a response!').style('font-size: 15px')
            self.label.set_visibility(False)

            # Chat input and button (Centered)
            with ui.row().style('width: 100%; max-width: 640px; background-color: transparent; border-radius: 20px; padding: 10px;'):
                
                # Input field
                self.input = ui.textarea(placeholder='Type here...').props('autogrow filled').style(
                    'flex-grow: 1; '
                    'background-color: var(--light-gray);' 
                    'color: white; '
                    'border-radius: 10px; '  
                    'min-height: 50px; '
                    'max-height: 150px; '
                    'font-family: Arial, sans-serif; '
                    'overflow: hidden;'
                )

                # Send button
                ui.button(icon='send', color='primary', on_click=self.process_input).style(
                    'border-radius: 20px; '
                    'width: 50px; '
                    'height: 50px; '
                    'margin: auto'
                )

    async def process_input(self):
        """Handles user input, calls LLM, plays TTS, and updates UI."""
        user_input = self.input.value
        self.input.set_value('')

        # Show loading UI
        self.spinner.set_visibility(True)
        self.label.set_visibility(True)
        ui.update(self.spinner)
        ui.update(self.label)

        # Call LLM asynchronously
        response = await asyncio.to_thread(self.call_rag, user_input)

        # Extract response and mood 
        response, mood =extract_response_and_mood(response)

        # Change the mood of video
        try:
            if mood is not None: 
                print("here error")

                self.video_emotion.set_source(f'{mood}.mp4') 
            else: 
                print("Else error")
                self.video_emotion.set_source('dorothy_longloop.mp4') # neutral

        except Exception as e: 
            print("here2 error")

            print(f"Error: {e}")

        print("TEST: response is", response,"mood is:", mood)
        # Hide loading UI
        self.spinner.set_visibility(False)
        self.label.set_visibility(False)
        ui.update(self.spinner)
        ui.update(self.label)

        # Play TTS, emotion video, & generate captions
        self.video_container.set_visibility(False)
        self.response_label.set_text(response)
        self.response_row.set_visibility(True)
        self.video_emotion.set_visibility(True)
        audio_element = await speak(response)

        if audio_element:
            # Estimate audio duration (you might want to make this more precise)
            audio_duration = len(response.split()) * 0.4  # rough estimate of speaking time
            
            ui.html(audio_element)
            
            # Wait for the estimated audio duration
            await asyncio.sleep(audio_duration)

        # Show video container after estimated speaking time. Hide caption container and emotion video
        self.video_container.set_visibility(True)
        self.response_row.set_visibility(False)
        self.video_emotion.set_visibility(False)


    def call_rag(self, user_input): 
        """Calls the LLM model asynchronously."""
        return query_rag_system(user_input)
    
    


def main():
    """Initializes the chatbot and runs the NiceGUI app."""
    if not os.path.exists('dorothy_longloop.mp4'):
        print("Warning: dorothy_longloop.mp4 not found.")
        print("yeah")

    DorothyChatbot()
    ui.run(title='Alchemist', dark=True, port=8080)

if __name__ in {"__main__", "__mp_main__"}:  
    main()