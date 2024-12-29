from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QTextEdit, QComboBox, QPushButton,
    QLabel, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from test_ontology import ObsidianOntology

class ObsidianGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ontology = ObsidianOntology()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Obsidian Note Automation')
        self.setGeometry(100, 100, 800, 600)

        # 중앙 위젯 생성
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 제목 입력
        title_layout = QHBoxLayout()
        title_label = QLabel('제목:')
        self.title_input = QLineEdit()
        title_layout.addWidget(title_label)
        title_layout.addWidget(self.title_input)
        layout.addLayout(title_layout)

        # 내용 입력
        content_label = QLabel('내용:')
        self.content_input = QTextEdit()
        layout.addWidget(content_label)
        layout.addWidget(self.content_input)

        # 템플릿 선택
        template_layout = QHBoxLayout()
        template_label = QLabel('템플릿:')
        self.template_combo = QComboBox()
        self.template_combo.addItems(['concept.md', 'default.md', 'daily.md'])
        template_layout.addWidget(template_label)
        template_layout.addWidget(self.template_combo)
        layout.addLayout(template_layout)

        # 버튼
        button_layout = QHBoxLayout()
        
        # 파일 업로드 버튼
        upload_btn = QPushButton('파일 업로드')
        upload_btn.clicked.connect(self.upload_file)
        button_layout.addWidget(upload_btn)
        
        # 노트 생성 버튼
        create_btn = QPushButton('노트 생성')
        create_btn.clicked.connect(self.create_note)
        button_layout.addWidget(create_btn)
        
        layout.addLayout(button_layout)

    def upload_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, '파일 선택', '', 'Text Files (*.txt *.md);;All Files (*)'
        )
        if file_name:
            try:
                with open(file_name, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.content_input.setText(content)
            except Exception as e:
                QMessageBox.critical(self, '오류', f'파일을 읽는 중 오류가 발생했습니다: {str(e)}')

    def create_note(self):
        title = self.title_input.text()
        content = self.content_input.toPlainText()
        template = self.template_combo.currentText()

        if not title:
            QMessageBox.warning(self, '경고', '제목을 입력해주세요.')
            return
        if not content:
            QMessageBox.warning(self, '경고', '내용을 입력해주세요.')
            return

        try:
            self.ontology.process_new_note(
                title=title,
                content=content,
                template_name=template
            )
            QMessageBox.information(self, '성공', '노트가 생성되었습니다.')
            self.title_input.clear()
            self.content_input.clear()
        except Exception as e:
            QMessageBox.critical(self, '오류', f'노트 생성 중 오류가 발생했습니다: {str(e)}')
