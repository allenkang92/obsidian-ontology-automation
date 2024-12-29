"""
온톨로지 시각화 도구
"""
class OntologyVisualizer:
    def generate_mermaid(self, ontology):
        """온톨로지를 Mermaid 다이어그램으로 변환"""
        nodes = set()
        edges = []
        
        # 관계에서 노드와 엣지 추출
        for rel in ontology.get('relationships', []):
            source = rel['source'].replace(' ', '_')
            target = rel['target'].replace(' ', '_')
            rel_type = rel['type']
            
            nodes.add(source)
            nodes.add(target)
            
            # 관계 유형에 따른 화살표 스타일
            if rel_type == 'is_a':
                arrow = '-->'  # 상속 관계
            elif rel_type == 'part_of':
                arrow = '-->'  # 구성 관계
            elif rel_type == 'used_for':
                arrow = '-->'  # 사용 관계
            elif rel_type == 'related_to':
                arrow = '-.->  '  # 연관 관계
            else:
                arrow = '-->'  # 기본 화살표
            
            edges.append(f'    {source}{arrow}{target}')
        
        # 노드 스타일링
        node_styles = []
        for node in nodes:
            node_styles.append(f'    style {node} fill:#f9f,stroke:#333,stroke-width:2px')
        
        # Mermaid 다이어그램 생성
        mermaid = ['```mermaid', 'graph TD']
        mermaid.extend(edges)
        mermaid.extend(node_styles)
        mermaid.append('```')
        
        return '\n'.join(mermaid)
