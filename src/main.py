"""
Obsidian Note Automation GUI Application
"""
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QComboBox, QLabel, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from api.gemini import GeminiAPI
from obsidian.note import ObsidianNote
from utils.config import Config

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Obsidian Note Automation")
        self.setMinimumSize(800, 600)

        # Initialize components
        try:
            self.config = Config()
            self.gemini = GeminiAPI()
            self.obsidian = ObsidianNote(self.config.vault_path)
        except ValueError as e:
            QMessageBox.critical(self, "Configuration Error", str(e))
            sys.exit(1)

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Create UI elements
        self._create_input_section(layout)
        self._create_action_section(layout)
        self._create_output_section(layout)

    def _create_input_section(self, layout):
        """Create the input text area section"""
        input_label = QLabel("입력 텍스트:")
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("여기에 처리할 텍스트를 입력하세요...")
        
        layout.addWidget(input_label)
        layout.addWidget(self.input_text)

    def _create_action_section(self, layout):
        """Create the action buttons section"""
        action_layout = QHBoxLayout()
        
        # Action type selector
        self.action_type = QComboBox()
        self.action_type.addItems([
            "텍스트 요약",
            "개념 설명",
            "질문 생성",
            "키워드 추출",
            "아이디어 확장"
        ])
        
        # Process button
        process_btn = QPushButton("처리")
        process_btn.clicked.connect(self._process_text)
        
        # Save button
        save_btn = QPushButton("저장")
        save_btn.clicked.connect(self._save_to_obsidian)
        
        action_layout.addWidget(self.action_type)
        action_layout.addWidget(process_btn)
        action_layout.addWidget(save_btn)
        
        layout.addLayout(action_layout)

    def _create_output_section(self, layout):
        """Create the output text area section"""
        output_label = QLabel("결과:")
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        
        layout.addWidget(output_label)
        layout.addWidget(self.output_text)

    async def _process_text(self):
        """Process the input text based on selected action"""
        input_text = self.input_text.toPlainText()
        if not input_text:
            QMessageBox.warning(self, "입력 오류", "처리할 텍스트를 입력해주세요.")
            return

        action = self.action_type.currentText()
        try:
            if action == "텍스트 요약":
                result = await self.gemini.summarize(input_text)
            elif action == "개념 설명":
                result = await self.gemini.explain_concept(input_text)
            elif action == "질문 생성":
                result = await self.gemini.generate_questions(input_text)
            elif action == "키워드 추출":
                result = await self.gemini.extract_keywords(input_text)
            else:  # 아이디어 확장
                result = await self.gemini.expand_idea(input_text)

            self.output_text.setText(result)
        except Exception as e:
            QMessageBox.critical(self, "처리 오류", f"텍스트 처리 중 오류가 발생했습니다: {str(e)}")

    def _save_to_obsidian(self):
        """Save the processed text to an Obsidian note"""
        output_text = self.output_text.toPlainText()
        if not output_text:
            QMessageBox.warning(self, "저장 오류", "저장할 내용이 없습니다.")
            return

        try:
            # Create new note with current timestamp as title
            from datetime import datetime
            title = f"Note_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Prepare metadata
            metadata = {
                'type': self.action_type.currentText(),
                'source': self.input_text.toPlainText()[:100] + "..."  # First 100 chars of source
            }
            
            # Create the note
            file_path = self.obsidian.create_note(title, output_text, metadata)
            
            QMessageBox.information(self, "저장 완료", f"노트가 성공적으로 저장되었습니다:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "저장 오류", f"노트 저장 중 오류가 발생했습니다: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
