import time
import json
import gzip
from io import BytesIO
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

# --- 학번/비밀번호 설정 ---
student_id = ""
password = ""

personal_fields = ["DPTMJR_NM", "STD_NM", "MRKS_AVG", "RSDN_DT_SEX"]

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--headless=new")  # 헤드레스 모드
chrome_options.add_argument("--window-size=1200,800")  # 헤드레스에서 화면 크기 지정

driver = webdriver.Chrome(options=chrome_options)

os.makedirs("./data", exist_ok=True)

def decompress_json(content):
    """gzip 해제 후 JSON 반환"""
    try:
        try:
            content = gzip.GzipFile(fileobj=BytesIO(content)).read()
        except:
            pass
        return json.loads(content.decode("utf-8"))
    except Exception as e:
        print("❌ JSON 디코딩 오류:", e)
        return None

def save_json(data, filepath):
    """JSON 파일로 저장"""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 저장 완료 → {filepath}")
    except Exception as e:
        print("❌ JSON 저장 오류:", e)

def extract_personal_data(data, fields):
    extracted = []
    if "dsMain" in data:
        for record in data["dsMain"]:
            item = {k: record.get(k, None) for k in fields}
            extracted.append(item)
            # 터미널 출력
            print("\n📌 개인정보 추출:")
            for k, v in item.items():
                print(f" - {k}: {v}")
    return extracted

# --- 메인 동작 ---
try:
    driver.get("https://ndrims.dongguk.edu/unis/index.do")
    print("동국대 NDrims 접속 중...")
    
    WebDriverWait(driver, 30).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    print("동국대 NDrims 렌더링 완료")
    
    time.sleep(2)

    # 아이디/비밀번호 입력
    id_input = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[data-ndid="3e"]'))
    )
    id_input.send_keys(student_id)
    print("학번 입력됨")
    pw_input = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[data-ndid="3g"]'))
    )
    pw_input.send_keys(password)
    print("비밀번호 입력됨")

    # 로그인 버튼
    login_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="uuid-2c"]/div/a'))
    )
    login_button.click()
    print("로그인 처리중...")
    
    time.sleep(1)

    # 팝업 처리
    try:
        popup_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//a[.//div[text()='확인']]"))
        )
        popup_button.click()
        print("팝업 처리 완료\n")
    except:
        print("팝업 감지 안됨, PASS\n")
    
    time.sleep(1)
    
    if "login" not in driver.current_url.lower():
        print("✅ 로그인 성공! (학생인증 성공)")
    else:
        print("❌ 로그인 실패!")
        
    time.sleep(1)
    print("\n1")
    time.sleep(1)
    print("2")
    time.sleep(1)
    print("3")
    time.sleep(1)

    # 학적/확인서 메뉴 확장
    badge_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "div.cl-badge[data-ndid='g2']"))
    )
    driver.execute_script("arguments[0].click();", badge_button)
    print("\n학적/확인서 메뉴 확장됨")
    
    time.sleep(0.5)

    # 학적부 열람
    hakjuk_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "div.cl-tree-item[data-ndid='g5']"))
    )
    driver.execute_script("arguments[0].click();", hakjuk_button)
    print("학적부 열람 처리됨")
    
    time.sleep(3)

    # 수강 탭 열람
    sugang_tab = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@role='tab' and text()='수강']"))
    )
    driver.requests.clear()
    driver.execute_script("arguments[0].click();", sugang_tab)
    print("수강 탭 열람됨")
    
    time.sleep(1)

    # 성적 탭 열람
    grade_tab = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@role='tab' and text()='성적']"))
    )
    driver.requests.clear()
    driver.execute_script("arguments[0].click();", grade_tab)
    print("성적 탭 열람됨")
    
    time.sleep(1)

    # 모든 요청 확인 및 저장
    personal_saved = False
    other_count = 0
    for idx, request in enumerate(driver.requests, start=1):
        if not request.response:
            continue

        # 개인정보 응답
        if "EdbStdSearchP10/doList.do" in request.url and not personal_saved:
            data = decompress_json(request.response.body)
            if data:
                personal_data = extract_personal_data(data, personal_fields)
                save_json(personal_data, "./data/extracted_personal_info.json")
                personal_saved = True

        # 수강/성적 탭 응답
        elif "EdbStud010/doList.do" in request.url:
            data = decompress_json(request.response.body)
            if data:
                other_count += 1
                filename = f"./data/response_{other_count}.json"
                save_json(data, filename)

except Exception as e:
    print("❌ 오류 발생:", e)

finally:
    print("브라우저 종료 중...")
    driver.quit()
