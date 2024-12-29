# Obsidian Ontology Automation

Obsidian을 사용한 스터디 노트 자동화 도구입니다. Gemini API를 사용하여 노트를 자동으로 처리하고, 개념들 간의 관계를 추출하여 시각화합니다.

## 주요 기능

- **온톨로지 기반 노트 분석**
    - 노트 간의 관계 추출
    - 개념 맵 자동 생성
    - 관련 노트 자동 연결
    - 양방향 링크 자동 생성

## 온톨로지(Ontology)란?

온톨로지는 특정 도메인 내의 개념들과 그들 간의 관계를 명시적으로 정의한 형식적이고 명시적인 명세를 의미합니다. 이 프로젝트에서는 Obsidian 노트들 간의 관계를 온톨로지로 표현합니다.

### 온톨로지의 주요 구성 요소

1. **개념(Concepts)**: 노트들이 다루는 주요 주제나 아이디어
2. **관계(Relations)**: 노트들 간의 연결 관계 (예: 링크, 태그)
3. **속성(Properties)**: 각 노트의 특성 (제목, 생성일, 수정일 등)
4. **인스턴스(Instances)**: 실제 노트 파일들

### 이 프로젝트에서의 온톨로지 활용

- **노트 간 관계 분석**: 노트들 사이의 연결 관계를 그래프로 시각화
- **지식 구조화**: 관련된 노트들을 클러스터링하여 지식의 구조를 파악
- **인사이트 도출**: 노트들 간의 관계를 통해 새로운 통찰력 발견

## 설치 방법

```bash
git clone https://github.com/allenkang92/obsidian-ontology-automation.git
cd obsidian-ontology-automation
pip install -r requirements.txt
```

## 환경 설정

1. `.env.template` 파일을 `.env`로 복사합니다.
2. `.env` 파일에서 다음 값들을 설정합니다:
   - `GEMINI_API_KEY`: Google Gemini API 키
   - `OBSIDIAN_VAULT_PATH`: Obsidian 볼트 경로

## 사용 방법

GUI를 실행합니다:
```bash
python run_gui.py
```

## 주요 기능

- Obsidian 노트 파일 분석
- 노트 간 관계 시각화
- 온톨로지 데이터 추출 및 분석
- 대화형 GUI 인터페이스

