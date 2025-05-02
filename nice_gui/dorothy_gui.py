import os
import asyncio
import time 
import random
from nicegui import ui
from LLM import query_rag_system                                                # Communicate to LLM
from TTS import speak                                                           # Get the audio file
from helper import extract_response_and_mood                                    # Get response and mood from LLM
from helper import select_images_for_input, build_filename_keyword_index        # Get the images based on keyword match
from nicegui.events import KeyEventArguments                                    # Keyboard listener
from static import IMAGE_CAPTIONS, FIRST_ACCESS_BUFFER, BUFFER                  # Static lists for captions and buffer statements


# --------------- Chat Page UI ---------------
class DorothyChatbot:
    """
    Sets up the NiceGUI chatbot with TTS, image and video retrieval.
    """
    
    def __init__(self):
        """ 
        Initializes the chatbot UI and the flags needed for logic

        Parameters/Returns: 
            - None 
        """
        self.setup_ui()                         # calls the ui setup method 
        self.is_processing = False              # flag to set if we are in processing input or not 
        self.is_first_access = True             # flag to deal with issues with really long wait time when first access. 

    def setup_ui(self):
        """
        Sets up the UI for the chat page. 

        Parameters/Returns: 
            - None 
        """

        # Hidden button for keyboard listening 
        self.hidden_button = ui.button('', on_click=lambda: asyncio.create_task(self.process_input())).style('display: none')

        # Global styles
        ui.colors(primary='#A1DAD7')            # blue colour 
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

            /* Bubble fade-in animation */
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

            /* Animated typing dots */
            .dot-loader {
                display: flex;
                gap: 6px;
                padding: 10px 14px;
                background-color: #A1DAD7;
                border-radius: 16px;
                max-width: fit-content;
                animation: fadeZoomIn 0.6s ease-out;
            }
            .dot-loader span {
                width: 8px;
                height: 8px;
                background-color: black;
                border-radius: 50%;
                animation: dotFlashing 1s infinite linear alternate;
            }
            .dot-loader span:nth-child(2) {
                animation-delay: 0.2s;
            }
            .dot-loader span:nth-child(3) {
                animation-delay: 0.4s;
            }
            @keyframes dotFlashing {
                0% { opacity: 0.2; }
                50%, 100% { opacity: 1; }
            }
            </style>
            ''')

        # Get all the image files; used later
        self.image_files = [
            f for f in os.listdir('static') 
            if f.endswith('.jpg') or f.endswith('.png')
        ]

        # Get all the image keywords; used later
        self.filename_keywords = build_filename_keyword_index(self.image_files)

        # Minimalist gray navbar
        with ui.row().classes('w-full h-16 fixed top-0 left-0 z-50 bg-[#1f1f1f] px-6 items-center justify-start border-b border-gray-700'):
            ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to('/')).props('flat dense round').classes(
                'text-white hover:text-gray-300 text-base'
            )
            ui.label('AI/Chemist').classes('ml-3 text-white font-[Helvetica] text-lg ')

        # Main container to center everything on the page: has everything except for the navbar.
        with ui.column().classes('w-full items-center justify-center').style('min-height: 100vh; padding-top: 40px; padding-bottom: 40px;'):
            with ui.row().classes('w-full justify-center gap-12').style('height: 100%; align-items: center;'):

                # === LEFT: VIDEO COLUMN [IDLE AND RESPONSE STAGE] ===
                with ui.column().classes('items-center justify-center').style('''
                    flex: 1 1 300px;
                    min-width: 300px;
                    max-width: 640px;
                '''):

                    # IDLE CAROUSEL 
                    self.idle_carousel_wrapper = ui.column().classes('items-center').style('''
                        width: 90%;
                        max-width: 640px;
                        aspect-ratio: 12 / 9;
                        border-radius: 5px;
                        overflow: hidden;
                    ''')

                    self.show_carousel()

                    # RESPONSE CONTAINER

                    with ui.column().classes('items-center justify-center').style('width: 100%; gap: 16px; padding-top: 20px') as self.response_visual_container:

                        # Video (top)
                        self.emotion_video = ui.video('static/dorothy_longloop.mp4',
                            controls=False, autoplay=True, muted=True, loop=True
                        ).props('autoplay loop').classes('video-frame-glow').style('''
                            width: 70%;
                            max-width: 640px;
                            aspect-ratio: 16 / 9;
                            border-radius: 5px;
                            overflow: hidden;
                        ''')

                        # Carousel (bottom)
                        self.emotion_carousel_wrapper = ui.column().classes('items-center').style('''
                            width: 70%;
                            max-width: 640px;
                            aspect-ratio: 12 / 9;
                            border-radius: 5px;
                            overflow: hidden;
                        ''')
                        self.emotion_carousel_wrapper.set_visibility(False)


                    # Hide whole thing by default
                    self.response_visual_container.set_visibility(False)

                # === RIGHT: CHAT COLUMN ===
                with ui.column().classes('justify-start').style('''
                    flex: 1 1 300px;
                    min-width: 300px;
                    max-width: 640px;
                '''):

                    # Chat history box 
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

                    # Add label when its empty: "Chat with Dorothy"
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

                        # Add zoom in animation to label above
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

                    # User input box and send button code
                    with ui.row().classes('items-center gap-4').style('width: 100%; padding: 10px;'):
                        # Container that takes 85% of the space
                        with ui.element('div').style('flex: 1 1 85%;'):
                            self.input = ui.textarea(placeholder='Type your message...') \
                                .props('autogrow filled') \
                                .style('''
                                    width: 100%;
                                    min-height: 60px;
                                    max-height: 180px;
                                    background-color: var(--light-gray);
                                    color: white;
                                    border-radius: 10px;
                                    font-family: Helvetica, sans-serif;
                                    resize: none;
                                    overflow-y: auto;
                                ''')
                            
                            # Keyboard listener
                            ui.add_body_html('''
                            <script>
                            document.addEventListener('DOMContentLoaded', () => {
                                const textarea = document.querySelector('textarea');
                                if (textarea) {
                                    textarea.addEventListener('keydown', function(e) {
                                        if (e.key === 'Enter' && !e.shiftKey) {
                                            e.preventDefault();
                                            document.querySelector('button[style*="display: none"]').click();
                                        }
                                    });
                                }
                            });
                            </script>
                            ''')

                        # Send button: fixed size, doesn’t shrink
                        ui.button(icon='send', color='primary', on_click=self.process_input).style(
                            '''
                            flex: 0 0 50px;
                            width: 50px;
                            height: 50px;
                            border-radius: 20px;
                            '''
                        )

        
    # ========== HELPER METHODS FOR CHAT PAGE UI ==========

    # 1) Case: In response state; carousel is playing
    def show_response_carousel(self, user_input: str):
        """
        Displays a carousel of images relevant to the user input during response stage.
        Response stage is when we are processing user input. 

        Parameters: 
            - user input (string): used for keyword matching with the images for the carousel. 

        Returns: 
            - None 
        """
        # Get the images using a helper function 
        selected_images = select_images_for_input(user_input, self.image_files, self.filename_keywords)

        # Show the response carousel! 
        self.emotion_carousel_wrapper.clear()
        self.emotion_carousel_wrapper.set_visibility(True)

        # Update the carousel components 
        with self.emotion_carousel_wrapper:
            with ui.carousel(animated=True, arrows=True).props(
                'cycle autoplay interval=9000 height=100%'
            ).style('width: 100%; max-width: 600px; border-radius: 10px; overflow: hidden;'):
                for image in selected_images:
                    with ui.carousel_slide().classes('p-0'):
                        with ui.column().classes('w-full h-full items-center'):
                            ui.image(f'static/{image}').classes('w-full h-full object-cover')
                            ui.label(IMAGE_CAPTIONS.get(image, "Untitled Image")).classes(
                                'text-white text-sm mt-2 text-center font-[Helvetica]' )
                            
    #2) Case: In idle state; idle carousel is playing
    def show_carousel(self):
            """
            Rebuilds the carousel dynamically with new random images and shows to user. 

            Parameters/Returns: 
                - None 
            """

            # Show the idle carousel wrapper 
            self.idle_carousel_wrapper.clear()
            self.idle_carousel_wrapper.set_visibility(True)

            # Get the random images 
            random_images = random.sample(self.image_files, 5)   # Get 5 images

            # Show the carousel with the adjustments and style 
            with self.idle_carousel_wrapper:
                with ui.carousel(animated=True, arrows=True).props(
                    'cycle autoplay interval=9000 height=100%'
                ).style('width: 100%; max-width: 600px; border-radius: 10px; overflow: hidden;'):
                    for image in random_images:
                        with ui.carousel_slide().classes('p-0'):
                            with ui.column().classes('w-full h-full items-center'):
                                ui.image(f'static/{image}').classes('w-full h-full object-cover')
                                ui.label(IMAGE_CAPTIONS.get(image, "Untitled Image")).classes(
                                    'text-white text-sm mt-2 text-center font-[Helvetica]'
                                )

    # 3) Case: We are processing user input. 
    async def process_input(self):
        """
        Handles user input, calls LLM, plays TTS, and updates UI.

        Parameters/Returns: 
            - None 
        """
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

        # Delete label within chat history since not empty anymore 
        if self.chat_placeholder is not None:
            self.chat_placeholder.delete()          # remove placeholder if it's still there
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
        self.is_processing = True                       # stops overlap in input   

        # ii) Let Dorothy add to the chatbot a deadtime buffer. 

        # - Get the response, randomized.
        if self.is_first_access:                        # first time accessing - much slower than later responses.
            buffer_response = random.choice(FIRST_ACCESS_BUFFER)
        else: # already accessed
            buffer_response = random.choice(BUFFER)     # random buffer_response 

        # - Show her buffer response in chat history
        with self.chat_history:
            with ui.row().classes('justify-start w-full'):
                ui.label(buffer_response).style('''
                    background-color: #A1DAD7;
                    color: black;
                    padding: 10px 14px;
                    border-radius: 16px;
                    max-width: 70%;
                    font-family: Helvetica, sans-serif;
                ''')

        # - Play audio! 
        audio_element = await speak(buffer_response)

        # - Don't do anything until audio is finished playing - except for loading the bubbles for UI loading! 
        if audio_element:
            # Estimate audio duration
            audio_duration = len(buffer_response.split()) * 0.41  # 2.4 words/second
            
            with self.chat_history:
                ui.html(audio_element)

            # Wait for the estimated audio duration
            await asyncio.sleep(audio_duration)

            # After buffer_response is shown and audio is playing...
            with self.chat_history:
                with ui.row().classes('justify-start w-full') as self.loading_bubble:
                    ui.html('''
                    <div class="dot-loader">
                        <span></span><span></span><span></span>
                    </div>
                    ''')

        # --- CALL LLM ----
        response = await asyncio.to_thread(self.call_rag, user_input)

        # Extract response and mood 
        response, mood =extract_response_and_mood(response)

        # Remove bubble just before showing LLM response
        if self.loading_bubble:
            self.loading_bubble.delete()
            self.loading_bubble = None


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

         # iv) Hide idle carousel 
        self.idle_carousel_wrapper.set_visibility(False) # hide carousel 

        # UI UPDATE: Emotion of the video! 
        try:
            if mood is not None: 

                self.emotion_video.set_source(f'static/{mood}.mp4') 
            else: 
                self.emotion_video.set_source('static/dorothy_longloop.mp4') # neutral

        except Exception as e: 

            print(f"Error: {e}")

        # --- RESPONSE STAGE UI CHANGE! ---
        # Play TTS, emotion video, & generate captions
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
            
            with self.chat_history:
                ui.html(audio_element)
            
            # Wait for the estimated audio duration
            await asyncio.sleep(audio_duration)

        # --- TRANSITION: Response stage -> idle stage --- # 

        # i ) Hide all the response stage elements
        self.response_visual_container.set_visibility(False)

        # ii) Reset processing flags - this allows us to set carousel! 
        self.is_processing = False
        self.last_processed_time = time.time()  

        # iii) Show the idle carousel again
        self.idle_carousel_wrapper.set_visibility(True)
        self.show_carousel()

        # iv) Update flag - has accessed for one time now! 
        self.is_first_access = False

    
    # 4) Calls query_rag_system. Mainly made for name
    def call_rag(self, user_input): 
        """Calls the LLM model asynchronously."""
        return query_rag_system(user_input)
    
# --------------- MAIN Page UI ---------------
@ui.page('/')
def main_page():
    """ 
    Logic for the main page UI 

    Parameters/Returns: 
        - None
    """
    # Use AOS for animations when scrolling, smooth for pressing the hyperlinks in the navbar
    ui.add_head_html('''
                     
        <style>
    .dot-loader {
        display: flex;
        gap: 6px;
        padding: 10px 14px;
        background-color: #A1DAD7;
        border-radius: 16px;
        max-width: fit-content;
        animation: fadeZoomIn 0.6s ease-out;
    }
    .dot-loader span {
        width: 8px;
        height: 8px;
        background-color: black;
        border-radius: 50%;
        animation: dotFlashing 1s infinite linear alternate;
    }
    .dot-loader span:nth-child(2) {
        animation-delay: 0.2s;
    }
    .dot-loader span:nth-child(3) {
        animation-delay: 0.4s;
    }
    @keyframes dotFlashing {
        0% { opacity: 0.2; }
        50%, 100% { opacity: 1; }
    }
    </style>

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
                ui.link('Purpose', '#Purpose').classes('text-xl text-white hover:text-gray-300 font-[Helvetica]')
    
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

    # Purpose SECTION
    with ui.row().classes('w-full justify-center items-center py-20').props('id=Purpose'):
        with ui.column().classes('w-3/4 space-y-8'):
            ui.label('Purpose').props('data-aos=fade-up').classes(
                'text-[60px] font-bold font-[Helvetica] bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent text-left leading-relaxed pb-2'
            )
            ui.label('Alchemist was created for BIOIN 401: Bioinformatics at the University of Alberta, Winter 2025 semester.').props('data-aos=fade-up').classes(
                'text-xl text-gray-300 font-[Helvetica] mt-4'
            )

# --------------- Chat Page  ---------------
@ui.page('/chat')
def chat_page():
    """
    Creates the instance of a DorothyChatbot object when we are at chat page.
    
    Parameters/Returns: 
        - None 
    """
    chatbot = DorothyChatbot()

    # Keyboard listening 
    def handle_key(event: KeyEventArguments):
        """
        Nested function    

        Parameters: 
            - event (KeyEventArguments): the keyboard events we are listening for. 
        
        Returns: 
            - None 
        """
        if event.key == 'Enter' and event.action.keydown:
            asyncio.create_task(chatbot.process_input())

    # Bind the keyboard listener inside the UI context
    ui.keyboard(on_key=handle_key)

# ---------------   Main   ---------------

def main():
    """
    Initializes the chatbot and runs the NiceGUI app.

    """
        
    if not os.path.exists('static/dorothy_longloop.mp4'):
        print("Warning: dorothy_longloop.mp4 not found!")

    DorothyChatbot()
    ui.run(title='Alchemist', dark=True, port=8080)

if __name__ in {"__main__", "__mp_main__"}:  
    main()