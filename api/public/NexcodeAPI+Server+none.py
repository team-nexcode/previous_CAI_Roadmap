import time
import json
import gzip
from io import BytesIO
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/login', methods=['POST'])
def login():
	success = 0
	sendData = ""
	
	data = request.get_json()
	student_id = data.get("username")
	password = data.get("password")
	
	personal_fields = ["DPTMJR_NM", "STD_NM", "STD_NO", "MRKS_AVG", "RSDN_DT_SEX"]
	
	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_argument("--no-sandbox")
	chrome_options.add_argument("--disable-dev-shm-usage")
	chrome_options.add_argument("--headless=new")
	chrome_options.add_argument("--window-size=1200,800")
	
	
	driver = webdriver.Chrome(options=chrome_options)
	
	os.makedirs("./data", exist_ok=True)
	os.makedirs("./debug", exist_ok=True)
	
	def decompress_json(content): #gzip Decompress 처리
	    try:
	        try:
	            content = gzip.GzipFile(fileobj=BytesIO(content)).read()
	        except:
	            pass
	        return json.loads(content.decode("utf-8"))
	    except Exception as e:
	        print("JSON 디코딩 오류 :", e)
	        return None
	
	def save_json(data, filepath):
	    try:
	        with open(filepath, "w", encoding="utf-8") as f:
	            json.dump(data, f, ensure_ascii=False, indent=2)
	        print(f"저장 완료 → {filepath}")
	    except Exception as e:
	        print("JSON 저장 오류 :", e)
	
	def extract_personal_data(data, fields):
	    extracted = []
	    if "dsMain" in data:
	        for record in data["dsMain"]:
	            item = {k: record.get(k, None) for k in fields}
	            extracted.append(item)
	            # 터미널 출력
	            print("\n추출된 개인정보 :")
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
	    
	    if "main.clx" in driver.current_url.lower():
	        print("✅ 로그인 성공! (학생인증 성공)")
	        success = 1
	    else:
	        print("❌ 로그인 실패!")
	        sendData = "fail"
	        return jsonify({"status": "fail"})
	        
	    time.sleep(1)
	    print("\n1")
	    time.sleep(1)
	    print("2")
	    time.sleep(1)
	    print("3")
	    time.sleep(1)
	    print("4")
	    time.sleep(1)
	
	    driver.save_screenshot("./debug/debug_mainpage.png")
	    print("debug_mainpage success.")
	
	    time.sleep(1)
	
	    # 학적/확인서 메뉴 확장
	    badge_button = WebDriverWait(driver, 20).until(
	        EC.element_to_be_clickable((By.XPATH, "//div[@role='treeitem' and @aria-label='학적/확인서']"))
	    )
	    driver.execute_script("arguments[0].click();", badge_button)
	    print("\n학적/확인서 메뉴 확장됨")
	    
	    driver.save_screenshot("./debug/debug_step1.png")
	    print("debug_step1 success.")
	    
	    time.sleep(0.5)
	
	    # 학적부 열람
	    hakjuk_button = WebDriverWait(driver, 20).until(
	        EC.element_to_be_clickable((By.XPATH, "//div[@role='treeitem' and @aria-label='학적부열람']"))
	    )
	    driver.execute_script("arguments[0].click();", hakjuk_button)
	    print("\n학적부 열람 처리됨")
	    
	    time.sleep(1)
	    print("1")
	    time.sleep(1)
	    print("2")
	    time.sleep(1)
	    print("3")
	    time.sleep(1)
	    print("4")
	    time.sleep(1)
	
	    driver.save_screenshot("./debug/debug_step2.png")
	    print("debug_step2 success.")
	    
	    time.sleep(0.5)
	
	    # 수강 탭 열람
	    sugang_tab = WebDriverWait(driver, 20).until(
	        EC.element_to_be_clickable((By.XPATH, "//div[@role='tab' and text()='수강']"))
	    )
	    driver.requests.clear()
	    driver.execute_script("arguments[0].click();", sugang_tab)
	    print("\n수강 탭 열람됨")
	    
	    time.sleep(0.5)
	
	    # 성적 탭 열람
	    grade_tab = WebDriverWait(driver, 20).until(
	        EC.element_to_be_clickable((By.XPATH, "//div[@role='tab' and text()='성적']"))
	    )
	    driver.requests.clear()
	    driver.execute_script("arguments[0].click();", grade_tab)
	    print("성적 탭 열람됨")
	    time.sleep(0.5)
	
	    # 모든 요청 확인 및 저장
	    personal_saved = False
	    other_count = 0
	    for idx, requests in enumerate(driver.requests, start=1):
	        if not requests.response:
	            continue
	
	        # 개인정보 응답
	        if "EdbStdSearchP10/doList.do" in requests.url and not personal_saved:
	            data = decompress_json(requests.response.body)
	            if data:
	                personal_data = extract_personal_data(data, personal_fields)
	                sendData = personal_data
	                save_json(personal_data, "./data/extracted_personal_info.json")
	                personal_saved = True
	
	        # 수강/성적 탭 응답
	        elif "EdbStud010/doList.do" in requests.url:
	            data = decompress_json(requests.response.body)
	            if data:
	                other_count += 1
	                filename = f"./data/response_{other_count}.json"
	                save_json(data, filename)
	    
	except Exception as e:
	    print("❌ 오류 발생:", e)
	
 
	finally:
		print("\n< 요청자에게로의 응답 >")
		print(sendData)
		print("\n브라우저 종료 중...\n")
		driver.quit()
	
	if success == 1:
	    return jsonify({
	        "status": "success",
	        "data": sendData
	        })

if __name__ == '__main__':
	app.run(host="0.0.0.0", port=16003, ssl_context=('nexcode.kr.cer', 'nexcode.kr.key'))

