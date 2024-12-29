#!/usr/bin/env python3
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTextEdit, QPushButton
from src.ontology import ObsidianOntology

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("노트 생성기")
        self.setGeometry(100, 100, 600, 400)
        
        # 중앙 위젯 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 내용 입력 필드
        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("내용을 입력하세요...")
        layout.addWidget(self.content_edit)
        
        # 생성 버튼
        self.generate_button = QPushButton("노트 생성")
        self.generate_button.clicked.connect(self.generate_note)
        layout.addWidget(self.generate_button)
        
        # Obsidian Ontology 초기화
        self.ontology = ObsidianOntology()
    
    def generate_note(self):
        content = self.content_edit.toPlainText().strip()
        if not content:
            return
        self.ontology.process_new_note(content=content)
        self.content_edit.clear()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
