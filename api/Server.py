from utils.db_utils import dbsave, get_data, get_curcourses, get_completed, get_checklist, get_maincourses, set_track, delete_account
from utils.ndrims_utils import get_ndrims
from utils.recommend_utils import get_recommendations, get_cat
import json
import bcrypt
import pymysql
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from threading import Thread, Lock
from time import sleep
import uuid

progress_map = {}   # job_id -> {"step":int, "total":int, "msg":str, "done":bool, "error":str|None}
pm_lock = Lock()

def set_progress(job_id, **kwargs):
	with pm_lock:
		st = progress_map.get(job_id, {"step":0, "total":1, "msg":"", "done":False, "error":None})
		st.update(kwargs)
		progress_map[job_id] = st

app = Flask(__name__)
CORS(app)

@app.route('/login', methods=['POST'])
def login():
	sendData = []

	data = request.get_json()
	student_id = data.get("username")
	password = data.get("password")

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

	try:
		# 중복 확인
		cursor.execute("SELECT password FROM users WHERE username = %s", (student_id,))
		print(f"[Log] {student_id} : 로그인 요청 시도") #debug
		row = cursor.fetchone()
		if row:
			print(f"[Log] {student_id} : Database 사용자 찾음!") #debug
			stored_hash = row[0].encode('utf-8')
			if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
				save_dir_pattern = f"./data/{student_id}_*"
				matched_dirs = [d for d in os.listdir("./data") if d.startswith(f"{student_id}_")]

				if matched_dirs:
					folder_path = os.path.join("./data", matched_dirs[0])
					file_path = os.path.join(folder_path, "extracted_personal+info.json")
					if os.path.exists(file_path):
						with open(file_path, "r", encoding="utf-8") as f:
							sendData = json.load(f)
							print(f"[Log] {student_id} 로그인 성공!") #debug
							return jsonify({
								"status": "success",
								"data": sendData
							})
			print(f"[Log] {student_id} : 로그인 실패 (비밀번호 오류)")
			return jsonify({"status": "fail"})
		else:
			return jsonify({"status": "fail", "message": "등록되지 않은 사용자입니다."})

	except Exception as e:
		print("DB 오류:", e)
		return jsonify({"status": "fail", "message": "DB 오류"})

	finally:
		cursor.close()
		conn.close()

@app.route('/signup', methods=['POST'])
def signup():
	sendData = []

	data = request.get_json()
	student_id = data.get("username")
	password = data.get("password")
	track = data.get("track")

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

	try:
		# 중복 확인
		cursor.execute("SELECT password FROM users WHERE username = %s", (student_id,))
		print(f"[Log] {student_id} : 로그인 요청 시도") #debug
		row = cursor.fetchone()
		if row:
			print(f"[Log] {student_id} : Database 사용자 찾음!") #debug
			return jsonify({"status": "fail", "message": "이미 등록된 사용자입니다."})
		else:
			print(f"[Log] {student_id} : Database 사용자 등록되지 않음, API 실행...") #debug
			sendData = get_ndrims(student_id, password)
			if sendData.get("status") == "success":
				set_track(student_id, track)
			return jsonify(sendData)

	except Exception as e:
		print("DB 오류:", e)
		return jsonify({"status": "fail", "message": "DB 오류"})

	finally:
		cursor.close()
		conn.close()

@app.route('/data/checklist', methods=['POST'])
def get_check():
	try:
		data = request.get_json()
		student_id = data.get("student_id")
		
		print(f"[Log] {student_id} : 메인페이지 Loadding, 체크리스트 요청") #debug
		
		if not student_id:
			return jsonify({"status": "fail", "cmd": 400})

		checklist_data = get_checklist(student_id)

		if not checklist_data:
			return jsonify({"status": "fail", "cmd": 404})

		return jsonify({"status": "success", "data": checklist_data})

	except Exception as e:
		return jsonify({"status": "fail", "cmd": 500})

@app.route('/data/term', methods=['POST'])
def get_term():
	try:
		data = request.get_json()
		student_id = data.get("student_id")
		
		print(f"[Log] {student_id} : Clicked '나의 학점' 탭") #debug
		
		if not student_id:
			return jsonify({"status": "fail", "cmd": 400})

		term = get_data("term_summaries", student_id)

		if not term:
			return jsonify({"status": "fail", "cmd": 404})

		return jsonify({"status": "success", "data": term})

	except Exception as e:
		return jsonify({"status": "fail", "cmd": 500})

@app.route('/data/curcourses', methods=['POST'])
def get_curco():
	try:
		data = request.get_json()
		student_id = data.get("student_id")
		year = data.get("year")
		term = data.get("term")
		
		print(f"[Log] {student_id} : Clicked '현재 수강 강의' 탭") #debug
		
		if not student_id:
			return jsonify({"status": "fail", "cmd": 400})

		data_curcourses = get_curcourses(student_id, year, term)

		if not data_curcourses:
			return jsonify({"status": "fail", "cmd": 404})

		return jsonify({"status": "success", "data": data_curcourses})

	except Exception as e:
		return jsonify({"status": "fail", "cmd": 500})

@app.route('/data/completed', methods=['POST'])
def get_comp():
	try:
		data = request.get_json()
		student_id = data.get("student_id")
		
		print(f"[Log] {student_id} : Clicked '수강 완료 강의' 탭") #debug
		
		if not student_id:
			return jsonify({"status": "fail", "cmd": 400})

		completed_data = get_completed(student_id)

		if not completed_data:
			return jsonify({"status": "fail", "cmd": 404})

		return jsonify({"status": "success", "data": completed_data})

	except Exception as e:
		return jsonify({"status": "fail", "cmd": 500})
		
@app.route('/data/maincourses', methods=['POST'])
def get_maincour():
	try:
		data = request.get_json()
		student_id = data.get("student_id")
		
		print(f"[Log] {student_id} : 메인페이지 Loadding, Total 과목 데이터 전송..") #debug
		
		if not student_id:
			return jsonify({"status": "fail", "cmd": 400})

		maincourses = get_maincourses(student_id)

		if not maincourses:
			return jsonify({"status": "fail", "cmd": 404})

		return jsonify({"status": "success", "data": maincourses})

	except Exception as e:
		return jsonify({"status": "fail", "cmd": 500})	

@app.route('/data/mydata', methods=['POST'])
def get_mydata():
	try:
		data = request.get_json()
		student_id = data.get("student_id")
		
		print(f"[Log] {student_id} : 나의 정보 Page Loadding, 개인정보 전송..") #debug
		
		if not student_id:
			return jsonify({"status": "fail", "cmd": 400})
			
		mydata = get_data("students", student_id)[0]
		
		if not mydata:
			return jsonify({"status": "fail", "cmd": 404})
			
		return jsonify({"status": "success", "data": {"mail": mydata.get("email"), "phone": mydata.get("phone"), "track": mydata.get("track")}})
		
	except Exception as e:
		print(e)
		return jsonify({"status": "fail", "cmd": 500})

@app.route('/update/track', methods=['PATCH'])
def update_track():
	try:
		data = request.get_json()
		student_id = data.get("student_id")
		track = data.get("track")
		
		print(f"[Log] {student_id} : 나의 정보 Page, 트랙 수정 요청..") #debug
		
		if not student_id:
			return jsonify({"status": "fail", "cmd": 400})
			
		set_track(student_id, track)
		
		return jsonify({"status": "success"})
		
	except Exception as e:
		return jsonify({"status": "fail", "cmd": 500})	

@app.route('/delete', methods=['POST'])
def delete():
	try:
		data = request.get_json()
		student_id = data.get("student_id")
		password = data.get("password")
		
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
	
		try:
			# 중복 확인
			cursor.execute("SELECT password FROM users WHERE username = %s", (student_id,))
			row = cursor.fetchone()
			if row:
				stored_hash = row[0].encode('utf-8')
				if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
					print(f"[Log] {student_id} : 회원 탈퇴 API 호출..") #debug
					
					if not student_id:
						return jsonify({"status": "fail", "cmd": 400})
						
					if not password:
						return jsonify({"status": "fail", "cmd": 400})
						
					return delete_account(student_id)
					
				print(f"[Log] {student_id} : 로그인 실패 (비밀번호 오류)")
				return jsonify({"status": "fail", "message": "비밀번호를 확인해주세요."})
			else:
				return jsonify({"status": "fail", "message": "등록되지 않은 사용자입니다."})
	
		except Exception as e:
			print("DB 오류:", e)
			return jsonify({"status": "fail", "message": "DB 오류"})
	
		finally:
			cursor.close()
			conn.close()
		
	except Exception as e:
		return jsonify({"status": "fail", "cmd": 500})

@app.route('/update/ndrims_start', methods=['POST'])
def update_ndrims_start():
	try:
		data = request.get_json()
		student_id = data.get("student_id")
		password = data.get("password")

		if not student_id or not password:
			return jsonify({"status":"fail","message":"student_id/password 필요"}), 400

		conn = pymysql.connect(
			host="127.0.0.1",
			port=3306,
			user="",
			password="",
			db="",
			charset="utf8mb4"
		)
		cursor = conn.cursor()
		cursor.execute("SELECT password FROM users WHERE username = %s", (student_id,))
		row = cursor.fetchone()

		if not row:
			print(f"[Log] {student_id} : 등록되지 않은 사용자")
			return jsonify({"status": "fail", "message": "등록되지 않은 사용자입니다."}), 401

		stored_hash = row[0].encode("utf-8")
		if not bcrypt.checkpw(password.encode("utf-8"), stored_hash):
			print(f"[Log] {student_id} : 비밀번호 불일치")
			return jsonify({"status": "fail", "message": "비밀번호가 일치하지 않습니다."}), 401

		cursor.close()
		conn.close()
		print(f"[Log] {student_id} : 비밀번호 일치, 업데이트 시작 진행")

		job_id = str(uuid.uuid4())
		set_progress(job_id, step=0, total=5, msg="준비 중…", done=False, error=None)

		def worker():
			try:
				try:
					res = get_ndrims(
						student_id,
						password,
						progress_cb=lambda s, t, m: set_progress(job_id, step=s, total=t, msg=m)
					)
				except TypeError:
					set_progress(job_id, step=1, total=5, msg="포털 접속 및 로그인 중…"); sleep(1.0)
					set_progress(job_id, step=2, total=5, msg="학번/비밀번호 입력 완료"); sleep(1.0)
					set_progress(job_id, step=3, total=5, msg="로그인 완료"); sleep(1.0)
					set_progress(job_id, step=4, total=5, msg="렌더링 및 초기 준비 완료"); sleep(1.0)
					res = get_ndrims(student_id, password)
				set_progress(job_id, step=5, total=5, msg="모든 요청 수집 및 저장 완료", done=True, final=res)
			except Exception as e:
				set_progress(job_id, error=str(e), done=True)

		Thread(target=worker, daemon=True).start()
		return jsonify({"status":"accepted", "job_id": job_id}), 202

	except Exception as e:
		print("update_ndrims_start 오류:", e)
		return jsonify({"status":"fail","message":str(e)}), 500

@app.route('/update/ndrims_status', methods=['GET'])
def update_ndrims_status():
	job_id = request.args.get("job_id")
	if not job_id:
		return jsonify({"status":"fail","message":"job_id 필요"}), 400
	with pm_lock:
		st = progress_map.get(job_id)
	if not st:
		return jsonify({"status":"fail","message":"invalid job_id"}), 404
	return jsonify({"status":"success", "progress": st})

@app.route('/recommendations', methods=['POST'])
def get_recommendations_api():
	try:
		data = request.get_json()
		student_id = data.get('student_id')
		next_term = data.get('next_term')
		
		if not student_id:
			return jsonify({"status": "fail", "message": "student_id 누락"}), 400
		
		if not next_term:
			return jsonify({"status": "fail", "message": "next_term 누락"}), 400

		# 1. 전공 추천 (알고리즘 적용, 점수순 정렬)
		majors = get_recommendations(student_id, next_term)
		
		# 2. 교양 추천 (미이수 과목 필터링)
		liberal_arts = get_cat(student_id, next_term)
		
		# (오류 처리)
		if majors is None or liberal_arts is None:
			return jsonify({"status": "fail", "message": "DB 오류 발생"}), 500

		# 3. JSON으로 결합하여 반환
		return jsonify({
			"status": "success",
			"recommendations": {
				"majors": majors,
				"liberal_arts": liberal_arts
			}
		})

	except Exception as e:
		print(f"API 오류: {e}")
		return jsonify({"status": "fail", "message": f"서버 오류 발생: {e}"}), 500

if __name__ == '__main__':
	app.run(host="0.0.0.0", port=16003, ssl_context=('nexcode.kr.cer', 'nexcode.kr.key'))
