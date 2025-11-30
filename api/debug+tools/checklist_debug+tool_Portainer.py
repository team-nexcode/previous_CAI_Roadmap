import requests
import json

API_URL = ""

def test_checklist_api():

    try:
        student_id = input("▶︎ 조회할 학번을 입력하세요 (예: 2025000001): ").strip()
        if not student_id:
            print("❗️ 학번이 입력되지 않았습니다. 프로그램을 종료합니다.")
            return
        
        payload = {
            "student_id": student_id
        }

        print(f"\n⏳ '{API_URL}' 주소로 학번 '{student_id}'의 데이터를 요청합니다...")

        response = requests.post(API_URL, json=payload, timeout=10, verify=False)

        response.raise_for_status()

        data = response.json()

        print("✅ 요청 성공! 아래는 서버로부터 받은 응답입니다.")
        print("-" * 50)
        
        pretty_json = json.dumps(data, indent=4, ensure_ascii=False)
        print(pretty_json)
        print("-" * 50)

    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP 에러 발생: {e.response.status_code} {e.response.reason}")
        print("서버에서 오류 응답을 보냈습니다. 응답 내용:", e.response.text)
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 중 에러 발생: {e}")
        print("네트워크 연결 상태나 URL을 확인해 주세요.")
    except json.JSONDecodeError:
        print("❌ JSON 파싱 에러: 서버가 유효한 JSON 형식을 반환하지 않았습니다.")
        print("서버 응답 내용:", response.text)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_checklist_api()
