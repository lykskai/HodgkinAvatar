import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtCore import QUrl
import pyqtgraph as pg

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
        from PyQt6.QtCore import QTimer
        self.loop_timer = QTimer()
        self.loop_timer.timeout.connect(self.loop_video)
        self.loop_timer.start(1000)  # Check every second to ensure smooth looping
        
        # Audio Visualizer (Hidden by Default)
        self.visualizer = pg.PlotWidget(self)
        self.visualizer.setYRange(-1, 1)
        self.waveform = self.visualizer.plot(pen='g')
        self.visualizer.hide()
        
        # Circular Input Box & Send Button
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(300, 10, 300, 200)  # Reduce horizontal space
        self.input_text = QLineEdit(self)
        self.input_text.setFont(QFont("Arial", 14))
        self.input_text.setPlaceholderText("Type here...")
        self.input_text.setFixedHeight(50)
        self.input_text.setStyleSheet("border-radius: 15px; padding: 10px; background-color: white; border: 2px solid #ccc;")
        
        self.send_button = QPushButton("Send", self)
        self.send_button.setFont(QFont("Arial", 14))
        self.send_button.setFixedHeight(50)
        self.send_button.clicked.connect(self.process_input)
        
        input_layout.addWidget(self.input_text)
        input_layout.addWidget(self.send_button)
        
        # Add Widgets to Layout
        main_layout.addWidget(self.video_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.visualizer, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addLayout(input_layout)
        
    def process_input(self):
        """Handles user input and switches between video and visualizer."""
        user_input = self.input_text.text()
        
        # Hide video and show visualizer when TTS plays (Placeholder for actual implementation)
        self.video_widget.hide()
        self.visualizer.show()
        
        # Simulate switching back to video after TTS is done (Temporary logic)
        from PyQt6.QtCore import QTimer
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
