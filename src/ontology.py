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
from src.template_manager import TemplateManager

class ObsidianOntology:
    def __init__(self, vault_path=None):
        # 볼트 경로를 지정하지 않은 경우 자동으로 찾기
        if vault_path is None:
            vaults = find_obsidian_vaults()
            if not vaults:
                raise ValueError("옵시디언 볼트를 찾을 수 없습니다.")
            vault_path = vaults[0]
            print(f"옵시디언 볼트를 찾았습니다: {vault_path}")
        
        self.vault_path = Path(vault_path)
        
        # 환경 변수 로드
        load_dotenv()
        
        # Gemini API 설정
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-pro')
        
        # 매니저 및 도구 초기화
        self.note_manager = NoteManager(vault_path)
        self.visualizer = OntologyVisualizer()
        self.template_manager = TemplateManager(vault_path)
    
    def _extract_title(self, content):
        """내용에서 핵심 주제를 추출하여 제목 생성"""
        prompt = f"""
다음 내용의 핵심 주제를 추출해주세요.
입력된 단어의 형태를 최대한 유지해주세요.
불필요하게 단어를 줄이거나 변형하지 마세요.

예시:
"인공지능이란 무엇인가?" -> "인공지능"
"윤리학의 기본 개념" -> "윤리학"
"자연어 처리 시스템" -> "자연어 처리"

내용:
{content}
"""
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"제목 생성 오류: {e}")
            return "새로운 노트"

    def process_new_note(self, content, template_name="concept.md"):
        """새로운 노트를 생성하고 온톨로지 관계를 추출"""
        # 공백 제거 후 내용 확인
        content = content.strip()
        if not content:
            print("내용을 입력해주세요.")
            return
            
        # 제목 자동 생성
        title = self._extract_title(content)
        print(f"\n=== '{title}' 노트 처리 중 ===\n")
        
        # Gemini API로 내용 생성
        prompt = f"""
{title}에 대해 다음 형식으로 정확하게 설명해주세요:

## 정의
- 한 문장으로 핵심을 정확하게 설명해주세요

## 주요 특징
- 가장 중요한 특징 3가지를 나열해주세요
- 각 특징은 한 줄로 간단명료하게 설명해주세요

## 관련 분야
- 가장 밀접하게 관련된 3가지 분야를 나열해주세요
- 각 분야와의 관련성을 한 줄로 설명해주세요

## 활용
- 실제 활용되는 3가지 예시를 나열해주세요
- 각 활용 사례를 한 줄로 구체적으로 설명해주세요

주의사항:
1. 모든 설명은 간단명료하게 작성해주세요
2. 전문 용어는 꼭 필요한 경우에만 사용해주세요
3. "~적 설" 같은 불필요한 표현은 사용하지 마세요
4. 각 섹션은 정확히 3가지 항목만 포함해주세요
"""
        
        try:
            response = self.model.generate_content(prompt)
            generated_content = response.text
        except Exception as e:
            print(f"Gemini API 오류: {e}")
            generated_content = content
        
        # 온톨로지 추출
        ontology = self._extract_ontology(generated_content)
        print("추출된 온톨로지:")
        print(yaml.dump(ontology, allow_unicode=True))
        
        # Mermaid 다이어그램 생성
        mermaid_diagram = self.visualizer.generate_mermaid(ontology)
        
        # 메타데이터 생성
        created = modified = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        metadata = {
            'title': title,
            'created': created,
            'modified': modified,
            'type': 'concept',
            'concepts': ontology.get('concepts', [])
        }
        
        # 노트 생성
        try:
            note_content = self.template_manager.render_template(
                template_name,
                {
                    'title': title,
                    'content': generated_content,
                    'mermaid_diagram': mermaid_diagram,
                    'ontology': ontology,
                    'created': created,
                    'modified': modified,
                    'type': 'concept'
                }
            )
            
            # 노트 저장
            note_path = self.note_manager.create_note(title, note_content)
            print(f"\n노트가 생성되었습니다: {note_path}\n")
            
        except Exception as e:
            print(f"오류 발생: {e}")
    
    def _extract_ontology(self, content):
        """텍스트에서 온톨로지 관계를 추출"""
        prompt = """
다음 텍스트에서 주요 개념들과 그들 사이의 관계를 추출해주세요.
리스트나 계층 구조가 있는 경우, 각 항목을 개별 개념으로 추출하고 관계를 명시해주세요.
예를 들어 "1.1 API 호출 속도"는 "API 호출"의 하위 개념입니다.

YAML 형식으로 반환해주세요:

concepts:  # 텍스트에서 언급된 주요 개념들
  - concept1
  - concept2
  ...

relationships:  # 개념들 간의 관계
  - source: 개념1  # 관계의 주체
    target: 개념2  # 관계의 대상
    type: is_a     # 관계 유형: is_a(종류), part_of(구성요소), used_for(용도), related_to(관련)
  ...

관계 유형은 다음 중 하나를 사용해주세요:
- is_a: "A는 B의 한 종류이다" (예: "API 호출 속도는 API 호출의 한 종류이다")
- part_of: "A는 B의 구성요소이다" (예: "초당 호출 횟수는 API 호출 속도의 구성요소이다")
- used_for: "A는 B를 위해 사용된다" (예: "RateLimiter는 API 호출 속도 제어를 위해 사용된다")
- related_to: "A는 B와 관련이 있다"

텍스트:
{content}
"""
        try:
            response = self.model.generate_content(prompt.format(content=content))
            yaml_text = response.text.strip()
            
            # YAML 코드 블록이 있다면 제거
            yaml_text = re.sub(r'^```yaml\s*|```\s*$', '', yaml_text)
            
            # YAML 파싱
            ontology = yaml.safe_load(yaml_text)
            
            return ontology
        except Exception as e:
            print(f"온톨로지 추출 중 오류 발생: {e}")
            return {'concepts': [], 'relationships': []}
