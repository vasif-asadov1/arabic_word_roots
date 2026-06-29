import sys
import sqlite3
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QLabel, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

import os

# Get the absolute path of the directory containing this script (src/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Build the path to the data folder dynamically
DB_NAME = os.path.join(BASE_DIR, "..", "data", "roots.sqlite3")



class FlashcardApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fusha Roots Flashcards")
        self.setFixedSize(500, 400)
        
        # Load data from database
        self.roots_data = self.load_data()
        self.current_index = 0
        
        self.setup_ui()
        self.update_display()

    def load_data(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT root_arabic, meaning_english, meaning_turkish FROM roots")
        data = cursor.fetchall()
        conn.close()
        return data if data else [("No Data", "No Data", "No Data")]

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Flashcard Frame
        self.card_frame = QFrame()
        self.card_frame.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border-radius: 15px;
                border: 2px solid #5c5c5c;
            }
        """)
        card_layout = QVBoxLayout(self.card_frame)
        card_layout.setAlignment(Qt.AlignCenter)

        # Arabic Root Label
        self.arabic_label = QLabel()
        self.arabic_label.setAlignment(Qt.AlignCenter)
        self.arabic_label.setStyleSheet("color: #e0e0e0; border: none;")
        # Set Amiri Font for Arabic text
        amiri_font = QFont("Amiri", 48, QFont.Bold)
        self.arabic_label.setFont(amiri_font)
        self.arabic_label.setCursor(Qt.PointingHandCursor)
        self.arabic_label.setToolTip("Click to reveal meaning")
        
        # Connect click event to reveal meaning
        self.arabic_label.mousePressEvent = self.reveal_meaning

        # Meaning Label (Hidden by default)
        self.meaning_label = QLabel()
        self.meaning_label.setAlignment(Qt.AlignCenter)
        self.meaning_label.setStyleSheet("color: #a3be8c; font-size: 18px; border: none;")
        self.meaning_label.hide()

        card_layout.addWidget(self.arabic_label)
        card_layout.addWidget(self.meaning_label)

        # Buttons Layout
        btn_layout = QHBoxLayout()
        
        self.btn_prev = QPushButton("Previous")
        self.btn_prev.setCursor(Qt.PointingHandCursor)
        self.btn_prev.clicked.connect(self.show_previous)
        
        self.btn_next = QPushButton("Next")
        self.btn_next.setCursor(Qt.PointingHandCursor)
        self.btn_next.clicked.connect(self.show_next)

        btn_layout.addWidget(self.btn_prev)
        btn_layout.addWidget(self.btn_next)

        # Add to main layout
        main_layout.addWidget(self.card_frame)
        main_layout.addLayout(btn_layout)

        # General App Styling
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; }
            QPushButton {
                background-color: #3c3f41;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #4c5052; }
            QPushButton:pressed { background-color: #2b2d2f; }
        """)

    def update_display(self):
        root, eng, tur = self.roots_data[self.current_index]
        self.arabic_label.setText(root)
        # Store meanings to display later
        self.current_meaning = f"{tur}\n({eng})"
        self.meaning_label.setText(self.current_meaning)
        self.meaning_label.hide()  # Hide meaning when moving to a new card

    def reveal_meaning(self, event):
        # Toggle visibility of the meaning
        if self.meaning_label.isHidden():
            self.meaning_label.show()
        else:
            self.meaning_label.hide()

    def show_previous(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_display()

    def show_next(self):
        if self.current_index < len(self.roots_data) - 1:
            self.current_index += 1
            self.update_display()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FlashcardApp()
    window.show()
    sys.exit(app.exec())