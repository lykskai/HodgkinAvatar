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
        # Minimalist gray navbar
        with ui.row().classes('w-full h-16 fixed top-0 left-0 z-50 bg-[#1f1f1f] px-6 items-center justify-start border-b border-gray-700'):
            ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to('/')).props('flat dense round').classes(
                'text-white hover:text-gray-300 text-base'
            )
            ui.label('AI/Chemist').classes('ml-3 text-white font-[Helvetica] text-lg ')



        with ui.column().classes('items-center').style(
        'width: 100%; display: flex; justify-content: center; align-items: center; padding-top: 100px;'):

            # Video container (centered as normal)
            self.video_container = ui.video('dorothy_longloop.mp4',
                controls=False, autoplay=True, muted=True, loop=True
            ).props('autoplay loop').classes('video-frame-glow').style(
                'width: 640px; height: 360px; border-radius: 50px; overflow: hidden; margin-bottom: 12px;'
            )

            # Wrapper that holds emotion video and response box, keeps layout stable
            with ui.element('div').classes('relative').style(
                'width: 640px; margin-bottom: 12px;'
            ):

                # Wrapper for emotion video, so we can hide/show it without affecting layout
                # TODO: Make this more responsive to the UI when we move it around. 
                with ui.element('div').classes('absolute').style(
                    'left: -250px; top: 0; width: 300px; height: 300px;'
                ) as self.video_emotion_wrapper:

                    self.video_emotion = ui.video('dorothy_longloop.mp4',
                    controls=False, autoplay=True, muted=True, loop=True
                ).props('autoplay loop').classes('rounded shadow-md').style(
                    'width: 200px; height: 200px; object-fit: cover; '
                    'border-radius: 16px; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);'
                )


                self.video_emotion_wrapper.style('display: none;')  # Start hidden

                # Wrapper for response bubble, lets us fully hide it from layout
                with ui.element('div').classes('w-full flex justify-center').style(
                    'margin-bottom: 12px;'
                ) as self.response_wrapper:

                    with ui.row().style(
                        'width: 640px; height: 360px; border-radius: 20px; overflow: hidden; '
                        'background-color: #1f1f1f; '  # flatter background
                        'border: 1px solid #3a3a3a; '  # subtle border
                        'display: flex; justify-content: center; align-items: center;'
                    ) as self.response_row:


                        self.response_label = ui.label('').classes('fade-in').style(
                            'text-align: center; justify-content: center; align-items: center; '
                            'font-family: Helvetica, sans-serif; color: white; '
                            'padding: 20px; line-height: 1.5; font-size: 20px; overflow-y: auto; '
                            'max-height: 100%; width: 100%;'
                        )

                self.response_wrapper.style('display: none;')  # Start hidden

            # Chat input row
            with ui.row().classes('items-center gap-4').style(
                'width: 100%; max-width: 640px; padding: 10px;'):

                # Spinner (shown only when thinking)
                self.spinner = ui.spinner(size='20px', color='primary')
                self.spinner.set_visibility(False)

                # Input field
                self.input = ui.textarea(placeholder='Type here...').props('autogrow filled').style(
                    'flex-grow: 1; background-color: var(--light-gray); color: white; border-radius: 10px; '
                    'min-height: 50px; max-height: 150px; font-family: Helvetica, sans-serif; overflow: hidden;'
                )

                # Send button
                ui.button(icon='send', color='primary', on_click=self.process_input).style(
                    'border-radius: 20px; width: 50px; height: 50px;'
                )




    async def process_input(self):
        """Handles user input, calls LLM, plays TTS, and updates UI."""
        user_input = self.input.value
        self.input.set_value('')

        # Show loading UI
        self.spinner.set_visibility(True)   

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

        # Play TTS, emotion video, & generate captions
        self.video_container.set_visibility(False)
        self.response_label.set_text(response)
        self.response_wrapper.style('display: flex;')
        self.video_emotion_wrapper.style('display: block;')
        audio_element = await speak(response)

        if audio_element:
            # Estimate audio duration
            audio_duration = len(response.split()) * 0.4  # 1 word / 0.4 = 2.5 words per second
            
            ui.html(audio_element)
            
            # Wait for the estimated audio duration
            await asyncio.sleep(audio_duration)

        # Show video container after estimated speaking time. Hide caption container and emotion video
        self.video_container.set_visibility(True)
        self.response_wrapper.style('display: none;')
        self.video_emotion_wrapper.style('display: none;')


    def call_rag(self, user_input): 
        """Calls the LLM model asynchronously."""
        return query_rag_system(user_input)
    
    
@ui.page('/')
def main_page():
    # Use AOS for animations when scrolling, smooth for pressing the hyperlinks in the navbar
    ui.add_head_html('''
    <!-- AOS: Animate On Scroll -->
    <link href="https://unpkg.com/aos@2.3.4/dist/aos.css" rel="stylesheet">
    <script src="https://unpkg.com/aos@2.3.4/dist/aos.js"></script>
    <script>
        window.addEventListener('load', () => {
            AOS.init({
                duration: 800,
                once: true,
            });
        });
    </script>
    <style>
    html, body {
        margin: 0;
        padding: 0;
        width: 100%;
        overflow-x: hidden;
        scroll-behavior: smooth;
    }
    *, *::before, *::after {
        box-sizing: border-box;
    }
    </style>
    ''')

    # NAV BAR
    with ui.header().classes('w-full h-16 bg-black fixed top-0 z-50 shadow'):
        with ui.row().classes('w-full h-full px-8 items-center justify-between'):
            ui.label('AI/Chemist').classes('text-xl text-white font-bold font-[Helvetica]')
            with ui.row().classes('gap-10'):
                ui.link('Home', '#home').classes('text-xl text-white hover:text-gray-300 font-[Helvetica]')
                ui.link('About', '#about').classes('text-xl text-white hover:text-gray-300 font-[Helvetica]')
                ui.link('Demo', '#demo').classes('text-xl text-white hover:text-gray-300 font-[Helvetica]')
            ui.button('Contact', on_click=lambda: ui.navigate.to('/contact')).classes(
                'bg-[#A1DAD7] text-white font-bold font-[Helvetica] px-3 py-1 rounded text-sm'
            )

    ui.space().classes('h-16')  # Space for fixed navbar

    # HOME SECTION
    with ui.row().classes('w-full h-[66vh] justify-center items-center').props('id=home'):
        with ui.column().classes('items-center'):
            ui.label('Welcome to Alchemist').props('data-aos=fade-down').classes(
                'text-[90px] font-bold font-[Helvetica] bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent leading-none text-center'
            )
            ui.label(
                "Chat with Dorothy Hodgkin — your AI science companion, inspired by the Nobel Prize-winning chemist who unlocked the structure of life's molecules."
            ).props('data-aos=fade-up').classes(
                'text-xl text-gray-300 font-[Helvetica] text-center max-w-4xl mt-2'
            )
            ui.button('Chat with Dorothy', on_click=lambda: ui.navigate.to('/chat')).props('data-aos=zoom-in').classes(
                'bg-[#A1DAD7] text-white font-[Helvetica] px-4 py-2 rounded mt-4 normal-case'
            )

    ui.separator().classes('w-3/4 opacity-30 mx-auto my-8')

    # ABOUT SECTION
    with ui.row().classes('w-full justify-center py-16').props('id=about'):
        with ui.column().classes('w-3/4 space-y-8'):
            ui.label('About Dorothy Hodgkin').props('data-aos=fade-up').classes(
                'text-[60px] font-bold font-[Helvetica] bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent text-left leading-relaxed pb-2'
            )
            with ui.element('div').classes('w-full grid grid-cols-3 gap-8 mx-auto items-center'):
                ui.image('static/dorothy.jpg').props('data-aos=fade-right').classes('col-span-1 w-full rounded shadow-lg')
                ui.label(
                    "Dorothy Crowfoot Hodgkin was a pioneering chemist who used X-ray crystallography to reveal the "
                    "structures of essential biomolecules. Her groundbreaking discoveries included the molecular structures of penicillin, "
                    "vitamin B12, and insulin — achievements that earned her the Nobel Prize in Chemistry in 1964. Hodgkin's work bridged "
                    "the worlds of biology and chemistry, laying the foundation for modern structural biology."
                ).props('data-aos=fade-left').classes(
                    'col-span-2 text-xl text-gray-300 font-[Helvetica] leading-relaxed'
                )

    ui.separator().classes('w-3/4 opacity-30 mx-auto my-8')

    # DEMO SECTION
    with ui.row().classes('w-full justify-center items-center py-20').props('id=demo'):
        with ui.column().classes('w-3/4 space-y-8'):
            ui.label('Demo').props('data-aos=fade-up').classes(
                'text-[60px] font-bold font-[Helvetica] bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent text-left leading-relaxed pb-2'
            )
            ui.label('Demo coming soon...').props('data-aos=fade-up').classes(
                'text-xl text-gray-300 font-[Helvetica] mt-4'
            )


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