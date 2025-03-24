import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QSizePolicy
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtCore import QUrl

import pyqtgraph as pg

class DynamicTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set size policy to allow expanding
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        # Set fixed initial height
        self.setFixedHeight(50)
        self.setMinimumHeight(50)
        self.setMaximumHeight(150)  # Changed max height to 150
        
        # Styling
        self.setFont(QFont("Arial", 14))
        self.setPlaceholderText("Type here...")
        self.setStyleSheet("""
    QTextEdit {
        border-radius: 15px; 
        padding: 10px; 
        background-color: #555555
        color: black;
    }
""")
        
        # Enable vertical scrollbar when content exceeds max height
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Connect textChanged signal to adjust height
        self.textChanged.connect(self.adjust_height)

    def adjust_height(self):
        # Get the document's size hint
        doc_height = self.document().size().height()
        
        # Calculate the height, ensuring it doesn't start too large
        new_height = min(max(doc_height + 20, 50), 150)
        
        # Always update height to match content
        self.setFixedHeight(int(new_height))

class ChatbotApp(QWidget):
    def loop_video(self):
        """Loops the video when it ends."""
        if self.player.position() >= self.player.duration() - 500:
            self.player.setPosition(0)
            self.player.setLoops(QMediaPlayer.Loops.Infinite)
        self.player.play()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize the UI components."""
        self.setWindowTitle("Dorothy Chatbot")
        self.showFullScreen()  # Makes the app take the entire screen
        
        self.setStyleSheet("background-color: #333333;")  # Dark gray background
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Video Widget for Dorothy's Idle Animation
        self.video_widget = QVideoWidget(self)
        self.video_widget.setFixedSize(600, 400)  # Adjust width and height as needed
        self.video_widget.setStyleSheet("border-radius: 20px; overflow: hidden;")
        self.player = QMediaPlayer()
        self.player.setVideoOutput(self.video_widget)
        self.player.setSource(QUrl.fromLocalFile("dorothy_idle.mp4"))
        self.player.play()
        
        self.loop_timer = QTimer()
        self.loop_timer.timeout.connect(self.loop_video)
        self.loop_timer.start(1000)  # Check every second to ensure smooth looping
        
        # Audio Visualizer (Hidden by Default)
        self.visualizer = pg.PlotWidget(self)
        self.visualizer.setYRange(-1, 1)
        self.waveform = self.visualizer.plot(pen='g')
        self.visualizer.hide()
        
        # Create a container widget for input layout
        self.input_container = QWidget(self)
        self.input_container.setStyleSheet("background-color: #555555; border-radius: 20px;")
        self.input_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Create a container widget for input layout
        self.input_container = QWidget(self)
        self.input_container.setStyleSheet("background-color: #555555; border-radius: 20px;")
        self.input_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Use a horizontal layout for the input container
        input_layout = QHBoxLayout(self.input_container)
        input_layout.setContentsMargins(150, 10, 150, 10)  # Keep your desired margins
        input_layout.setSpacing(10)

        self.input_text = DynamicTextEdit(self)
        self.input_text.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.send_button = QPushButton("Send", self)
        self.send_button.setFont(QFont("Arial", 14))
        self.send_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.send_button.setFixedHeight(50)
        
        self.send_button.clicked.connect(self.process_input)

        input_layout.addWidget(self.input_text)
        input_layout.addWidget(self.send_button)

        # Add Widgets to Layout
        main_layout.addWidget(self.video_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.input_container, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.visualizer, alignment=Qt.AlignmentFlag.AlignCenter)   
    def process_input(self):
        """Handles user input and switches between video and visualizer."""
        user_input = self.input_text.toPlainText()
        
        # Hide video and show visualizer when TTS plays (Placeholder for actual implementation)
        self.video_widget.hide()
        self.visualizer.show()
        
        # Clear input text after sending
        self.input_text.clear()
        
        # Simulate switching back to video after TTS is done (Temporary logic)
        QTimer.singleShot(3000, self.restore_video)
        
    def restore_video(self):
        """Switch back to Dorothy's idle animation after TTS ends."""
        self.visualizer.hide()
        self.video_widget.show()
        self.player.play()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    chatbot = ChatbotApp()
    chatbot.show()
    sys.exit(app.exec())