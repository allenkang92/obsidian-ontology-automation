import os
from pathlib import Path
import frontmatter
import google.generativeai as genai
from dotenv import load_dotenv
import re
import yaml
from datetime import datetime
from src.utils.vault_finder import find_obsidian_vaults
from src.note_manager import NoteManager
from src.visualizer import OntologyVisualizer
from src.tagger import AutoTagger
from src.template_manager import TemplateManager

class ObsidianOntology:
    def __init__(self, vault_path=None):
        # 볼트 경로를 지정하지 않은 경우 자동으로 찾기
        if vault_path is None:
            vaults = find_obsidian_vaults()
            if not vaults:
                raise ValueError("옵시디언 볼트를 찾을 수 없습니다.")
            vault_path = vaults[0]  # 첫 번째 발견된 볼트 사용
            print(f"옵시디언 볼트를 찾았습니다: {vault_path}")
            
        self.vault_path = Path(vault_path)
        self.note_manager = NoteManager(self.vault_path)
        self.template_manager = TemplateManager(self.vault_path)
        
        # API 설정
        load_dotenv()
        api_key = os.getenv('GEMINI_API_KEY')
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
        # 태거 초기화
        self.tagger = AutoTagger(self.model)

    def extract_ontology(self, text):
        """텍스트에서 온톨로지 관계를 추출"""
        prompt = f"""
다음 텍스트를 분석하여 개념들 간의 관계를 추출해주세요.
마크다운이나 코드 블록을 사용하지 말고, 순수한 YAML 형식으로만 응답해주세요.

예시 형식:
concepts:
  - 개념1
  - 개념2
relationships:
  - type: is_a
    source: 개념1
    target: 개념2
    description: 관계 설명

텍스트:
{text}
"""
        response = self.model.generate_content(prompt)
        yaml_text = response.text.strip()
        
        # 마크다운 코드 블록이 있다면 제거
        yaml_text = re.sub(r'^```yaml\s*|```\s*$', '', yaml_text)
        
        # YAML 형식에서 frontmatter 구분자(---)를 제거
        yaml_text = re.sub(r'^---\s*|---\s*$', '', yaml_text)
        
        # YAML 파싱
        try:
            ontology = yaml.safe_load(yaml_text)
            return ontology if isinstance(ontology, dict) else {'concepts': [], 'relationships': []}
        except Exception as e:
            print(f"YAML 파싱 오류: {e}")
            return {'concepts': [], 'relationships': []}

    def find_related_notes(self, concepts):
        """주어진 개념들과 관련된 노트들을 찾음"""
        related_notes = []
        for note_path in self.vault_path.glob("**/*.md"):
            try:
                with open(note_path, 'r', encoding='utf-8') as f:
                    metadata = frontmatter.load(f)
                    if 'concepts' in metadata.metadata:
                        note_concepts = set(metadata.metadata['concepts'])
                        if note_concepts.intersection(concepts):
                            related_notes.append(note_path)
            except Exception as e:
                print(f"Error processing {note_path}: {e}")
        return related_notes

    def process_new_note(self, title, content, template_name='default.md'):
        """새로운 노트 처리"""
        print(f"\n=== '{title}' 노트 처리 중 ===")
        
        # 1. Gemini API로 내용 생성
        generate_prompt = f"""
다음 주제에 대해 자세히 설명해주세요. 다음 내용을 포함해주세요:
1. 정의와 개념
2. 주요 특징
3. 관련된 개념이나 분야
4. 실제 예시나 응용

주제: {content}
"""
        response = self.model.generate_content(generate_prompt)
        generated_content = response.text.strip()
        
        # 2. 온톨로지 추출
        ontology = self.extract_ontology(generated_content)
        print("\n추출된 온톨로지:")
        print(yaml.dump(ontology, allow_unicode=True))
        
        # 3. 태그 생성
        text_tags = self.tagger.extract_tags(generated_content)
        ontology_tags = self.tagger.suggest_tags_from_ontology(ontology)
        keywords = self.tagger.extract_keywords(generated_content)
        tags = self.tagger.combine_tags(text_tags, ontology_tags, keywords)
        
        # 4. 관련 노트 찾기
        concepts = self._extract_concepts_from_yaml(ontology)
        related_notes = self.find_related_notes(concepts)
        
        # 5. 시각화
        visualizer = OntologyVisualizer()
        mermaid_diagram = visualizer.generate_mermaid(ontology)
        
        # 6. 노트 생성
        metadata = {
            'title': title,
            'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'modified': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'type': 'concept',
            'tags': tags,
            'concepts': concepts
        }
        
        # 템플릿에 전달할 변수
        template_vars = {
            **metadata,
            'content': generated_content,
            'relationships': ontology.get('relationships', []),
            'mermaid_diagram': mermaid_diagram,
            'related_notes': [str(note.relative_to(self.vault_path)) for note in related_notes]
        }
        
        # 노트 생성
        note_content = self.template_manager.render_template(template_name, template_vars)
        note_path = self.note_manager.create_note(title, note_content)
        
        print(f"\n노트가 생성되었습니다: {note_path}")
        return note_path

    def suggest_connections(self, text):
        """새로운 텍스트와 기존 노트들 사이의 연결 제안"""
        # 1. 온톨로지 추출
        ontology = self.extract_ontology(text)
        print("=== 추출된 온톨로지 ===")
        print(ontology)
        print()

        # 2. 관련 노트 찾기
        concepts = self._extract_concepts_from_yaml(ontology)
        related_notes = self.find_related_notes(concepts)
        
        if related_notes:
            print("=== 관련된 노트들 ===")
            for note in related_notes:
                print(f"- {note.name}")
            print()

            # 3. 연결 관계 제안
            notes_content = self._get_notes_content(related_notes)
            suggestions = self._generate_connection_suggestions(text, notes_content)
            print("=== 제안된 연결 관계 ===")
            print(suggestions)
        else:
            print("관련된 노트를 찾을 수 없습니다.")

    def _extract_concepts_from_yaml(self, ontology):
        """온톨로지에서 개념 리스트 추출"""
        if isinstance(ontology, dict) and 'concepts' in ontology:
            return set(ontology['concepts'])
        return set()

    def _get_notes_content(self, note_paths):
        """노트들의 내용을 가져옴"""
        contents = []
        for path in note_paths:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    post = frontmatter.load(f)
                    contents.append({
                        'title': path.stem,
                        'content': post.content,
                        'metadata': post.metadata
                    })
            except Exception as e:
                print(f"Error reading {path}: {e}")
        return contents

    def _generate_connection_suggestions(self, new_text, existing_notes):
        """새로운 텍스트와 기존 노트들 사이의 연결 관계 제안"""
        prompt = """
다음 새로운 텍스트와 기존 노트들 사이의 의미있는 연결 관계를 제안해주세요.
각 연결에 대해 그 이유도 설명해주세요.

새로운 텍스트:
{new_text}

기존 노트들:
{existing_notes}
"""
        formatted_notes = "\n".join([
            f"제목: {note['title']}\n내용: {note['content'][:200]}..." 
            for note in existing_notes
        ])
        
        response = self.model.generate_content(prompt.format(
            new_text=new_text,
            existing_notes=formatted_notes
        ))
        return response.text

def test_ontology():
    try:
        # 볼트 경로를 자동으로 찾아서 사용
        ontology = ObsidianOntology()
        
        test_text = """
        머신러닝은 인공지능의 한 분야로, 컴퓨터가 데이터로부터 학습하여 패턴을 발견하고 예측을 수행하는 기술이다.
        지도학습은 머신러닝의 주요 방법 중 하나로, 레이블이 있는 데이터를 사용하여 모델을 훈련시킨다.
        딥러닝은 머신러닝의 한 종류로, 여러 층의 인공신경망을 사용하여 복잡한 패턴을 학습한다.
        """
        
        print("\n=== 온톨로지 기반 노트 연결 테스트 ===")
        ontology.suggest_connections(test_text)
        
        # 새로운 노트 처리 테스트
        title = "머신러닝 개념"
        content = """
        머신러닝은 인공지능의 한 분야로, 컴퓨터가 데이터로부터 학습하여 패턴을 발견하고 예측을 수행하는 기술이다.
        """
        ontology.process_new_note(title, content)
        
    except Exception as e:
        print(f"오류 발생: {e}")

def test_deep_learning():
    try:
        ontology = ObsidianOntology()
        
        deep_learning_content = """
딥러닝(Deep Learning)은 인공신경망을 기반으로 한 머신러닝의 한 분야입니다.

주요 특징:
1. 다층 신경망 구조
   - 입력층, 은닉층, 출력층으로 구성
   - 여러 개의 은닉층을 통해 복잡한 패턴 학습

2. 학습 방법
   - 역전파(Backpropagation) 알고리즘 사용
   - 경사하강법으로 가중치 최적화
   - 대규모 데이터셋 필요

3. 주요 응용 분야
   - 컴퓨터 비전 (CNN)
   - 자연어 처리 (RNN, Transformer)
   - 음성 인식
   - 강화학습

4. 프레임워크
   - TensorFlow
   - PyTorch
   - Keras
        """
        
        # 딥러닝 노트 생성
        print("\n=== 딥러닝 노트 테스트 ===")
        ontology.process_new_note(
            title="딥러닝의 이해",
            content=deep_learning_content,
            template_name="concept.md"
        )
        
    except Exception as e:
        print(f"오류 발생: {e}")

def test_kafka():
    """카프카 노트 테스트"""
    try:
        ontology = ObsidianOntology()
        ontology.process_new_note(
            title="카프카의 이해",
            content="카프카",
            template_name="concept.md"
        )
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    test_kafka()
