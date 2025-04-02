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
                    'font-family: Helvetica, sans-serif; '
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
                    'font-family: Helvetica, sans-serif; '
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

                self.video_emotion.set_source(f'{mood}.mp4') 
            else: 
                self.video_emotion.set_source('dorothy_longloop.mp4') # neutral

        except Exception as e: 

            print(f"Error: {e}")

        print("[DEBUG] Response is", response,"Mood is:", mood)
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
            # Estimate audio duration
            audio_duration = len(response.split()) * 0.4  # 1 word / 0.4 = 2.5 words per second
            
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
    
    
@ui.page('/')
def main_page():
    # Smooth scrolling CSS with additional fixes for the navbar issue
    ui.add_head_html('''
    <style>
    html, body {
        margin: 0;
        padding: 0;
        width: 100%;
        overflow-x: hidden;
    }
    *, *::before, *::after {
        box-sizing: border-box;
    }
    html {
        scroll-behavior: smooth;
    }
    </style>
    ''')

    # Fixed NAV BAR - properly structured
    with ui.header().classes('w-full h-16 bg-black fixed top-0 z-50 shadow'):
        with ui.row().classes('w-full h-full px-8 items-center justify-between'):
            # Logo on the left
            ui.label('AI/Chemist').classes('text-xl text-white font-bold font-[Helvetica]')
            
            # Navigation links in center
            with ui.row().classes('gap-10'):
                ui.link('Home', '#home').classes('text-xl text-white hover:text-gray-300 font-[Helvetica]')
                ui.link('About', '#about').classes('text-xl text-white hover:text-gray-300 font-[Helvetica]')
                ui.link('Demo', '#demo').classes('text-xl text-white hover:text-gray-300 font-[Helvetica]')
            
            # Contact button on right
            ui.button('Contact', on_click=lambda: ui.navigate.to('/contact')).classes(
                'bg-[#A1DAD7] text-white font-bold font-[Helvetica] px-3 py-1 rounded text-sm'
            )

    # Add spacing to account for fixed navbar
    ui.space().classes('h-16')

    # HOME SECTION
    with ui.row().classes('w-full h-[66vh] justify-center items-center').props('id=home'):
        with ui.column().classes('items-center'):
            # HEADING with gradient
            ui.label('Welcome to Alchemist').classes(
            'text-[90px] font-bold font-[Helvetica] bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent leading-none text-center'
            )
            # BODY 
            ui.label(
            "Chat with Dorothy Hodgkin — your AI science companion, inspired by the Nobel Prize-winning chemist who unlocked the structure of life's molecules."
            ).classes('text-xl text-gray-300 font-[Helvetica] text-center max-w-4xl mt-2')
            # BUTTON
            ui.button('Chat with Dorothy', on_click=lambda: ui.navigate.to('/chat')).classes(
            'bg-[#A1DAD7] text-white font-[Helvetica] px-4 py-2 rounded mt-4 normal-case'
            )

    # Divider
    ui.separator().classes('w-3/4 opacity-30 mx-auto my-8')

   # ABOUT SECTION
    with ui.row().classes('w-full justify-center py-16').props('id=about'):
        with ui.column().classes('w-3/4 space-y-8'):
            # Heading
            ui.label('About Dorothy Hodgkin').classes(
                'text-[60px] font-bold font-[Helvetica] bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent text-left leading-relaxed pb-2'
            )
            
            # Use grid instead of row for more reliable side-by-side layout
            with ui.element('div').classes('w-full grid grid-cols-3 gap-8 mx-auto items-center'):
                # Image in first column
                ui.image('static/dorothy.jpg').classes('col-span-1 w-full rounded shadow-lg')
                
                # Body text in remaining two columns
                ui.label(
                    "Dorothy Crowfoot Hodgkin was a pioneering chemist who used X-ray crystallography to reveal the "
                    "structures of essential biomolecules. Her groundbreaking discoveries included the molecular structures of penicillin, "
                    "vitamin B12, and insulin — achievements that earned her the Nobel Prize in Chemistry in 1964. Hodgkin's work bridged "
                    "the worlds of biology and chemistry, laying the foundation for modern structural biology."
                ).classes('col-span-2 text-xl text-gray-300 font-[Helvetica] leading-relaxed')

    # Divider
    ui.separator().classes('w-3/4 opacity-30 mx-auto my-8')

    # DEMO SECTION
    with ui.row().classes('w-full justify-center items-center py-20').props('id=demo'):
        with ui.column().classes('w-3/4 space-y-8'):
            ui.label('Demo').classes(
                'text-[60px] font-bold font-[Helvetica] bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent text-left leading-relaxed pb-2'
            )
            ui.label('Demo coming soon...').classes('text-xl text-gray-300 font-[Helvetica] mt-4')

@ui.page('/chat')
def chat_page():
    chatbot = DorothyChatbot()

def main():
    """Initializes the chatbot and runs the NiceGUI app."""
    if not os.path.exists('dorothy_longloop.mp4'):
        print("Warning: dorothy_longloop.mp4 not found!")

    DorothyChatbot()
    ui.run(title='Alchemist', dark=True, port=8080)

if __name__ in {"__main__", "__mp_main__"}:  
    main()