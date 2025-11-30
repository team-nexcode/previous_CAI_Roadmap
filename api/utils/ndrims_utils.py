from utils.db_utils import dbsave
import time
import json
import gzip
import bcrypt
import pymysql
from io import BytesIO
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
# from flask import jsonify  # ← 삭제

def get_ndrims(student_id, password, progress_cb=None):
	total = 5
	success = 0
	sendData = []
	result = {"status": "fail", "message": "unknown"}  # 최종 반환값

	hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

	conn = pymysql.connect(
		host="127.0.0.1",
		port=3306,
		user="",
		password="",
		db="",
		charset="utf8mb4"
	)
	cursor = conn.cursor()

	personal_fields = ["DPTMJR_NM", "STD_NM", "STD_NO", "MRKS_AVG", "RSDN_DT_SEX"]

	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_argument("--no-sandbox")
	chrome_options.add_argument("--disable-dev-shm-usage")
	chrome_options.add_argument("--headless=new")
	chrome_options.add_argument("--window-size=1200,800")
	driver = webdriver.Chrome(options=chrome_options)

	os.makedirs("./data", exist_ok=True)
	os.makedirs("./debug", exist_ok=True)

	def decompress_json(content):
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
				print("\n추출된 개인정보 :")
				for k, v in item.items():
					print(f" - {k}: {v}")
		return extracted

	try:
		if progress_cb: progress_cb(1, total, "포털 접속 및 로그인 중…")

		driver.get("https://ndrims.dongguk.edu/unis/index.do")
		print("동국대 NDrims 접속 중...")

		WebDriverWait(driver, 30).until(
			lambda d: d.execute_script("return document.readyState") == "complete"
		)
		print("동국대 NDrims 렌더링 완료")

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

		if progress_cb: progress_cb(2, total, "학번/비밀번호 입력 완료")

		login_button = WebDriverWait(driver, 20).until(
			EC.element_to_be_clickable((By.XPATH, '//*[@id="uuid-2c"]/div/a'))
		)
		login_button.click()
		print("로그인 처리중...")

		time.sleep(1)

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
			result = {"status": "fail", "message": "login failed"}
			return result

		if progress_cb: progress_cb(3, total, "로그인 완료")

		time.sleep(1); print("\n1")
		time.sleep(1); print("2")
		time.sleep(1); print("3")
		time.sleep(1); print("4")
		time.sleep(1)

		driver.save_screenshot("./debug/debug_mainpage.png")
		print("debug_mainpage success.")

		time.sleep(1)

		if progress_cb: progress_cb(4, total, "렌더링 및 초기 준비 완료")

		badge_button = WebDriverWait(driver, 20).until(
			EC.element_to_be_clickable((By.XPATH, "//div[@role='treeitem' and @aria-label='학적/확인서']"))
		)
		driver.execute_script("arguments[0].click();", badge_button)
		print("\n학적/확인서 메뉴 확장됨")

		driver.save_screenshot("./debug/debug_step1.png")
		print("debug_step1 success.")

		time.sleep(0.5)

		hakjuk_button = WebDriverWait(driver, 20).until(
			EC.element_to_be_clickable((By.XPATH, "//div[@role='treeitem' and @aria-label='학적부열람']"))
		)
		driver.execute_script("arguments[0].click();", hakjuk_button)
		print("\n학적부 열람 처리됨")

		time.sleep(1); print("1")
		time.sleep(1); print("2")
		time.sleep(1); print("3")
		time.sleep(1); print("4")
		time.sleep(1)

		driver.save_screenshot("./debug/debug_step2.png")
		print("debug_step2 success.")

		time.sleep(0.5)

		sugang_tab = WebDriverWait(driver, 20).until(
			EC.element_to_be_clickable((By.XPATH, "//div[@role='tab' and text()='수강']"))
		)
		driver.requests.clear()
		driver.execute_script("arguments[0].click();", sugang_tab)
		print("\n수강 탭 열람됨")

		time.sleep(0.5)

		grade_tab = WebDriverWait(driver, 20).until(
			EC.element_to_be_clickable((By.XPATH, "//div[@role='tab' and text()='성적']"))
		)
		driver.requests.clear()
		driver.execute_script("arguments[0].click();", grade_tab)
		print("성적 탭 열람됨")
		time.sleep(0.5)

		personal_saved = False
		other_count = 0
		save_dir = "../data"

		for idx, requests in enumerate(driver.requests, start=1):
			if not requests.response:
				continue

			if "EdbStdSearchP10/doList.do" in requests.url and not personal_saved:
				data = decompress_json(requests.response.body)
				if data:
					personal_data = extract_personal_data(data, personal_fields)
					sendData = personal_data

					if personal_data and len(personal_data) > 0:
						std_no = personal_data[0].get("STD_NO", "unknown")
						std_nm = personal_data[0].get("STD_NM", "unknown")
						save_dir = f"./data/{std_no}_{std_nm}"
						os.makedirs(save_dir, exist_ok=True)

						save_json(personal_data, f"{save_dir}/extracted_personal+info.json")

						personal_saved = True

			elif "EdbStud010/doList.do" in requests.url:
				data = decompress_json(requests.response.body)
				if data:
					other_count += 1
					filename = f"{save_dir}/response_{other_count}.json"
					save_json(data, filename)

					if other_count == 3:
						dbsave(save_dir)
						if progress_cb: progress_cb(5, total, "모든 요청 수집 및 저장 완료")

		# 여기까지 오면 성공
		result = {"status": "success", "data": sendData}

	except Exception as e:
		print("❌ 오류 발생:", e)
		result = {"status": "fail", "message": str(e)}

	finally:
		print("브라우저 종료 중...")
		try:
			driver.quit()
		except:
			pass

		try:
			if success == 1:
				cursor.execute("SELECT password FROM users WHERE username = %s", (student_id,))
				row = cursor.fetchone()
				if not row:
					cursor.execute(
						"INSERT INTO users (username, password) VALUES (%s, %s)",
						(student_id, hashed_password.decode('utf-8'))
					)
					conn.commit()
		finally:
			try:
				cursor.close()
			except:
				pass
			try:
				conn.close()
			except:
				pass

	return result
