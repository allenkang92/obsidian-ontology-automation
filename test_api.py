import os
from dotenv import load_dotenv
import google.generativeai as genai

def test_gemini_api():
    # 환경 변수 로드
    load_dotenv()
    
    # API 키 가져오기
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key or api_key == 'your_api_key_here':
        print("Error: GEMINI_API_KEY가 설정되지 않았습니다.")
        print("'.env' 파일에서 API 키를 설정해주세요.")
        return
    
    try:
        # Gemini API 설정
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # 간단한 테스트 실행
        test_text = "안녕하세요! 간단한 테스트입니다."
        response = model.generate_content(test_text)
        
        print("=== API 테스트 결과 ===")
        print("입력:", test_text)
        print("출력:", response.text)
        print("\nAPI 연결이 성공적으로 작동합니다!")
        
    except Exception as e:
        print("API 연결 중 오류가 발생했습니다:")
        print(str(e))

if __name__ == "__main__":
    test_gemini_api()
