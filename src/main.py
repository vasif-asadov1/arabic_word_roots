import sys
import os
import sqlite3
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QLabel, QFrame, QListWidget,
                               QScrollArea, QDialog, QComboBox, QStackedWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QKeySequence, QShortcut


# Import our mathematical morphology engine
from sarf_engine import SarfEngine 

if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_NAME = os.path.join(BASE_DIR, "data", "roots.sqlite3")

import re

def clean_deepdive_data(text):
    """Parses both Almaany and Lane's Lexicon formats dynamically for the UI."""
    if not text or not text.strip():
        return []

    # --- ALMAANY FORMAT ROUTE ---
    if re.search(r'\(\s*فعل\s*\)', text):
        blocks = []
        current_block = None
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            is_pos = bool(re.search(r'\(\s*فعل\s*\)', line))
            is_arabic_only = bool(re.search(r'[\u0600-\u06FF]', line)) and not re.search(r'[a-zA-Z]{2,}', line)
            is_meaning = line.startswith('-')

            if is_arabic_only and not is_pos:
                if current_block: blocks.append(current_block)
                current_block = {"arabic": line, "pos": "", "meanings": []}
            elif is_pos and current_block:
                current_block["pos"] = line.strip()
            elif is_meaning and current_block:
                meaning = line.lstrip('- ').replace('\xa0', ' ').strip()
                if meaning: current_block["meanings"].append(meaning)
        if current_block: blocks.append(current_block)
        return blocks

    # --- LANE'S LEXICON FORMAT ROUTE ---
    # Collapse all the wild whitespace and newlines into single spaces
    cleaned = re.sub(r'\s+', ' ', text).strip()
    
    # Remove the stray " ذ " artifact often found in the raw XML data
    cleaned = re.sub(r'(?<![\u0600-\u06FF])ذ(?![\u0600-\u06FF])', '', cleaned).strip()

    # Lane's uses markers like -b2-, -b3- to separate distinct meanings/paragraphs
    raw_meanings = re.split(r'-[A-Za-z0-9]+-', cleaned)
    
    meanings = [m.strip() for m in raw_meanings if m.strip()]

    # Return in the exact dictionary format your DeepDive UI already expects
    return [{
        "arabic": "Classical Entry", 
        "pos": "Lane's Lexicon",
        "meanings": meanings
    }]


class DeepDiveWidget(QWidget):
    """Embedded right-sidebar widget for Lane's Lexicon data."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(450)
        self.setMaximumWidth(600)
        
        self.base_font_size = 14 # Default starting font size
        self.current_root = ""
        self.current_raw = ""

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(12)

        self.title = QLabel("")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(QFont("Amiri", 36, QFont.Bold))
        self.title.setStyleSheet("color: #88c0d0; border: none; margin-bottom: 8px;")
        main_layout.addWidget(self.title)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #4a6984;")
        main_layout.addWidget(sep)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("""
            QScrollArea { border: none; background-color: transparent; }
            QScrollBar:vertical { background: #2b2b2b; width: 8px; border-radius: 4px; }
            QScrollBar::handle:vertical { background: #4a6984; border-radius: 4px; }
        """)
        main_layout.addWidget(self.scroll)

        self.setStyleSheet("QWidget { background-color: #24272b; border-radius: 10px; }")

    def update_content(self, root_text, almaany_raw):
        """Dynamically recreates the content using the current base_font_size."""
        self.current_root = root_text
        self.current_raw = almaany_raw
        
        self.title.setText(root_text)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(14)
        content_layout.setContentsMargins(8, 8, 8, 8)

        blocks = clean_deepdive_data(almaany_raw)

        if not blocks:
            no_data = QLabel("No deep dive data found for this root.")
            no_data.setStyleSheet(f"color: #6c6c6c; font-size: {self.base_font_size}px; font-style: italic;")
            no_data.setAlignment(Qt.AlignCenter)
            content_layout.addWidget(no_data)
        else:
            for block in blocks:
                block_frame = QFrame()
                block_frame.setStyleSheet("QFrame { background-color: #313438; border-radius: 10px; border: 1px solid #3d4147; }")
                block_layout = QVBoxLayout(block_frame)
                
                if block["arabic"]:
                    arabic_lbl = QLabel(block["arabic"])
                    # Arabic font scales up proportionally (+8) so it's always bigger than English
                    arabic_lbl.setFont(QFont("Amiri", self.base_font_size + 8, QFont.Bold))
                    arabic_lbl.setStyleSheet("color: #e0e0e0; border: none;")
                    arabic_lbl.setAlignment(Qt.AlignRight)
                    block_layout.addWidget(arabic_lbl)

                if block["pos"]:
                    pos_lbl = QLabel(block["pos"])
                    pos_lbl.setFont(QFont("Amiri", self.base_font_size - 1))
                    pos_lbl.setStyleSheet("color: #88c0d0; background-color: #1e3a4a; border-radius: 4px; padding: 2px 8px; border: none;")
                    pos_lbl.setAlignment(Qt.AlignRight)
                    block_layout.addWidget(pos_lbl)

                for meaning in block["meanings"]:
                    clean_meaning = meaning.strip()
                    if not clean_meaning:
                        continue
                    
                    # 1. Use Regex to wrap any Arabic text inside the English definition in HTML tags
                    # This boosts the Arabic font size and changes its color to a nice blue so it stands out
                    html_meaning = re.sub(
                        r'([\u0600-\u06FF]+(?:[\s\u0600-\u06FF]*[\u0600-\u06FF]+)*)', 
                        rf'<span dir="rtl" style="color: #88c0d0; font-family: Amiri; font-size: {self.base_font_size + 6}px;">\1</span>', 
                        clean_meaning
                    )
                    
                    # 2. Add extra line height for readability
                    final_html = f"<div dir='ltr' style='line-height: 150%; text-align: left;'>&bull; {html_meaning}</div>"

                    m_lbl = QLabel(final_html)
                    m_lbl.setTextFormat(Qt.RichText) # Tell PySide6 to render it as HTML!
                    m_lbl.setStyleSheet(f"color: #a3be8c; font-size: {self.base_font_size}px; border: none;")
                    m_lbl.setWordWrap(True)
                    
                    # Add breathing room (margin) between the bullet points
                    m_lbl.setContentsMargins(0, 0, 0, 15)
                    
                    block_layout.addWidget(m_lbl)

                content_layout.addWidget(block_frame)

        content_layout.addStretch()
        self.scroll.setWidget(content_widget)



class SarfWidget(QWidget):
    """Embedded right-sidebar widget for morphological conjugations."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(350)
        self.setMaximumWidth(450)
        self.root_text = ""
        self.engine = SarfEngine()

        layout = QVBoxLayout(self)

        combo_layout = QVBoxLayout() # Stacked vertically for sidebar
        
        self.tense_combo = QComboBox()
        self.tense_combo.addItems([
            "Geçmiş Zaman (Madi)", 
            "Şimdiki/Geniş Zaman (Mudari')", 
            "Gelecek Zaman (Mustakbel)"
        ])
        self.tense_combo.setCursor(Qt.PointingHandCursor)

        self.zamir_combo = QComboBox()
        self.zamir_combo.addItems(list(self.engine.past_suffixes.keys()))
        self.zamir_combo.setCursor(Qt.PointingHandCursor)

        combo_layout.addWidget(self.tense_combo)
        combo_layout.addWidget(self.zamir_combo)

        self.word_label = QLabel()
        self.word_label.setAlignment(Qt.AlignCenter)
        self.word_label.setStyleSheet("color: #88c0d0; border: none; margin-top: 40px;")
        amiri_font = QFont("Amiri", 55, QFont.Bold)
        self.word_label.setFont(amiri_font)

        layout.addLayout(combo_layout)
        layout.addWidget(self.word_label)
        layout.addStretch()

        self.zamir_combo.currentTextChanged.connect(self.update_conjugation)
        self.tense_combo.currentTextChanged.connect(self.update_conjugation)

        self.setStyleSheet("""
            QWidget { background-color: #24272b; border-radius: 10px; }
            QComboBox { 
                padding: 8px; font-size: 14px; background-color: #3c3f41; 
                color: white; border: 1px solid #5c5c5c; border-radius: 4px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView { 
                background-color: #3c3f41; color: white; selection-background-color: #4a6984;
            }
        """)

    def update_content(self, root_text):
        """Dynamically calculates sarf when a new word is selected."""
        self.root_text = root_text
        self.update_conjugation()

    def update_conjugation(self):
        if not self.root_text:
            return
            
        zamir = self.zamir_combo.currentText()
        tense = self.tense_combo.currentText()
        
        if tense == "Geçmiş Zaman (Madi)":
            result = self.engine.conjugate_past_tense(self.root_text, zamir)
        elif tense == "Şimdiki/Geniş Zaman (Mudari')":
            result = self.engine.conjugate_present_tense(self.root_text, zamir)
        elif tense == "Gelecek Zaman (Mustakbel)":
            result = self.engine.conjugate_future_tense(self.root_text, zamir)
        else:
            result = "Error"
            
        self.word_label.setText(result)


class FlashcardApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fusha Roots Flashcards")
        # Made the window wider to comfortably fit the sidebar, and flexible so you can resize it!
        self.setMinimumSize(1250, 600) 
        
        self.roots_data = self.load_data()
        self.current_index = 0
        
        self.setup_ui()
        self.setup_shortcuts()
        self.update_display()
    
    def setup_shortcuts(self):
        """Binds the keyboard shortcuts for zooming."""
        # We bind both '=' and '+' just in case your keyboard layout requires Shift
        QShortcut(QKeySequence("Ctrl+="), self).activated.connect(self.zoom_in)
        QShortcut(QKeySequence("Ctrl++"), self).activated.connect(self.zoom_in)
        QShortcut(QKeySequence("Ctrl+-"), self).activated.connect(self.zoom_out)

    def zoom_in(self):
        """Increases font size if the Deep Dive panel is open."""
        if not self.right_panel.isHidden() and self.right_panel.currentIndex() == 1:
            self.deepdive_widget.base_font_size += 2
            # Re-render with the new size!
            self.deepdive_widget.update_content(self.deepdive_widget.current_root, self.deepdive_widget.current_raw)

    def zoom_out(self):
        """Decreases font size if the Deep Dive panel is open."""
        if not self.right_panel.isHidden() and self.right_panel.currentIndex() == 1:
            if self.deepdive_widget.base_font_size > 10: # Prevent it from becoming completely invisible
                self.deepdive_widget.base_font_size -= 2
                # Re-render with the new size!
                self.deepdive_widget.update_content(self.deepdive_widget.current_root, self.deepdive_widget.current_raw)

    def load_data(self):
        if not os.path.exists(DB_NAME):
            return [("No DB", "Run data scripts", "Veritabanı yok", "")]
            
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT root_arabic, meaning_english, meaning_turkish, almaany_en FROM roots")
        data = cursor.fetchall()
        conn.close()
        return data if data else [("Empty", "No Data", "No Data", "")]

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)

        # --- LEFT: Sidebar Word List ---
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(180)
        self.sidebar.setCursor(Qt.PointingHandCursor)
        self.sidebar.setFocusPolicy(Qt.NoFocus)
        
        sidebar_font = QFont("Amiri", 14)
        self.sidebar.setFont(sidebar_font)
        for index, root_info in enumerate(self.roots_data):
            self.sidebar.addItem(f"{index + 1}.  {root_info[0]}")
            
        self.sidebar.currentRowChanged.connect(self.jump_to_word)

        # --- CENTER: Main Flashcard ---
        center_layout = QVBoxLayout()

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

        # Control Buttons
        btn_layout = QHBoxLayout()
        self.btn_prev = QPushButton("Previous")
        self.btn_prev.setCursor(Qt.PointingHandCursor)
        self.btn_prev.clicked.connect(self.show_previous)
        
        self.btn_sarf = QPushButton("⚙️ Sarf (Conjugate)")
        self.btn_sarf.setCursor(Qt.PointingHandCursor)
        self.btn_sarf.setStyleSheet("background-color: #4a6984; font-weight: bold;")
        self.btn_sarf.clicked.connect(self.toggle_sarf)

        self.btn_deepdive = QPushButton("📖 Deep Dive")
        self.btn_deepdive.setCursor(Qt.PointingHandCursor)
        self.btn_deepdive.setStyleSheet("background-color: #3a5a3a; font-weight: bold;")
        self.btn_deepdive.clicked.connect(self.toggle_deepdive)

        self.btn_next = QPushButton("Next")
        self.btn_next.setCursor(Qt.PointingHandCursor)
        self.btn_next.clicked.connect(self.show_next)

        btn_layout.addWidget(self.btn_prev)
        btn_layout.addWidget(self.btn_sarf)
        btn_layout.addWidget(self.btn_deepdive)
        btn_layout.addWidget(self.btn_next)

        center_layout.addWidget(self.card_frame)
        center_layout.addLayout(btn_layout)

        # --- RIGHT: Toggleable Side Panel Stack ---
        self.right_panel = QStackedWidget()
        self.right_panel.setFixedWidth(550)
        
        self.sarf_widget = SarfWidget()
        self.deepdive_widget = DeepDiveWidget()
        
        # Index 0 = Sarf, Index 1 = Deep Dive
        self.right_panel.addWidget(self.sarf_widget)
        self.right_panel.addWidget(self.deepdive_widget)
        self.right_panel.hide() # Hidden by default on startup

        # Combine all three columns
        main_layout.addWidget(self.sidebar)
        main_layout.addLayout(center_layout)
        main_layout.addWidget(self.right_panel)

        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; }
            QListWidget {
                background-color: #2b2b2b; color: #e0e0e0;
                border: 1px solid #5c5c5c; border-radius: 5px; padding: 5px;
            }
            QListWidget::item { padding: 8px; border-radius: 3px; }
            QListWidget::item:hover { background-color: #3c3f41; }
            QListWidget::item:selected { background-color: #4a6984; color: white; font-weight: bold; }
            QPushButton {
                background-color: #3c3f41; color: white; border-radius: 5px; padding: 10px; font-size: 14px;
            }
            QPushButton:hover { background-color: #4c5052; }
            QPushButton:pressed { background-color: #2b2d2f; }
        """)

    def update_display(self):
        if not self.roots_data:
            return
            
        root, eng, tur, almaany_raw = self.roots_data[self.current_index]
        self.arabic_label.setText(root)
        self.current_meaning = f"{tur}\n\n({eng})"
        self.meaning_label.setText(self.current_meaning)
        
        self.scroll_area.hide() 
        
        self.sidebar.blockSignals(True)
        self.sidebar.setCurrentRow(self.current_index)
        self.sidebar.blockSignals(False)

        # INSTANT SYNC: If the side panel is open, push the new word data to it automatically
        if not self.right_panel.isHidden():
            self.sarf_widget.update_content(root)
            self.deepdive_widget.update_content(root, almaany_raw)

    def reveal_meaning(self, event):
        if self.scroll_area.isHidden(): self.scroll_area.show()
        else: self.scroll_area.hide()

    def toggle_sarf(self):
        if self.right_panel.isHidden():
            self.right_panel.show()
            self.right_panel.setCurrentIndex(0)
        elif self.right_panel.currentIndex() == 0:
            self.right_panel.hide() # Close it if it's already on Sarf
        else:
            self.right_panel.setCurrentIndex(0) # Switch to Sarf from Deep Dive
        
        # Force a data sync so it immediately populates
        self.update_display()

    def toggle_deepdive(self):
        if self.right_panel.isHidden():
            self.right_panel.show()
            self.right_panel.setCurrentIndex(1)
        elif self.right_panel.currentIndex() == 1:
            self.right_panel.hide() # Close it if it's already on Deep Dive
        else:
            self.right_panel.setCurrentIndex(1) # Switch to Deep Dive from Sarf
            
        # Force a data sync so it immediately populates
        self.update_display()

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FlashcardApp()
    window.show()
    sys.exit(app.exec())