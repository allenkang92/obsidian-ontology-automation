"""
노트 템플릿 관리자
"""
import os
from pathlib import Path
import yaml
import jinja2

class TemplateManager:
    def __init__(self, vault_path):
        self.vault_path = Path(vault_path)
        self.template_dir = self.vault_path / '.templates'
        self.ensure_template_dir()
        
        # Jinja2 환경 설정
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(self.template_dir)),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
    
    def ensure_template_dir(self):
        """템플릿 디렉토리가 없으면 생성"""
        if not self.template_dir.exists():
            self.template_dir.mkdir(parents=True)
            self.create_default_templates()
    
    def create_default_templates(self):
        """기본 템플릿 생성"""
        templates = {
            'default.md': """---
title: {{ title }}
created: {{ created }}
modified: {{ modified }}
type: note
tags: {{ tags | join(', ') }}
---

# {{ title }}

{{ content }}

{% if related_notes %}
## 관련 노트
{% for note in related_notes %}
- [[{{ note }}]]
{% endfor %}
{% endif %}

{% if mermaid_diagram %}
## 개념 관계도
{{ mermaid_diagram }}
{% endif %}
""",
            'concept.md': """---
title: {{ title }}
created: {{ created }}
modified: {{ modified }}
type: concept
tags: {{ tags | join(', ') }}
concepts: {{ concepts | join(', ') }}
---

# {{ title }}

## 정의
{{ content }}

{% if relationships %}
## 관계
{% for rel in relationships %}
- {{ rel.source }} {{ rel.type }} {{ rel.target }}: {{ rel.description }}
{% endfor %}
{% endif %}

{% if examples %}
## 예시
{% for example in examples %}
- {{ example }}
{% endfor %}
{% endif %}

{% if mermaid_diagram %}
## 개념 관계도
{{ mermaid_diagram }}
{% endif %}

{% if related_notes %}
## 관련 노트
{% for note in related_notes %}
- [[{{ note }}]]
{% endfor %}
{% endif %}
""",
            'daily.md': """---
title: {{ title }}
created: {{ created }}
modified: {{ modified }}
type: daily
tags: daily
---

# {{ title }}

## 오늘의 할 일
- [ ] 

## 메모
{{ content }}

{% if related_notes %}
## 관련 노트
{% for note in related_notes %}
- [[{{ note }}]]
{% endfor %}
{% endif %}
"""
        }
        
        for name, content in templates.items():
            path = self.template_dir / name
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def get_template(self, template_name='default.md'):
        """템플릿 가져오기"""
        return self.env.get_template(template_name)
    
    def render_template(self, template_name, variables):
        """템플릿 렌더링"""
        try:
            template = self.env.get_template(template_name)
            return template.render(**variables)
        except Exception as e:
            print(f"Error processing {template_name}: {e}")
            # 기본 템플릿 사용
            return f"""---
title: {variables.get('title', '')}
created: {variables.get('created', '')}
modified: {variables.get('modified', '')}
type: {variables.get('type', 'note')}
---

# {variables.get('title', '')}

{variables.get('content', '')}

## 관계도
{variables.get('mermaid_diagram', '')}

## 관련 노트
"""
    
    def list_templates(self):
        """사용 가능한 템플릿 목록 반환"""
        return [f.name for f in self.template_dir.glob('*.md')]
