import os
from dotenv import load_dotenv
import google.generativeai as genai

def test_all_features():
    # 환경 변수 로드
    load_dotenv()
    
    # API 키 설정
    api_key = os.getenv('GEMINI_API_KEY')
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    
    # 테스트용 텍스트
    test_text = """
    인공지능(AI)은 인간의 학습능력과 추론능력, 지각능력, 자연언어의 이해능력 등을 컴퓨터 프로그램으로 실현한 기술이다.
    인공지능은 크게 약인공지능(Weak AI)과 강인공지능(Strong AI)으로 나눌 수 있다.
    약인공지능은 특정 분야에서만 인간의 능력을 모방하는 수준이며, 강인공지능은 인간과 같은 수준의 지능을 가진 AI를 말한다.
    최근에는 머신러닝과 딥러닝의 발전으로 인공지능의 성능이 크게 향상되었다.
    """
    
    print("=== 1. 텍스트 요약 테스트 ===")
    prompt_summary = f"다음 텍스트를 간단히 요약해주세요:\n\n{test_text}"
    response = model.generate_content(prompt_summary)
    print(response.text)
    print("\n")
    
    print("=== 2. 개념 설명 테스트 ===")
    concept = "인공지능"
    prompt_explain = f"'{concept}'이라는 개념에 대해 자세히 설명해주세요."
    response = model.generate_content(prompt_explain)
    print(response.text)
    print("\n")
    
    print("=== 3. 질문 생성 테스트 ===")
    prompt_questions = f"다음 텍스트를 바탕으로 학습 내용을 확인할 수 있는 3가지 질문을 만들어주세요:\n\n{test_text}"
    response = model.generate_content(prompt_questions)
    print(response.text)
    print("\n")
    
    print("=== 4. 키워드 추출 테스트 ===")
    prompt_keywords = f"다음 텍스트에서 중요한 키워드들을 추출하고, 각 키워드에 대해 간단히 설명해주세요:\n\n{test_text}"
    response = model.generate_content(prompt_keywords)
    print(response.text)

if __name__ == "__main__":
    test_all_features()
