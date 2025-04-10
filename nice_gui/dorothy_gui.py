import os
import asyncio
from nicegui import ui
from LLM import query_rag_system                # Communicate to LLM
from TTS import speak                           # Get the audio file
from helper import extract_response_and_mood    # Get response and mood from LLM
import time 
import random
from helper import select_images_for_input      # Get the images based on keyword match

# --------------- Chat Page UI ---------------
class DorothyChatbot:
    """Sets up the NiceGUI chatbot with TTS and soundwave visualization."""
    
    def __init__(self):
        self.setup_ui()
        self.is_processing = False              # flag to set if we are in processing input or not 
        self.is_idle = False                    # flag to set if user is idle- handles video to photo slide transition
        self.last_processed_time = time.time()
        self.start_idle_timer()


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

        # Main container to center everything on the page
        with ui.column().classes('w-full items-center justify-center').style('min-height: 100vh; padding-top: 40px; padding-bottom: 40px;'):
                            
            with ui.row().classes('w-full justify-center gap-12').style('height: 100%; align-items: center;'):

                # === LEFT: VIDEO COLUMN [IDLE AND RESPONSE STAGE] ===
                with ui.column().classes('items-center justify-center').style('''
                    flex: 1 1 300px;
                    min-width: 300px;
                    max-width: 640px;
                '''):

                    # IDLE VIDEO (Shown in idle stage)
                    self.idle_video_container = ui.video('static/dorothy_longloop.mp4',
                        controls=False, autoplay=True, muted=True, loop=True
                    ).props('autoplay loop').classes('video-frame-glow').style('''
                        width: 100%;
                        height: 360px;
                        border-radius: 50px;
                        overflow: hidden;
                    ''')

                    # IDLE CAROUSEL 
                    self.idle_carousel_wrapper = ui.column().classes('items-center')
                    self.idle_carousel_wrapper.set_visibility(False)


                    with ui.column().classes('items-center').style('width: 100%;') as self.response_visual_container:

                        self.emotion_video = ui.video('static/dorothy_longloop.mp4',
                            controls=False, autoplay=True, muted=True, loop=True
                        ).props('autoplay loop').classes('video-frame-glow').style('''
                            width: 80%;
                            height: 60%;
                            border-radius: 50px;
                            overflow: hidden;
                            margin-bottom: 12px;
                        ''')

                        self.emotion_carousel_wrapper = ui.column().classes('items-center').style('''
                                height: 50%;
                                width: 80%;
                                border-radius: 30px;
                                overflow: hidden;
                                margin-top: 5px;
                            ''')
                        self.emotion_carousel_wrapper.set_visibility(False)

                    # hide whole thing by default
                    self.response_visual_container.set_visibility(False)



                # === RIGHT: CHAT COLUMN ===
                with ui.column().classes('justify-start').style('''
                    flex: 1 1 300px;
                    min-width: 300px;
                    max-width: 640px;
                '''):

                    self.chat_history = ui.column().style('''
                        height: 70vh;
                        width: 100%;
                        overflow-y: auto;
                        background-color: #1f1f1f;
                        border-radius: 16px;
                        padding: 16px;
                        margin-bottom: 12px;
                        border: 1px solid #3a3a3a;
                        font-family: Helvetica, sans-serif;
                        gap: 12px;
                    ''')

                    # Add label when its empty
                    with self.chat_history:
                        self.chat_placeholder = ui.label('Chat with Dorothy!').classes(
                            'font-bold font-[Helvetica]'
                        ).style('''
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            height: 100%;
                            width: 100%;
                            text-align: center;
                            font-size: 32px;
                            background: linear-gradient(to right, #A1DAD7, #ffffff);
                            -webkit-background-clip: text;
                            -webkit-text-fill-color: transparent;
                            animation: fadeZoomIn 1.5s ease-out;
                        ''')

                        # Add zoom in animation to label 
                        ui.add_head_html('''
                        <style>
                            @keyframes fadeZoomIn {
                                0% {
                                    opacity: 0;
                                    transform: scale(0.95);
                                }
                                100% {
                                    opacity: 1;
                                    transform: scale(1);
                                }
                            }
                        </style>
                        ''')

                    # Below is the code for user input box, send button, and the spinner

                    with ui.row().classes('items-center gap-4').style('width: 100%; padding: 10px;'):
                        # i) Spinner - hidden as default
                        self.spinner = ui.spinner(size='30px', color='primary')
                        self.spinner.set_visibility(False)
                        # ii) Input text box
                        self.input = ui.textarea(placeholder='Type your message...').props('autogrow filled').style('''
                            flex-grow: 1;
                            background-color: var(--light-gray);
                            color: white;
                            border-radius: 10px;
                            min-height: 50px;
                            max-height: 100px;
                            font-family: Helvetica, sans-serif;
                            overflow: hidden;
                        ''')
                        # iii) Send button
                        ui.button(icon='send', color='primary', on_click=self.process_input).style(
                            'border-radius: 20px; width: 50px; height: 50px;'
                        )

                
                # Below is a handler for user movement (clicking) to stop idle state! Add it only when idle! 
                with ui.element('div').classes('absolute top-0 left-0 w-full h-full z-50').style('cursor: pointer;') as self.touch_overlay:
                    self.touch_overlay.on('click', self.user_interacted)
                    self.touch_overlay.on('touchstart', self.user_interacted)

                
                self.touch_overlay.set_visibility(False)        # hidden as default

                # Get all the image files; used later
                self.image_files = [
                    f for f in os.listdir('static') 
                    if f.endswith('.jpg') or f.endswith('.png')
                ]

        
# HELPER FUNCTIONS for chat page UI

    # 1) Case: Exit idle state of carousel playing
    def user_interacted(self, _=None):
        """Handles any user tap/click to exit idle mode early."""
        print("[DEBUG] User touched screen — exiting idle mode early.")
        self.last_processed_time = time.time()
        self.is_idle = False
        self.idle_carousel_wrapper.set_visibility(False)
        self.idle_video_container.set_visibility(True)

    #2) Case: In response state; carousel is playing
    def show_response_carousel(self, user_input: str):
        """Displays a carousel of images relevant to the user input during response stage."""
        selected_images = select_images_for_input(user_input, self.image_files)

        for image in selected_images: 
            print(f"[DEBUG- CAROUSEL]: {image}")
        self.emotion_carousel_wrapper.clear()
        self.emotion_carousel_wrapper.set_visibility(True)

        with self.emotion_carousel_wrapper:
            with ui.carousel(animated=True, arrows=True, navigation=True).props(
                'cycle autoplay interval=7000 height=360px'
            ).style(
                'width: 640px; border-radius: 50px; overflow: hidden; margin-bottom: 12px;'
            ):
                for image in selected_images:
                    with ui.carousel_slide().classes('p-0'):
                        ui.image(f'static/{image}').classes('w-full h-full object-cover')

    #3) Case: In idle state; idle carousel is playing
    def show_carousel(self):
            """Rebuilds the carousel dynamically with new random images and shows it."""
            self.idle_carousel_wrapper.clear()
            self.idle_carousel_wrapper.set_visibility(True)
            self.idle_video_container.set_visibility(False)

            image_files = [
                f for f in os.listdir('static')
                if f.endswith('.jpg') and ('PERSONAL' in f or 'CASUAL' in f)
            ]
            random_images = random.sample(image_files, 3)

            with self.idle_carousel_wrapper:
                with ui.carousel(animated=True, arrows=True, navigation=True).props('cycle autoplay interval=7000 height=360px').style(
                    'width: 640px; border-radius: 50px; overflow: hidden; margin-bottom: 12px;'
                ):
                    for image in random_images:
                        with ui.carousel_slide().classes('p-0'):
                            ui.image(f'static/{image}').classes('w-full h-full object-cover')

            self.touch_overlay.set_visibility(True)                     # Turn on event handler

    # 4) Case: We are processing user input. 
    async def process_input(self):
        """Handles user input, calls LLM, plays TTS, and updates UI."""
        if  self.is_processing: 
            # We are still processing a previous request. Leave and let user know.
            ui.notify(
                    "A previous request is still being processed. Please wait a moment before trying again.",
                    position="bottom-left")

            # Leave
            return
        
        start_time = time.time()                    # For debug
        print(f"[DEBUG]: Just received user input. Time: {start_time}")

        # --- Response stage, processing --- 

        # 1) Extract user input!
        user_input = self.input.value   
        self.input.set_value('')                    # clears self.input for ui 

        # -- Delete label within chat history since not empty anymore
        # Remove placeholder if it's still there
        if self.chat_placeholder is not None:
            self.chat_placeholder.delete()
            self.chat_placeholder = None

        # 2) Display user's message in the chat history
        with self.chat_history:
            with ui.row().classes('justify-end w-full'):
                ui.label(user_input).style('''
                    background-color: #3a3a3a;
                    color: white;
                    padding: 10px 14px;
                    border-radius: 16px;
                    max-width: 70%;
                    font-family: Helvetica, sans-serif;
                ''')


        # 3) Show loading UI

        # i) Set flags
        self.is_processing = True                   # flag to communicate with the timer for carousel - also stops overlap in input

        # ii) Set spinner
        self.spinner.set_visibility(True)          

        # iii) Hide idle carousel - extra step to ensure it will not show!
        self.idle_carousel_wrapper.set_visibility(False) # hide carousel 
        self.idle_video_container.set_visibility(True)   # show video, for now

        # --- CALL LLM ----
        response = await asyncio.to_thread(self.call_rag, user_input)

        # Extract response and mood 
        response, mood =extract_response_and_mood(response)

        # UI UPDATE: Add response to chatbot! 
        with self.chat_history:
            with ui.row().classes('justify-start w-full'):
                ui.label(response).style('''
                    background-color: #A1DAD7;
                    color: black;
                    padding: 10px 14px;
                    border-radius: 16px;
                    max-width: 70%;
                    font-family: Helvetica, sans-serif;
                ''')

        # UI UPDATE: Emotion of the video! 
        try:
            if mood is not None: 

                self.emotion_video.set_source(f'static/{mood}.mp4') 
            else: 
                self.emotion_video.set_source('static/dorothy_longloop.mp4') # neutral

        except Exception as e: 

            print(f"Error: {e}")

        print("[DEBUG] Response is", response,"Mood is:", mood)

        # Hide loading UI
        self.spinner.set_visibility(False)  

        # --- RESPONSE STAGE UI CHANGE! ---
        # Play TTS, emotion video, & generate captions
        self.idle_video_container.set_visibility(False)             # hide idle video 
        self.response_visual_container.set_visibility(True)            # show wrapper
        self.show_response_carousel(user_input)                     # show response carousel
        self.emotion_video.set_visibility(True)                     # show emotion video
        print(f"[DEBUG]: Just showed user output. Total time:{time.time() - start_time}")

        # Play audio! 
        audio_element = await speak(response)

        # Don't do anything until audio is finished playing. 
        if audio_element:
            # Estimate audio duration
            audio_duration = len(response.split()) * 0.41  # 2.4 words/second
            
            ui.html(audio_element)
            
            # Wait for the estimated audio duration
            await asyncio.sleep(audio_duration)

        # --- TRANSITION: Response stage -> idle stage --- # 

        # i ) Hide all the response stage elements
        self.response_visual_container.set_visibility(False)


        # ii) Show idle video. Another function handles the showing of idle carousel 
        self.idle_video_container.set_visibility(True)
               

        # iii) Reset processing flags - this allows us to set carousel! 
        self.is_processing = False
        self.last_processed_time = time.time()  
    
    # 5) Case: reset the timer when exiting idle state.
    def reset_idle_timer(self):
        """Call this whenever the user interacts."""
        self.last_input_time = time.time()
    
    # 6) Case: start the timer and show idle carousel. Entering idle state.
    def start_idle_timer(self):
        """Launches a repeating timer to check if chatbot has been idle."""
        async def check_idle():
            while True:
                await asyncio.sleep(1)

                if self.is_processing:
                    # Are we processing? then reset loop until we aren't processing anymore
                    self.last_processed_time = time.time()
                    continue

                idle_duration = time.time() - self.last_processed_time
                if idle_duration >= 10:     # if we have been idle for more than 10 seconds
                    if not self.is_idle:   
                        # Only rebuild and show the carousel once when entering idle state
                        self.show_carousel()                        # show the photo

                    self.is_idle = True

                    self.idle_video_container.set_visibility(False)      # hide the video
                else:
                    # When user presses the screen, we go back to video!
                    self.touch_overlay.set_visibility(False)               # hidden; can access input
                    self.is_idle = False
                    self.idle_carousel_wrapper.set_visibility(False)
                    self.idle_video_container.set_visibility(True)

        # Nested function to queue up second countdown since idle.
        def start_async_task():
            asyncio.create_task(check_idle())

        # Use ui.timer to launch the async check safely once
        ui.timer(0.1, start_async_task, once=True)

    # 7) Calls query_rag_system. Mainly made for name
    def call_rag(self, user_input): 
        """Calls the LLM model asynchronously."""
        return query_rag_system(user_input)
    
# --------------- MAIN Page UI ---------------
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
                # Image
                ui.image('static/CASUAL_LAB_Dorothy.jpg') \
                    .props('data-aos=fade-right') \
                    .classes('col-span-1 w-full rounded-lg shadow-lg')
                # Text
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

# --------------- Chat Page  ---------------
@ui.page('/chat')
def chat_page():
    "Creates the instance of a DorothyChatbot object when we are at chat page."
    chatbot = DorothyChatbot()

# --------------- Main   ---------------

def main():
    """Initializes the chatbot and runs the NiceGUI app."""
    if not os.path.exists('static/dorothy_longloop.mp4'):
        print("Warning: dorothy_longloop.mp4 not found!")

    DorothyChatbot()
    ui.run(title='Alchemist', dark=True, port=8080)

if __name__ in {"__main__", "__mp_main__"}:  
    main()