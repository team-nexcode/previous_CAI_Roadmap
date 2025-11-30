import json, os, pymysql
from flask import jsonify
from datetime import datetime

def get_db():
	return pymysql.connect(
		host="127.0.0.1",
		port=3306,
		user="",
		password="",
		db="",
		charset="utf8mb4"
	)
	
def upsert_student(cur, student_id, bas, college, faculty, major, birth):
	sql = """
	INSERT INTO students
		(student_id, name, email, phone, sex, campus, entry_date, entry_yy_sem, foreign_yn,
		club_name, address_full, bank_name, bank_account_enc, level_test_teps, deep_yn,
		ENT_TOPIK_GRD_CD_NM, GRAD_TOPIK_GRD_CD_NM, GRAD_TOPIK_GAIN_DT, ENT_TOPIK_GAIN_DT,
		colleges, faculties, majors, birth)
	VALUES
		(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,AES_ENCRYPT(%s, %s),%s,%s,
		%s, %s, %s, %s,
		%s, %s, %s, %s) 
	ON DUPLICATE KEY UPDATE
		name=VALUES(name), email=VALUES(email), phone=VALUES(phone),
		sex=VALUES(sex), campus=VALUES(campus), entry_date=VALUES(entry_date),
		entry_yy_sem=VALUES(entry_yy_sem), foreign_yn=VALUES(foreign_yn),
		club_name=VALUES(club_name), address_full=VALUES(address_full),
		bank_name=VALUES(bank_name), bank_account_enc=VALUES(bank_account_enc),
		level_test_teps=VALUES(level_test_teps), deep_yn=VALUES(deep_yn),
		ENT_TOPIK_GRD_CD_NM=VALUES(ENT_TOPIK_GRD_CD_NM),
		GRAD_TOPIK_GRD_CD_NM=VALUES(GRAD_TOPIK_GRD_CD_NM),
		GRAD_TOPIK_GAIN_DT=VALUES(GRAD_TOPIK_GAIN_DT),
		ENT_TOPIK_GAIN_DT=VALUES(ENT_TOPIK_GAIN_DT),
		colleges=VALUES(colleges), faculties=VALUES(faculties),
		majors=VALUES(majors), birth=VALUES(birth);
	"""
	params = (
		int(student_id), bas.get("DPSTR_NM"), bas.get("EMAIL"), bas.get("HP_NO"),
		bas.get("SEX_CD_NM"), bas.get("CAMPUS_NM"), bas.get("ENT_DT") if bas.get("ENT_DT") else None,
		bas.get("ENT_YY_SEM"), bas.get("FORGN_YN"), bas.get("CLUB_NM"),
		bas.get("ADDR"), bas.get("BANK_CD_NM"), (bas.get("BANK_ACC_NO") or "").strip() or None,
		"your-32byte-key", bas.get("LEVEL_TEST_TEPS"), bas.get("DEEP_YN"),
		bas.get("ENT_TOPIK_GRD_CD_NM"), bas.get("GRAD_TOPIK_GRD_CD_NM"),
		bas.get("GRAD_TOPIK_GAIN_DT") or None, bas.get("ENT_TOPIK_GAIN_DT") or None,
		college, faculty, major, birth,
	)
	cur.execute(sql, params)

def ensure_term(cur, year, sem_cd, yy_sem_name):
	if not (year and sem_cd): return
	if not yy_sem_name:
		yy_sem_name = f"{year}-{sem_cd}"
		
	sql = """
	INSERT INTO terms (year, sem_cd, yy_sem_name)
	VALUES (%s,%s,%s)
	ON DUPLICATE KEY UPDATE yy_sem_name=VALUES(yy_sem_name);
	"""
	cur.execute(sql, (int(year), sem_cd, yy_sem_name))

def upsert_course(cur, row):
	course_key = f"{row.get('SBJ_NO')}:{row.get('DVCLS')}:{row.get('OPEN_YY')}:{row.get('OPEN_SEM_CD')}"
	sql = """
	INSERT INTO courses
		(course_key, sbj_no, dvcls, name, cpdv_nm, dept_all_nm, dpt_nm, colg_nm, cors_nm,
		detl_curi_nm, main_prof_nm, credit, open_year, sem_cd, open_yy_sem, timetable,
		recrs_recod_yn, sys_ins_dttm)
	VALUES
		(%s,%s,%s,%s,%s,%s,%s,%s,%s,
		%s,%s,%s,%s,%s,%s,%s,%s,%s)
	ON DUPLICATE KEY UPDATE
		name=VALUES(name),
		cpdv_nm=VALUES(cpdv_nm),
		dept_all_nm=VALUES(dept_all_nm),
		dpt_nm=VALUES(dpt_nm),
		colg_nm=VALUES(colg_nm),
		cors_nm=VALUES(cors_nm),
		detl_curi_nm=VALUES(detl_curi_nm),
		main_prof_nm=VALUES(main_prof_nm),
		credit=VALUES(credit),
		open_year=VALUES(open_year),
		sem_cd=VALUES(sem_cd),
		open_yy_sem=VALUES(open_yy_sem),
		timetable=VALUES(timetable),
		recrs_recod_yn=VALUES(recrs_recod_yn),
		sys_ins_dttm=VALUES(sys_ins_dttm);
	"""
	cur.execute(sql, (
		course_key,
		row.get("SBJ_NO"),
		row.get("DVCLS"),
		row.get("SBJ_NM"),
		row.get("CPDIV_NM"),
		row.get("DEPT_ALL_NM"),
		row.get("DPT_NM"),
		row.get("COLG_NM"),
		row.get("CORS_NM"),
		row.get("DETL_CURI_NM"),
		row.get("MAIN_PROF_NM"),
		float(row["CDT"]) if row.get("CDT") else None,
		int(row["OPEN_YY"]) if row.get("OPEN_YY") else None,
		row.get("OPEN_SEM_CD"),
		row.get("OPEN_YY_SEM"),
		row.get("TMTBL_KOR_DSC"),
		row.get("RECRS_RECOD_YN"),
		row.get("SYS_INS_DTTM"),
	))
	return course_key

def upsert_enrollment(cur, student_id, course_key, year, sem_cd, open_yy_sem, status, grade_cd, credit):
	sql = """
	INSERT INTO enrollments
		(student_id, course_key, year, sem_cd, open_yy_sem, status, grade_cd, credit)
	VALUES
		(%s,%s,%s,%s,%s,%s,%s,%s)
	ON DUPLICATE KEY UPDATE
		grade_cd=VALUES(grade_cd),
		credit=VALUES(credit),
		open_yy_sem=VALUES(open_yy_sem);
	"""
	cur.execute(sql, (
		int(student_id), course_key, int(year), sem_cd, open_yy_sem, status, grade_cd,
		float(credit) if credit is not None else None
	))

def upsert_term_summary(cur, student_id, year, sem_cd, yy_sem_name=None,
						applied=None, gained=None, gpa=None,
						rank_text=None, dept_rank=None, per_sco=None):
	if not yy_sem_name:
		yy_sem_name = f"{year}-{sem_cd}"
	sql = """
	INSERT INTO term_summaries
		(student_id, year, sem_cd, yy_sem_name, applied_cdt, gained_cdt, gpa, rank_text, dept_rank, per_sco)
	VALUES
		(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
	ON DUPLICATE KEY UPDATE
		applied_cdt = VALUES(applied_cdt),
		gained_cdt  = VALUES(gained_cdt),
		gpa         = VALUES(gpa),
		rank_text   = VALUES(rank_text),
		dept_rank   = VALUES(dept_rank),
		per_sco     = VALUES(per_sco);
	"""
	cur.execute(sql, (
		int(student_id), int(year), sem_cd, yy_sem_name,
		float(applied) if applied is not None else None,
		float(gained) if gained is not None else None,
		float(gpa) if gpa is not None else None,
		rank_text, dept_rank,
		float(per_sco) if per_sco is not None else None
	))

def parse_department(full_name):
	"""'~대학 ~학부 ~전공' 형태의 문자열을 분리하여 딕셔너리로 반환합니다."""
	if not full_name:
		return {'college': None, 'faculty': None, 'major': None}

	parts = {'college': None, 'faculty': None, 'major': None}
	remaining_str = full_name

	college_kw = "대학"
	if college_kw in remaining_str:
		idx = remaining_str.find(college_kw)
		parts['college'] = remaining_str[:idx + len(college_kw)].strip()
		remaining_str = remaining_str[idx + len(college_kw):].strip()

	faculty_kw = "학부"
	if faculty_kw in remaining_str:
		idx = remaining_str.find(faculty_kw)
		parts['faculty'] = remaining_str[:idx + len(faculty_kw)].strip()
		remaining_str = remaining_str[idx + len(faculty_kw):].strip()
	else:
		faculty_kw = "학과"
		if faculty_kw in remaining_str:
			idx = remaining_str.find(faculty_kw)
			parts['faculty'] = remaining_str[:idx + len(faculty_kw)].strip()
			remaining_str = remaining_str[idx + len(faculty_kw):].strip()

	if remaining_str:
		parts['major'] = remaining_str.strip()
		
	return parts

def dbsave(student_dir):
	# -------- DB 연결 --------
	# get_db() 또는 직접 연결 코드를 사용하세요.
	# conn = get_db() 
	conn = pymysql.connect(
		host="127.0.0.1", port=3306, user="",
		password="", db="", charset="utf8mb4"
	)
	cur = conn.cursor()

	try:
		# -------- JSON 로드 --------
		# 1. 응답 파일(response_1, 2, 3) 로드
		res_files = ["response_1.json", "response_2.json", "response_3.json"]
		res_list = []
		for fname in res_files:
			fpath = os.path.join(student_dir, fname)
			if not os.path.exists(fpath):
				raise FileNotFoundError(f"{fpath} 파일이 존재하지 않습니다.")
			with open(fpath, "r", encoding="utf-8") as f:
				res_list.append(json.load(f))
		
		res1, res2, res3 = res_list
		
		# 2. [추가] 개인정보 파일(extracted_personal+info.json) 로드
		personal_info_path = os.path.join(student_dir, "extracted_personal+info.json")
		if not os.path.exists(personal_info_path):
			raise FileNotFoundError(f"{personal_info_path} 파일이 존재하지 않습니다.")
		with open(personal_info_path, "r", encoding="utf-8") as f:
			personal_info_list = json.load(f)

		# -------- 데이터 처리 및 DB 저장 --------
		# 1) 학번(student_id) 추출
		rec_list = res3.get("dsMainRec", [])
		if not rec_list:
			raise RuntimeError("dsMainRec가 비어 있어 학번 추출 불가")
		student_id = rec_list[0].get("STD_NO")
		if not student_id:
			raise RuntimeError("STD_NO 없음")
		
		# 2) 학생 기본사항 처리 및 upsert
		bas = (res1.get("dsMainBas") or [{}])[0]
		personal_data = (personal_info_list or [{}])[0]
		
		# [추가] 학과/전공 및 생년월일 데이터 파싱
		department_full_name = personal_data.get("DPTMJR_NM")
		parsed_dept = parse_department(department_full_name) # parse_department 함수 호출
		
		rsdn_dt_sex_full = personal_data.get("RSDN_DT_SEX")
		birth_value = rsdn_dt_sex_full.split('(')[0] if rsdn_dt_sex_full else None

		# [수정] 파싱된 모든 정보를 인자로 전달하여 upsert_student 호출
		upsert_student(
			cur,
			student_id,
			bas,
			college=parsed_dept['college'],
			faculty=parsed_dept['faculty'],
			major=parsed_dept['major'],
			birth=birth_value
		)
		
		# 3) term 마스터
		for t in res2.get("dsMainTkcrsYy", []):
			yy, sem_cd = t.get("YY"), t.get("SEM_CD")
			if yy and sem_cd and yy.isdigit():
				ensure_term(cur, int(yy), sem_cd, t.get("YY_SEM"))
		
		# 4) 수강신청/수강중
		for c in res2.get("dsMainTkcrs", []):
			course_key = upsert_course(cur, c)
			yy = c.get("OPEN_YY")
			sem_cd = c.get("OPEN_SEM_CD")
			if yy and sem_cd:
				ensure_term(cur, int(yy), sem_cd, c.get("OPEN_YY_SEM"))
			upsert_enrollment(
				cur,
				student_id=student_id,
				course_key=course_key,
				year=int(yy) if yy and yy.isdigit() else None,
				sem_cd=sem_cd,
				open_yy_sem=c.get("OPEN_YY_SEM"),
				status="registered",
				grade_cd=None,
				credit=c.get("CDT")
			)
		
		# 5) 성적(이수 완료)
		for r in res3.get("dsMainRec", []):
			open_yy_sem = r.get("OPEN_YY_SEM")
			year_str = open_yy_sem.split("-")[0] if open_yy_sem and "-" in open_yy_sem else r.get("YY")
			year = int(year_str) if year_str and year_str.isdigit() else None
			sem_cd = r.get("SEM_CD")
			dvcls = r.get("DVCLS")
			sbj_no = r.get("SBJ_NO")
			course_row_min = {
				"SBJ_NO": sbj_no, "DVCLS": dvcls, "SBJ_NM": r.get("SBJ_NM"),
				"CPDIV_NM": r.get("CPDIV_CD"), "DEPT_ALL_NM": r.get("ADMT_RECOD_CLSF_NM"),
				"DPT_NM": None, "COLG_NM": None, "CORS_NM": None,
				"DETL_CURI_NM": r.get("DETL_CUTI_CD"), "MAIN_PROF_NM": r.get("EMP_NM"),
				"CDT": r.get("CDT"), "OPEN_YY": year, "OPEN_SEM_CD": sem_cd,
				"OPEN_YY_SEM": open_yy_sem, "TMTBL_KOR_DSC": None,
				"RECRS_RECOD_YN": r.get("RECRS_YY_SEM"), "SYS_INS_DTTM": None
			}
			course_key = upsert_course(cur, course_row_min)
			if year and sem_cd:
				ensure_term(cur, year, sem_cd, open_yy_sem or (str(year)))
			upsert_enrollment(
				cur,
				student_id=student_id,
				course_key=course_key,
				year=year,
				sem_cd=sem_cd,
				open_yy_sem=open_yy_sem or "",
				status="completed",
				grade_cd=r.get("RECOD_GRD_CD"),
				credit=r.get("CDT")
			)
		
		# 6) 학기별 요약
		for s in res3.get("dsMainRecYySem", []):
			if s.get("YY") == "%" or s.get("SEM_CD") == "%" or not s.get("YY").isdigit():
				continue
			upsert_term_summary(
				cur,
				student_id=student_id,
				year=int(s["YY"]),
				sem_cd=s["SEM_CD"],
				yy_sem_name=s.get("YY_SEM_NM"),
				applied=s.get("APPL_CDT"),
				gained=s.get("GAIN_CDT"),
				gpa=s.get("AVG_MRK")
			)

		for ss in res3.get("dsSubRec", []):
			if ss.get("SEM_CD") and ss.get("YY").isdigit():
				upsert_term_summary(
					cur,
					student_id=student_id,
					year=int(ss["YY"]),
					sem_cd=ss.get("SEM_CD"),
					applied=ss.get("APPL_CDT"),
					gained=ss.get("GAIN_CDT"),
					gpa=ss.get("AVG_MRK"),
					rank_text=ss.get("RANK"),
					dept_rank=ss.get("DPT_RANK"),
					per_sco=ss.get("PER_SCO")
				)
			
		conn.commit()
		print(f"학번 {student_id} 데이터 저장 완료!")

	except Exception as e:
		if conn:
			conn.rollback()
		# 오류 내용을 출력하거나 로깅
		print(f"학번 {student_id if 'student_id' in locals() else 'Unknown'} 처리 중 오류: {e}")
		# 오류를 상위로 전달하여 API가 처리하게 함
		raise

	finally:
		if conn:
			cur.close()
			conn.close()

def get_data(table, student_id):
	try:
		conn = get_db()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		sql = f"SELECT * FROM {table} WHERE student_id = %s"
		cursor.execute(sql, (student_id,))
		result = cursor.fetchall()
		return result
	except Exception as e:
		print("get_data 오류:", e)
		return None
	finally:
		cursor.close()
		conn.close()

def get_curcourses(student_id, year, term):
	"""
	특정 학생의 현재 수강 중인 과목('2025-2학기', 'registered') 정보를
	여러 DB와 테이블을 JOIN하여 조회합니다.
	"""
	conn = None
	cursor = None
	try:
		conn = get_db()
		cursor = conn.cursor(pymysql.cursors.DictCursor)

		sql = f"""
			SELECT
				c.name,
				c.main_prof_nm,
				c.credit,
				c.timetable,
				c2.ROOM_KOR_DSC,
				c.sbj_no,
				c.dvcls,
				c.cpdv_nm
			FROM
				test.enrollments AS e
			INNER JOIN
				test.courses AS c ON e.course_key = c.course_key
			INNER JOIN
				courses.courses_{year}term{term} AS c2 ON c.sbj_no = c2.SBJ_NO COLLATE utf8mb4_general_ci 
				AND c.dvcls = c2.DVCLS COLLATE utf8mb4_general_ci
			WHERE
				e.student_id = %s
				AND e.open_yy_sem = '{year}-{term}학기'
				AND e.status = 'registered'
		"""
		params = (student_id,)
		cursor.execute(sql, params)
		result = cursor.fetchall()
		return result
	except Exception as e:
		print(f"get_curcourses 함수 오류: {e}")
		return None
	finally:
		if cursor:
			cursor.close()
		if conn:
			conn.close()

def get_completed(student_id):
	"""
	특정 학생이 이수 완료(completed)한 과목들의 상세 정보를 DB에서 조회합니다.
	enrollments와 courses 테이블을 JOIN하여 두 테이블의 정보를 모두 반환합니다.
	"""
	conn = None
	cursor = None
	try:
		conn = get_db()
		cursor = conn.cursor(pymysql.cursors.DictCursor)

		sql = """
			SELECT
				e.open_yy_sem,
				e.year,
				e.grade_cd,
				e.credit,
				c.sbj_no,
				c.dvcls,
				c.name,
				c.cpdv_nm,
				c.main_prof_nm
			FROM
				enrollments AS e
			INNER JOIN
				courses AS c ON e.course_key = c.course_key
			WHERE
				e.student_id = %s AND e.status = %s
		"""
		params = (student_id, 'completed')
		cursor.execute(sql, params)
		result = cursor.fetchall()
		return result
	except Exception as e:
		print(f"get_completed 함수 오류: {e}")
		return None
	finally:
		if cursor:
			cursor.close()
		if conn:
			conn.close()
			
def get_enrolled(student_id):
	conn = None
	cursor = None
	try:
		conn = get_db()
		cursor = conn.cursor(pymysql.cursors.DictCursor)

		sql = """
			SELECT
				e.open_yy_sem,
				e.year,
				e.grade_cd,
				e.credit,
				c.sbj_no,
				c.dvcls,
				c.name,
				c.cpdv_nm,
				c.main_prof_nm
			FROM
				enrollments AS e
			INNER JOIN
				courses AS c ON e.course_key = c.course_key
			WHERE
				e.student_id = %s AND e.status = %s
		"""
		params = (student_id, 'registered')
		cursor.execute(sql, params)
		result = cursor.fetchall()
		return result
	except Exception as e:
		print(f"get_completed 함수 오류: {e}")
		return None
	finally:
		if cursor:
			cursor.close()
		if conn:
			conn.close()

def get_checklist(student_id):
	conn = None
	cursor = None
	# 최종적으로 반환할 result 딕셔너리를 모든 키와 함께 0으로 초기화합니다.
	result = {
		'major': 0.0,       # 전공 이수 학점
		'common': 0.0,      # 공통교양 이수 학점
		'gpa': 0.0,         # 전체 평점 평균
		'total_credit': 0.0,# F 제외 총 취득 학점
		'eng_credit': 0,    # 영어(외국어) 강의 이수 개수
		'basic': 0,         # 기본소양 이수 개수
		'bsm': 0,           # BSM 과목
		'design1': 0,       # 종합설계1 이수 여부 (1 or 0)
		'design2': 0,        # 종합설계2 이수 여부 
		'basic_completed': False,  # 기본소양 과목 두 개 이상 이수 여부 (불린 값)
		'missing_basic_courses': [],  # 수강하지 않은 기본소양 과목 목록
		'bsm_completed': False,  # BSM 과목 두 개 이상 이수 여부 (불린 값)
		'missing_bsm_courses': [],  # 수강하지 않은 BSM 과목 목록
		'experiment_course_status': "",
		'common_dongguk_attitude': False,  # 동국인성 이수 여부
		'common_self_dev': False,  # 자기개발 이수 여부
		'common_thinkncom': False,  # 사고와소통 이수 여부
		'common_creative': False,  # 창의융합 이수 여부
		'common_digitaliter': False,  # 디지털리터러시 이수 여부
		'missing_common_dongguk_attitude': [],  # 수강하지 않은 동국인성 과목
		'missing_common_self_dev': [],  # 수강하지 않은 자기개발 과목
		'missing_common_thinkncom': [],  # 수강하지 않은 사고와소통 과목
		'missing_common_creative': [],  # 수강하지 않은 창의융합 과목
		'missing_common_digitaliter': [],
	}
	
	try:
		conn = get_db()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		params = (student_id,)
		
		# --- 1. 평점 평균(GPA) 계산 ---
		# term_summaries 테이블에서 해당 학생의 모든 학기 gpa 평균을 계산합니다.
		sql_gpa = "SELECT AVG(gpa) as avg_gpa FROM term_summaries WHERE student_id = %s"
		cursor.execute(sql_gpa, params)
		gpa_data = cursor.fetchone()
		if gpa_data and gpa_data['avg_gpa'] is not None:
			avg_gpa = float(gpa_data['avg_gpa'])
			result['gpa'] = round(avg_gpa, 2)
		
		# --- 2. 학점 및 특정 과목 이수 여부 계산 (효율적인 단일 쿼리) ---
		# enrollments와 courses 테이블을 조인하여 여러 항목을 한 번에 계산합니다.
		sql_credits_and_courses = """
		SELECT
			-- 전공/공통교양 학점
			SUM(CASE WHEN c.cpdv_nm = '전공' AND e.grade_cd <> 'F' THEN c.credit ELSE 0 END) AS major_credits,
			SUM(CASE WHEN c.cpdv_nm = '공교' AND e.grade_cd <> 'F' THEN c.credit ELSE 0 END) AS common_credits,
			
			-- F 등급을 제외한 총 취득 학점
			SUM(CASE WHEN e.grade_cd <> 'F' THEN c.credit ELSE 0 END) AS total_credit,
			
			-- 기본소양 과목 총 취득 학점
			SUM(CASE WHEN c.name IN ('기술창조와특허', '공학경제', '공학윤리') AND e.grade_cd <> 'F' THEN c.credit ELSE 0 END) AS basic_credits,
			
			-- BSM 과목 총 취득 학점
			SUM(CASE WHEN c.name IN (
				'미적분학및연습1', '미적분학및연습2', '확률및통계학', '공학선형대수학', 
				'공학수학1', '이산수학', '수치해석', '일반물리학및실험1', 
				'일반물리학및실험2', '일반화학및실험1', '일반화학및실험2', 
				'일반생물학및실험1', '일반생물학및실험2', '물리학개론', '화학개론', 
				'생물학개론', '지구환경과학', '프로그래밍기초와실습', '인터넷프로그래밍', 
				'데이터프로그래밍기초와실습', '인공지능프로그래밍기초와실습'
			) AND e.grade_cd <> 'F' THEN c.credit ELSE 0 END) AS bsm_credits,
		
			-- 종합설계1 이수 여부 (이수했으면 1, 아니면 0)
			MAX(CASE WHEN c.sbj_no = 'CSC4018' THEN 1 ELSE 0 END) AS design1_completed,
			
			-- 종합설계2 이수 여부 (이수했으면 1, 아니면 0)
			MAX(CASE WHEN c.sbj_no = 'CSC4019' THEN 1 ELSE 0 END) AS design2_completed
		
		FROM enrollments AS e
		INNER JOIN courses AS c ON e.course_key = c.course_key
		WHERE e.student_id = %s
			AND e.status = 'completed'
		"""
		cursor.execute(sql_credits_and_courses, params)
		summary_data = cursor.fetchone()
		if summary_data:
			result['major'] = float(summary_data.get('major_credits') or 0.0)
			result['common'] = float(summary_data.get('common_credits') or 0.0)
			result['total_credit'] = float(summary_data.get('total_credit') or 0.0)
			result['basic'] = float(summary_data.get('basic_credits') or 0.0)
			result['bsm'] = float(summary_data.get('bsm_credits') or 0.0)
			result['design1'] = int(summary_data.get('design1_completed') or 0)
			result['design2'] = int(summary_data.get('design2_completed') or 0)
		
		dongguk_attitude_courses = ['자아와명상1', '자아와명상2', '불교와인간']
		courses_taken = []
		sql_dongguk_attitude = """
		SELECT c.name
		FROM enrollments e
		INNER JOIN courses c ON e.course_key = c.course_key
		WHERE e.student_id = %s AND e.status = 'completed' AND c.name IN (%s, %s, %s)
		"""
		cursor.execute(sql_dongguk_attitude, (student_id, *dongguk_attitude_courses))
		taken_courses = cursor.fetchall()
		for course in taken_courses:
			courses_taken.append(course['name'])
		
		if len(courses_taken) == 3:
			result['common_dongguk_attitude'] = True
		else:
			result['common_dongguk_attitude'] = False

		# 수강하지 않은 동국인성 과목 반환
		missing_dongguk_attitude = [course for course in dongguk_attitude_courses if course not in courses_taken]
		result['missing_common_dongguk_attitude'] = missing_dongguk_attitude

		# 자기개발: 커리어 디자인, 기업가정신과 리더십
		self_dev_courses = ['커리어 디자인', '기업가정신과 리더십']
		courses_taken = []
		sql_self_dev = """
		SELECT c.name
		FROM enrollments e
		INNER JOIN courses c ON e.course_key = c.course_key
		WHERE e.student_id = %s AND e.status = 'completed' AND c.name IN (%s, %s)
		"""
		cursor.execute(sql_self_dev, (student_id, *self_dev_courses))
		taken_courses = cursor.fetchall()
		for course in taken_courses:
			courses_taken.append(course['name'])
		
		if len(courses_taken) == 2:
			result['common_self_dev'] = True
		else:
			result['common_self_dev'] = False
		
		# 수강하지 않은 자기개발 과목 반환
		missing_self_dev = [course for course in self_dev_courses if course not in courses_taken]
		result['missing_common_self_dev'] = missing_self_dev

		# 사고와소통: 기술보고서작성및발표, English 포함 강의
		thinkncom_courses = ['기술보고서작성및발표']
		english_course_taken = False
		courses_taken = []
		sql_thinkncom = """
		SELECT c.name
		FROM enrollments e
		INNER JOIN courses c ON e.course_key = c.course_key
		WHERE e.student_id = %s AND e.status = 'completed' AND c.name IN (%s)
		"""
		cursor.execute(sql_thinkncom, (student_id, *thinkncom_courses))
		taken_courses = cursor.fetchall()
		for course in taken_courses:
			courses_taken.append(course['name'])
		
		# 영어 수업을 들었는지 확인
		sql_english_courses = """
		SELECT c.name
		FROM enrollments e
		INNER JOIN courses c ON e.course_key = c.course_key
		WHERE e.student_id = %s AND e.status = 'completed' AND c.name LIKE %s
		"""
		cursor.execute(sql_english_courses, (student_id, '%English%'))
		english_courses = cursor.fetchall()
		if english_courses:
			english_course_taken = True
		
		# 두 과목을 모두 수강한 경우
		if len(courses_taken) == 1 and english_course_taken:
			result['common_thinkncom'] = True
		else:
			result['common_thinkncom'] = False
		
		# 수강하지 않은 사고와소통 과목 반환
		missing_thinkncom = [course for course in thinkncom_courses if course not in courses_taken]
		result['missing_common_thinkncom'] = missing_thinkncom

		# 창의융합: 세미나
		creative_courses = ['세미나']
		courses_taken = []
		sql_creative = """
		SELECT c.name
		FROM enrollments e
		INNER JOIN courses c ON e.course_key = c.course_key
		WHERE e.student_id = %s AND e.status = 'completed' AND c.name LIKE %s
		"""
		cursor.execute(sql_creative, (student_id, '%세미나%'))
		taken_courses = cursor.fetchall()
		for course in taken_courses:
			courses_taken.append(course['name'])
		
		# 세미나 수업을 들었는지 확인
		if len(courses_taken) >= 1:
			result['common_creative'] = True
		else:
			result['common_creative'] = False
		
		# 수강하지 않은 창의융합 과목 반환
		missing_creative = [course for course in creative_courses if course not in courses_taken]
		result['missing_common_creative'] = missing_creative

		# 디지털리터러시: 디지털 기술과 사회의 이해, 프로그래밍 이해와 실습, 빅데이터와인공지능의이해
		digitaliter_courses = ['디지털 기술과 사회의 이해', '프로그래밍 이해와 실습', '빅데이터와인공지능의이해']
		courses_taken = []
		sql_digitaliter = """
		SELECT c.name
		FROM enrollments e
		INNER JOIN courses c ON e.course_key = c.course_key
		WHERE e.student_id = %s AND e.status = 'completed' AND c.name IN (%s, %s, %s)
		"""
		cursor.execute(sql_digitaliter, (student_id, *digitaliter_courses))
		taken_courses = cursor.fetchall()
		for course in taken_courses:
			courses_taken.append(course['name'])
		
		# 세 과목 모두 수강한 경우
		if len(courses_taken) == 3:
			result['common_digitaliter'] = True
		else:
			result['common_digitaliter'] = False
		
		# 수강하지 않은 디지털리터러시 과목 반환
		missing_digitaliter = [course for course in digitaliter_courses if course not in courses_taken]
		result['missing_common_digitaliter'] = missing_digitaliter
		
		bsm_courses = ['미적분학및연습1', '확률및통계학', '공학선형대수학', '이산수학']
		courses_taken = []
		
		placeholders = ', '.join(['%s'] * len(bsm_courses))  # %s의 개수를 동적으로 맞춤
		sql_bsm_courses = f"""
		SELECT c.name 
		FROM enrollments e
		INNER JOIN courses c ON e.course_key = c.course_key
		WHERE e.student_id = %s AND e.status = 'completed' AND c.name IN ({placeholders})
		"""
		
		cursor.execute(sql_bsm_courses, (student_id, *bsm_courses))  # 동적으로 생성된 쿼리 실행
		taken_bsm_courses = cursor.fetchall()
		
		# 수강한 BSM 과목 목록
		for course in taken_bsm_courses:
			courses_taken.append(course['name'])
		
		# --- 4. 실험 과목 수강 여부 확인 (필수 항목 포함)---
		experiment_courses_taken = []

		sql_experiment_courses = """
		SELECT c.name
		FROM enrollments e
		INNER JOIN courses c ON e.course_key = c.course_key
		WHERE e.student_id = %s AND e.status = 'completed' AND c.name LIKE %s
		"""

# LIKE에서 '%' 실험%를 포함하여 패턴을 전달해야 하므로 
# '%실험%'을 직접 전달합니다.
		cursor.execute(sql_experiment_courses, (student_id, '%실험%'))
		experiment_courses = cursor.fetchall()

# 수강한 실험 과목 목록
		for course in experiment_courses:
			experiment_courses_taken.append(course['name'])

		if len(courses_taken) == 4 and len(experiment_courses_taken) >= 1:
			result['bsm_completed'] = True
		else:
			result['bsm_completed'] = False

		if len(experiment_courses_taken) >= 1:
			result['experiment_course_status'] = "실험 과목 수강 완료"
		else:
			result['experiment_course_status'] = "noexp"

# 수강하지 않은 BSM 과목 반환
		missing_bsm_courses = [course for course in bsm_courses if course not in courses_taken]
		result['missing_bsm_courses'] = missing_bsm_courses
		
		basic_courses = ['기술창조와특허', '공학경제', '공학윤리']
		courses_taken = []
		
		sql_basic_courses = """
		SELECT c.name 
		FROM enrollments e
		INNER JOIN courses c ON e.course_key = c.course_key
		WHERE e.student_id = %s AND e.status = 'completed' AND c.name IN (%s, %s, %s)
		"""
		cursor.execute(sql_basic_courses, (student_id, *basic_courses))
		taken_courses = cursor.fetchall()
		
		# 수강한 기본소양 과목 목록
		for course in taken_courses:
			courses_taken.append(course['name'])
		
		# 두 개 이상의 과목을 수강한 경우
		if len(courses_taken) >= 2:
			result['basic_completed'] = True
		else:
			result['basic_completed'] = False

		# 수강하지 않은 기본소양 과목 반환
		missing_courses = [course for course in basic_courses if course not in courses_taken]
		result['missing_basic_courses'] = missing_courses
		
		# --- 3. 영어 강의 이수 개수 계산 ---
		# 이 부분은 테이블 이름이 동적으로 변경되어 Python단에서 처리해야 합니다.
		sql_all_completed = "SELECT course_key FROM enrollments WHERE student_id = %s AND status = 'completed'"
		cursor.execute(sql_all_completed, params)
		completed_courses = cursor.fetchall()
		
		eng_course_count = 0
		for course in completed_courses:
			try:
				# course_key 파싱 (예: "CSC2004:01:2025:CM160.10")
				key_parts = course['course_key'].split(':')
				if len(key_parts) < 4: continue
				
				sbj_no, dvcls, year, sem_raw = key_parts
				term = '1' if '10' in sem_raw else '2'
				
				# 동적 테이블 이름 생성
				table_name = f"courses.courses_{year}term{term}"
				
				# 동적 테이블에서 강의 스타일 코드 조회
				sql_lang_check = f"SELECT LESN_STY_CD FROM {table_name} WHERE SBJ_NO = %s AND DVCLS = %s"
				cursor.execute(sql_lang_check, (sbj_no, dvcls))
				lang_data = cursor.fetchone()
				    
				if lang_data and lang_data['LESN_STY_CD'] == '외국어강의':
					eng_course_count += 1
		 
			except Exception:
				continue
		
		result['eng_credit'] = eng_course_count
		
		return result
	
	except Exception as e:
		print(f"get_checklist 함수 오류: {e}")
		return None
	finally:
		if cursor:
			cursor.close()
		if conn:
			conn.close()
			

def get_maincourses(student_id):
	conn = None
	cursor = None
	try:
		# 1. DB에 연결하고, 결과를 딕셔너리로 받기 위해 DictCursor를 사용합니다.
		conn = get_db()
		cursor = conn.cursor(pymysql.cursors.DictCursor)

		# 2. enrollments와 courses 테이블을 course_key 기준으로 JOIN하는 SQL 쿼리입니다.
		#    학번(student_id)이 일치하는 모든 과목의 이름(name)을 선택합니다.
		sql = """
			SELECT
				DISTINCT c.name
			FROM
				enrollments AS e
			INNER JOIN
				courses AS c ON e.course_key = c.course_key
			WHERE
				e.student_id = %s
		"""
		params = (student_id,)
		cursor.execute(sql, params)

		result_dicts = cursor.fetchall()
		result = [row['name'] for row in result_dicts]
		
		return result
		
	except Exception as e:
		print(f"get_maincourses 함수 오류: {e}")
		return None  # 오류 발생 시 None을 반환합니다.
		
	finally:
		# 5. DB 연결 리소스를 항상 정리합니다.
		if cursor:
			cursor.close()
		if conn:
			conn.close()

def set_track(student_id, track):
	try:
		conn = get_db()
		cur = conn.cursor()
		
		if track == "선택 안 함":
			track = None
		
		sql = """
		UPDATE students
		SET track = %s
		WHERE student_id = %s
		"""
		params = (track, student_id)
		cur.execute(sql, params)
		
		conn.commit()
	except Exception as e:
		print(f"set_track 함수 오류: {e}")
	finally:
		cur.close()
		conn.close()

def delete_account(student_id):
	conn = None
	cursor = None
	
	try:
		conn = get_db()
		cursor = conn.cursor()
		
		# enrollments 테이블 삭제
		cursor.execute("DELETE FROM enrollments WHERE student_id = %s", (student_id,))
		print(f"[{student_id}] enrollments에서 {cursor.rowcount}개 행 삭제 완료.")

		# term_summaries 테이블 삭제
		cursor.execute("DELETE FROM term_summaries WHERE student_id = %s", (student_id,))
		print(f"[{student_id}] term_summaries에서 {cursor.rowcount}개 행 삭제 완료.")
		
		# students 테이블 삭제
		cursor.execute("DELETE FROM students WHERE student_id = %s", (student_id,))
		
		cursor.execute("DELETE FROM userdb.users WHERE username = %s", (student_id,))
		print(f"[{student_id}] userdb.users에서 {cursor.rowcount}개 행 삭제 완료.")
		
		if cursor.rowcount == 0:
			conn.rollback() 
			return jsonify({"status": "fail", "message": f"오류: 학생 ID {student_id}가 students 테이블에 존재하지 않아 탈퇴 실패."})
		
		# 4. 모든 작업이 성공하면 최종 커밋
		conn.commit()
		return jsonify({"status": "success", "message": f"학생 ID {student_id}의 회원 탈퇴 및 모든 관련 데이터 삭제 완료 (4개 테이블 반영)."})

	except pymysql.MySQLError as e:
		# MySQL 오류 발생 시 롤백
		if conn:
			conn.rollback()
		print(f"DB 오류 발생. 롤백 실행: {e}")
		return jsonify({"status": "fail", "message": f"데이터베이스 처리 오류 발생: {e}"})
		
	except Exception as e:
		# 기타 오류 발생 시 롤백
		if conn:
			conn.rollback()
		print(f"일반 오류 발생. 롤백 실행: {e}")
		return jsonify({"status": "fail", "message": f"일반 오류 발생: {e}"})
		
	finally:
		if cursor:
			cursor.close()
		if conn:
			conn.close()


def get_ndrims(student_id, password, progress_cb=None):
	total = 5
	if progress_cb: progress_cb(1, total, "포털 로그인 중…")
	# 로그인/세션 준비…

	if progress_cb: progress_cb(2, total, "수강/성적 데이터 수집…")
	# 크롤/수집…

	if progress_cb: progress_cb(3, total, "데이터 정제…")
	# 전처리…

	if progress_cb: progress_cb(4, total, "DB 갱신…")
	# 저장…

	if progress_cb: progress_cb(5, total, "완료")
	return jsonify({"status":"success"})
