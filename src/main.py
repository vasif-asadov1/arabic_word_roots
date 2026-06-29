import sys
import os
import sqlite3
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QLabel, QFrame, QListWidget,
                               QScrollArea, QDialog, QComboBox) 
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

# Import our mathematical morphology engine
from sarf_engine import SarfEngine 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "..", "data", "roots.sqlite3")

class SarfDialog(QDialog):
    """A clean popup window dedicated entirely to morphological conjugations."""
    def __init__(self, root_text, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Sarf Patterns - {root_text}")
        self.setFixedSize(450, 300)
        self.root_text = root_text
        self.engine = SarfEngine()

        layout = QVBoxLayout(self)

        # Dropdowns Layout
        combo_layout = QHBoxLayout()
        
        self.tense_combo = QComboBox()
        # ADDED: Present and Future Tenses
        self.tense_combo.addItems([
            "Past Tense (Madi)", 
            "Present Tense (Mudari')", 
            "Future Tense (Mustaqbal)"
        ]) 
        self.tense_combo.setCursor(Qt.PointingHandCursor)

        self.zamir_combo = QComboBox()
        self.zamir_combo.addItems(list(self.engine.past_suffixes.keys()))
        self.zamir_combo.setCursor(Qt.PointingHandCursor)

        combo_layout.addWidget(self.tense_combo)
        combo_layout.addWidget(self.zamir_combo)

        # Dynamic Conjugated Word Display
        self.word_label = QLabel()
        self.word_label.setAlignment(Qt.AlignCenter)
        self.word_label.setStyleSheet("color: #88c0d0; border: none; margin-top: 20px;")
        amiri_font = QFont("Amiri", 55, QFont.Bold)
        self.word_label.setFont(amiri_font)

        layout.addLayout(combo_layout)
        layout.addWidget(self.word_label)

        # Connect the dropdowns to the update function
        self.zamir_combo.currentTextChanged.connect(self.update_conjugation)
        self.tense_combo.currentTextChanged.connect(self.update_conjugation)

        # Professional Dark Styling
        self.setStyleSheet("""
            QDialog { background-color: #2b2b2b; }
            QComboBox { 
                padding: 8px; 
                font-size: 14px; 
                background-color: #3c3f41; 
                color: white; 
                border: 1px solid #5c5c5c;
                border-radius: 4px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView { 
                background-color: #3c3f41; 
                color: white; 
                selection-background-color: #4a6984;
            }
        """)

        # Run once to display the default setting
        self.update_conjugation()

    def update_conjugation(self):
        """Routes the UI selection to the correct mathematical engine."""
        zamir = self.zamir_combo.currentText()
        tense = self.tense_combo.currentText()
        
        # Routing Logic
        if tense == "Past Tense (Madi)":
            result = self.engine.conjugate_past_tense(self.root_text, zamir)
        elif tense == "Present Tense (Mudari')":
            result = self.engine.conjugate_present_tense(self.root_text, zamir)
        elif tense == "Future Tense (Mustaqbal)":
            result = self.engine.conjugate_future_tense(self.root_text, zamir)
        else:
            result = "Error"
            
        self.word_label.setText(result)


class FlashcardApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fusha Roots Flashcards")
        self.setFixedSize(700, 450) 
        
        self.roots_data = self.load_data()
        self.current_index = 0
        
        self.setup_ui()
        self.update_display()

    def load_data(self):
        if not os.path.exists(DB_NAME):
            return [("No DB", "Run data scripts", "Veritabanı yok")]
            
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT root_arabic, meaning_english, meaning_turkish FROM roots")
        data = cursor.fetchall()
        conn.close()
        return data if data else [("Empty", "No Data", "No Data")]

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)

        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(180)
        self.sidebar.setCursor(Qt.PointingHandCursor)
        self.sidebar.setFocusPolicy(Qt.NoFocus)
        
        sidebar_font = QFont("Amiri", 14)
        self.sidebar.setFont(sidebar_font)
        for index, root_info in enumerate(self.roots_data):
            self.sidebar.addItem(f"{index + 1}.  {root_info[0]}")
            
        self.sidebar.currentRowChanged.connect(self.jump_to_word)

        right_layout = QVBoxLayout()

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

        self.arabic_label = QLabel()
        self.arabic_label.setAlignment(Qt.AlignCenter)
        self.arabic_label.setStyleSheet("color: #e0e0e0; border: none;")
        amiri_font = QFont("Amiri", 48, QFont.Bold)
        self.arabic_label.setFont(amiri_font)
        self.arabic_label.setCursor(Qt.PointingHandCursor)
        self.arabic_label.mousePressEvent = self.reveal_meaning

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.meaning_label = QLabel()
        self.meaning_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.meaning_label.setStyleSheet("color: #a3be8c; font-size: 16px; border: none; padding: 10px 20px;")
        self.meaning_label.setWordWrap(True)
        
        self.scroll_area.setWidget(self.meaning_label)
        self.scroll_area.hide() 

        card_layout.addWidget(self.arabic_label)
        card_layout.addWidget(self.scroll_area) 

        # --- UPDATED CONTROL BUTTONS ---
        btn_layout = QHBoxLayout()
        self.btn_prev = QPushButton("Previous")
        self.btn_prev.setCursor(Qt.PointingHandCursor)
        self.btn_prev.clicked.connect(self.show_previous)
        
        # New Sarf Button
        self.btn_sarf = QPushButton("⚙️ Sarf (Conjugate)")
        self.btn_sarf.setCursor(Qt.PointingHandCursor)
        self.btn_sarf.setStyleSheet("background-color: #4a6984; font-weight: bold;") # Highlighted styling
        self.btn_sarf.clicked.connect(self.open_sarf_dialog)

        self.btn_next = QPushButton("Next")
        self.btn_next.setCursor(Qt.PointingHandCursor)
        self.btn_next.clicked.connect(self.show_next)

        btn_layout.addWidget(self.btn_prev)
        btn_layout.addWidget(self.btn_sarf) # Added to the center
        btn_layout.addWidget(self.btn_next)

        right_layout.addWidget(self.card_frame)
        right_layout.addLayout(btn_layout)

        main_layout.addWidget(self.sidebar)
        main_layout.addLayout(right_layout)

        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; }
            QListWidget {
                background-color: #2b2b2b;
                color: #e0e0e0;
                border: 1px solid #5c5c5c;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item { padding: 8px; border-radius: 3px; }
            QListWidget::item:hover { background-color: #3c3f41; }
            QListWidget::item:selected { 
                background-color: #4a6984; 
                color: white; 
                font-weight: bold;
            }
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
        if not self.roots_data:
            return
            
        root, eng, tur = self.roots_data[self.current_index]
        self.arabic_label.setText(root)
        self.current_meaning = f"{tur}\n\n({eng})"
        self.meaning_label.setText(self.current_meaning)
        
        self.scroll_area.hide() 
        
        self.sidebar.blockSignals(True)
        self.sidebar.setCurrentRow(self.current_index)
        self.sidebar.blockSignals(False)

    def reveal_meaning(self, event):
        if self.scroll_area.isHidden():
            self.scroll_area.show()
        else:
            self.scroll_area.hide()

    def open_sarf_dialog(self):
        """Opens the dynamic conjugation window for the current root."""
        if not self.roots_data:
            return
        root_text = self.roots_data[self.current_index][0]
        dialog = SarfDialog(root_text, self)
        dialog.exec() # Pauses the main window until the dialog is closed

    def jump_to_word(self, row):
        self.current_index = row
        self.update_display()

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