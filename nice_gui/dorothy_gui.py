"""
This file handles the UI logic for the Alchemist chatbot.
""" 
import os
import sys
from nicegui import ui
import time

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
        
        # Add background color (dark gray), set text color to white
        ui.add_head_html('''
        <style>
            /* Define the global colors*/
            :root {
            --light-gray: #2E2E2E;
            --dark-gray: #1E1E1E;
            --primary-color: #A1DAD7;
            }
            body, .nicegui-app, html { 
                background-color: --dark-gray !important; 
                color: white;
            }
            .q-page {
                background-color: --dark-gray !important;
            }
        </style>
        ''')

        # Video/Avatar Container
        with ui.column().style('width: 100%; display: flex; justify-content: center; align-items: center; padding-top: 50px;'):
            # Video placeholder
            self.video_container = ui.video('dorothy_idle.mp4').style(
                'width: 640px; height: 360px; border-radius: 50px; overflow: hidden;'
            )
            
            # Audio Visualizer (placeholder)
            self.visualizer = ui.markdown('').style('display: none;')

            # Input Container- our button and our input text
            with ui.row().style('width: 100%; max-width: 640px; background-color: transparent; border-radius: 20px; padding: 10px; margin-top: 20px;'):
                # Dynamic text input
                self.input = ui.textarea(placeholder='Type here...').props('autogrow filled').style(
                    'flex-grow: 1; '
                    'background-color: --light-gray; /* light gray */  ' 
                    'color: white; '
                    'border-radius: 10px; '  
                    'min-height: 50px; '
                    'max-height: 150px; '
                    'font-family: Arial, sans-serif; '
                    'overflow: hidden;'
                )

                # Send button
                ui.button(icon='send', color='primary', on_click=self.process_input).props('text-color=black').style(
                'border-radius: 20px; '
                'width: 50px; '
                'height: 50px; '
                'margin: auto'
                )


    def process_input(self):
        """ 
        Process user input
        """
        user_input = self.input.value
        
        # Clear input
        self.input.value = ''
        
        # Hide video, show placeholder for audio visualization
        self.video_container.style('display: none;')
        self.visualizer.style('display: block;')
        
        # Simulate return to video after processing
        ui.timer(3, self.restore_video)

    def restore_video(self):
        self.video_container.style('display: block;')
        self.visualizer.style('display: none;')

def main():
    """ 
    Program logic
    """
    # Ensure video file exists
    if not os.path.exists('dorothy_idle.mp4'):
        print("Warning: dorothy_idle.mp4 not found. Ensure the video file is in the same directory.")

    # Initialize the chatbot
    DorothyChatbot()

    # Run the NiceGUI app
    ui.run(title='Dorothy Chatbot', dark=True, port=8080)

if __name__ in {"__main__", "__mp_main__"}:  
    # Run the program 
    main()