"""
옵시디언 노트 관리 및 연결 관리자
"""
import os
from pathlib import Path
import frontmatter
import yaml
import re
from datetime import datetime

class NoteManager:
    def __init__(self, vault_path):
        self.vault_path = Path(vault_path)
        
    def create_note(self, title, content, metadata=None):
        """새로운 노트 생성"""
        # 파일명 생성 (공백은 -로 변환)
        filename = f"{title.replace(' ', '-')}.md"
        filepath = self.vault_path / filename
        
        # 기본 메타데이터 설정
        if metadata is None:
            metadata = {}
        
        metadata.update({
            'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'modified': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        # frontmatter와 내용을 합쳐서 파일 생성
        note_content = frontmatter.Post(content, **metadata)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(note_content))
            
        return filepath
    
    def update_note(self, filepath, content=None, metadata=None):
        """기존 노트 업데이트"""
        with open(filepath, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        if content is not None:
            post.content = content
        
        if metadata is not None:
            post.metadata.update(metadata)
        
        post.metadata['modified'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
    
    def add_links(self, source_path, target_titles, bidirectional=True):
        """노트 간 링크 추가"""
        with open(source_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        content = post.content
        
        # 각 타겟에 대해 링크 추가
        for title in target_titles:
            if not self._has_link(content, title):
                # 관련 노트 섹션 찾기 또는 생성
                if '## 관련 노트' not in content:
                    content += '\n\n## 관련 노트\n'
                
                # 링크 추가
                content += f'- [[{title}]]\n'
        
        post.content = content
        
        # 파일 저장
        with open(source_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
        
        # 양방향 링크 생성
        if bidirectional:
            for title in target_titles:
                target_path = self.vault_path / f"{title.replace(' ', '-')}.md"
                if target_path.exists():
                    self._add_backlink(target_path, Path(source_path).stem)
    
    def _has_link(self, content, title):
        """특정 제목에 대한 링크가 이미 존재하는지 확인"""
        pattern = f"\\[\\[{title}\\]\\]"
        return bool(re.search(pattern, content))
    
    def _add_backlink(self, target_path, source_title):
        """역방향 링크 추가"""
        with open(target_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        content = post.content
        
        if not self._has_link(content, source_title):
            if '## 관련 노트' not in content:
                content += '\n\n## 관련 노트\n'
            content += f'- [[{source_title}]]\n'
        
        post.content = content
        
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
    
    def create_note_from_ontology(self, title, content, ontology):
        """온톨로지 정보를 포함한 새 노트 생성"""
        # YAML frontmatter 생성
        metadata = {
            'title': title,
            'concepts': ontology.get('concepts', []),
            'relationships': ontology.get('relationships', [])
        }
        
        # 노트 생성
        filepath = self.create_note(title, content, metadata)
        
        # 관련 노트들과 자동으로 링크 생성
        related_titles = []
        for rel in ontology.get('relationships', []):
            if rel['source'] == title:
                related_titles.append(rel['target'])
            elif rel['target'] == title:
                related_titles.append(rel['source'])
        
        if related_titles:
            self.add_links(filepath, related_titles)
        
        return filepath
