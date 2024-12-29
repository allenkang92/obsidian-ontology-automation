"""
자동 태그 생성기
"""
import re
from collections import Counter

class AutoTagger:
    def __init__(self):
        """태그 생성기 초기화"""
        self.common_words = {'및', '등', '것', '수', '는', '을', '를', '이', '가', '의', '에', '로', '와', '과', '한', '하는', '있는', '되는'}
    
    def extract_tags(self, text):
        """텍스트에서 태그 추출"""
        # 단어 추출 (한글, 영문)
        words = set()
        for word in text.split():
            # 특수문자 제거
            word = ''.join(c for c in word if c.isalnum() or c.isspace())
            if len(word) > 1 and word not in self.common_words:
                words.add(word.lower())
        
        return list(words)
    
    def suggest_tags_from_ontology(self, ontology):
        """온톨로지에서 태그 추출"""
        tags = set()
        
        # 개념들을 태그로 추가
        tags.update(ontology.get('concepts', []))
        
        # 관계에서 중요 개념 추출
        for rel in ontology.get('relationships', []):
            if rel['type'] in ['is_a', 'example_of']:
                tags.add(rel['target'])  # 상위 개념을 태그로
        
        return list(tags)
    
    def extract_keywords(self, text):
        """텍스트에서 키워드 추출"""
        # 불용어 제거 및 단어 빈도수 계산
        words = re.findall(r'\b\w+\b', text.lower())
        word_freq = Counter(words)
        
        # 상위 10개 키워드 반환
        return [word for word, _ in word_freq.most_common(10)]
    
    def combine_tags(self, text_tags, ontology_tags, keywords):
        """여러 소스에서 추출한 태그들을 결합하고 우선순위화"""
        all_tags = []
        
        # 온톨로지 태그를 가장 높은 우선순위로
        all_tags.extend(ontology_tags)
        
        # AI가 추출한 태그를 다음 우선순위로
        all_tags.extend([tag for tag in text_tags if tag not in all_tags])
        
        # 키워드를 마지막 우선순위로
        all_tags.extend([tag for tag in keywords if tag not in all_tags])
        
        return list(dict.fromkeys(all_tags))  # 중복 제거하면서 순서 유지
