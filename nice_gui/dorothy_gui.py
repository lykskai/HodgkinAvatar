import os # used to check if required video file exists; could change to non-local storage
from nicegui import ui # to create the ui
from LLM import query_rag_system
import asyncio  # Import asyncio for async processing

class DorothyChatbot:
    """ 
    Sets up the class for our chatbot and its attributes 
    """
    def __init__(self):
        # Setup the main app layout
        self.setup_ui()

    def setup_ui(self):
        # Define the main page
        ui.page('/')

        # Set global styles
        ui.colors(primary='#A1DAD7')  # this color is light blue
        
        # Apply global CSS styles
        ui.add_head_html('''
        <style>
            /* Define the global colors */
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

        # Logic for handling the video UI: Video Container
        with ui.column().style('width: 100%; display: flex; justify-content: center; align-items: center; padding-top: 50px;'):
            # Video placeholder (visible at all times)
            self.video_container = ui.video('dorothy_longloop.mp4', 
                controls=False, autoplay=True, muted=True, loop=True
                ).props('autoplay loop').style(
                'width: 640px; height: 360px; border-radius: 50px; overflow: hidden; margin-bottom: 20px'
            )

            # Logic for audio UI soundwave, placeholder 
            self.visualizer = ui.markdown('').style('display: none;')

            # The spinner and the label (shown during LLM processing)
            self.spinner = ui.spinner(size='30px', color='primary')
            self.spinner.set_visibility(False)  # Hidden by default

            self.label = ui.label('Dorothy is thinking of a response!').style('font-family: Helvetica-bold, sans-serif; font-size: 15px') 
            self.label.set_visibility(False)    # Hidden by default

            # Logic for chatting: our button and our input text
            with ui.row().style('width: 100%; max-width: 640px; background-color: transparent; border-radius: 20px; padding: 10px;'):
                # Dynamic text input
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

                
                # Send button. When pressed, we process the input.
                ui.button(icon='send', color='primary', on_click=self.process_input).props('text-color=black').style(
                'border-radius: 20px; '
                'width: 50px; '
                'height: 50px; '
                'margin: auto'
                )

    async def process_input(self):
        """ 
        Process user input in sequential steps
        """
        user_input = self.input.value

        # Clear input box
        self.input.set_value('')

        # Step 1: **Show loading UI elements (spinner & label, but keep video visible)**
        self.spinner.set_visibility(True)
        self.label.set_visibility(True)

        # **Force UI updates**
        ui.update(self.spinner)
        ui.update(self.label)

        # Step 2: **Call LLM in Background**
        response = await asyncio.to_thread(self.call_rag, user_input)

        # Step 3: **Hide loading UI after response**
        self.spinner.set_visibility(False)
        self.label.set_visibility(False)

        # **Force UI updates**
        ui.update(self.spinner)
        ui.update(self.label)

        # Print response (or display it in the UI)
        print(response)

    def call_rag(self, user_input): 
        """ Calls the LLM model in a separate thread to avoid UI blocking """
        return query_rag_system(user_input)

def main():
    """ 
    Program logic
    """
    # Ensure video file exists
    if not os.path.exists('dorothy_longloop.mp4'):
        print("Warning: dorothy_longloop.mp4 not found. Ensure the video file is in the same directory.")

    # Initialize the chatbot
    DorothyChatbot()

    # Run the NiceGUI app
    ui.run(title='Dorothy Chatbot', dark=True, port=8080)

if __name__ in {"__main__", "__mp_main__"}:  
    # Run the program
    main()
