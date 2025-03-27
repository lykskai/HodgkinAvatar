import os
import asyncio
from nicegui import ui
from LLM import query_rag_system
from TTS import speak  # Import the TTS functions

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
        with ui.column().style('width: 100%; display: flex; justify-content: center; align-items: center; padding-top: 200px;'):
            
            # Video Container (Visible at all times)
            self.video_container = ui.video('dorothy_longloop.mp4', 
                controls=False, autoplay=True, muted=True, loop=True
            ).props('autoplay loop').style(
                'width: 640px; height: 360px; border-radius: 50px; overflow: hidden; margin-bottom: 20px'
            )

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

        # Hide loading UI
        self.spinner.set_visibility(False)
        self.label.set_visibility(False)
        ui.update(self.spinner)
        ui.update(self.label)

        # Play TTS & generate soundwave visualization
        self.video_container.set_visibility(False)
        self.response_label.set_text(response)
        self.response_row.set_visibility(True)
        audio_element = await speak(response)

        if audio_element:
            # Estimate audio duration (you might want to make this more precise)
            audio_duration = len(response.split()) * 0.4  # rough estimate of speaking time
            
            ui.html(audio_element)
            
            # Wait for the estimated audio duration
            await asyncio.sleep(audio_duration)

        # Show video container after estimated speaking time. Hide caption container.
        self.video_container.set_visibility(True)
        self.response_row.set_visibility(False)

    def call_rag(self, user_input): 
        """Calls the LLM model asynchronously."""
        return query_rag_system(user_input)

def main():
    """Initializes the chatbot and runs the NiceGUI app."""
    if not os.path.exists('dorothy_longloop.mp4'):
        print("Warning: dorothy_longloop.mp4 not found.")

    DorothyChatbot()
    ui.run(title='Alchemist', dark=True, port=8080)

if __name__ in {"__main__", "__mp_main__"}:  
    main()
