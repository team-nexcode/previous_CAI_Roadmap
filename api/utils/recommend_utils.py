from utils.db_utils import get_db, get_completed, get_enrolled
import pymysql

def get_term(cursor, student_id):
	try:
		sql = """
			SELECT COUNT(DISTINCT CONCAT(year, sem_cd)) AS semester_count
			FROM term_summaries
			WHERE student_id = %s
		"""
		cursor.execute(sql, (student_id,))
		result = cursor.fetchone()
		return result['semester_count'] if result else 0
	except Exception as e:
		print(f"Error getting term count: {e}")
		return 0

WEIGHTS = {
	'to': 0.5,
	'urgency': 5.0,
	'unlock': 10.0,
	'type': 1.0,
	'track': 3.0
}

# --- 점수 계산 로직 함수로 분리 ---
def calculate_score(course, term, user_track, weights, apply_track_weight):
	
	S_to = float(course.get('to_count') or 0.0)
	S_unl = float(course.get('score_unlock') or 0.0)
	S_typ = float(course.get('score_type') or 0.0)

	S_urg = 0.0
	rec_grade = course.get('recommended_grade') 

	if rec_grade:
		user_next_grade = 1 + term // 2
		diff = user_next_grade - rec_grade
		S_urg = float(diff * 50)

	S_trk = 0.0
	course_tracks = course.get('course_tracks', [])
	if apply_track_weight and user_track and user_track in course_tracks:
		S_trk = 100.0
	if not apply_track_weight and user_track:
		S_trk = 100.0
	
	# (W) 가중치
	W_to = weights['to']
	W_urg = weights['urgency']
	W_unl = weights['unlock']
	W_tp = weights['type']
	W_trk = weights['track']
	
	total_score = (S_to * W_to) + (S_urg * W_urg) + (S_unl * W_unl) + (S_typ * W_tp) + (S_trk * W_trk)
	
	return {
		"name": course['name'],
		"sbj_no": course['sbj_no'],
		"recommend_grade": rec_grade,
		"track": course_tracks, 
		"credit": course['credit'],
		"description": course['description'],
		"score": total_score
	}


def get_recommendations(student_id, next_term):
	conn = None
	cursor = None
	recommendation_scores = []
	
	try:
		conn = get_db()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		
		# --- A. 유저 정보 로드 ---
		term = get_term(cursor, student_id)
		
		completed_courses = get_completed(student_id)
		completed_sbj_code_list = [c['sbj_no'] for c in completed_courses] if completed_courses else []
		
		enrolled_courses = get_enrolled(student_id)
		enrolled_sbj_code_list = [c['sbj_no'] for c in enrolled_courses] if enrolled_courses else []
		
		excluded_sbj_code_list = set(completed_sbj_code_list + enrolled_sbj_code_list)
		
		cursor.execute("SELECT track FROM students WHERE student_id = %s", (student_id,))
		user_data = cursor.fetchone()
		user_track = user_data.get('track') if user_data and user_data.get('track') else None
		
		sql_major = f"""
			SELECT
				T1.code AS sbj_no, T1.title AS name, T1.credit, T1.prereq AS prerequisites, 
				T3.track_name AS course_track,
				1 AS min_grade, 
				
				100 AS score_type,
				
				CASE
					WHEN T1.code LIKE 'PRI%' THEN 2
					WHEN T1.code LIKE 'CSC%' THEN CAST(SUBSTRING(T1.code, 4, 1) AS UNSIGNED)
					ELSE 2
				END AS recommended_grade,
				
				T1.enrollment AS score_unlock,
				50 AS to_count, -- T2.capacity
				
				CASE 
					WHEN EXISTS (
						SELECT 1
						FROM courses.courses_2025term{next_term} AS T4
						WHERE T4.SBJ_NO COLLATE utf8mb4_general_ci = T1.code
					) THEN 1
					ELSE 0
				END AS is_opened,
				교과목해설 AS description

			FROM courses.courses AS T1
			LEFT JOIN curriculum.courses AS T2 ON T1.code = T2.course_code
			LEFT JOIN curriculum.track_courses AS T3 ON T1.code = T3.course_code
			WHERE T1.code IS NOT NULL
			AND (T2.capacity IS NULL OR T2.capacity > -1);
		"""
		cursor.execute(sql_major)
		candidate_courses = cursor.fetchall()

		# --- C. 1-차 필터링: 자격 검사 및 그룹화 ---
		final_candidates = {}
		user_next_grade = 1 + term // 2 # (필터링을 위해 학년 미리 계산)
		
		for course in candidate_courses:
			sbj_no = course['sbj_no']
			
			if course['is_opened'] == 0:
				continue
			
			if sbj_no in excluded_sbj_code_list:
				continue
			
			to_count = course.get('to_count')
			if to_count is not None and to_count <= 0:
				continue

			# (min_grade 필터링)
			min_grade = course.get('min_grade')
			if min_grade and user_next_grade < min_grade:
				continue 
			
			prereqs_str = course.get('prerequisites')
			is_prereq_met = True
			if prereqs_str:
				prereqs_list = [p.strip() for p in prereqs_str.split(',') if p.strip()]
				if not all(p in excluded_sbj_code_list for p in prereqs_list):
					is_prereq_met = False
			
			if not is_prereq_met:
				continue

			if sbj_no not in final_candidates:
				final_candidates[sbj_no] = course
				final_candidates[sbj_no]['course_tracks'] = []
			
			if course.get('course_track'):
				track_name = course['course_track']
				if track_name not in final_candidates[sbj_no]['course_tracks']:
					final_candidates[sbj_no]['course_tracks'].append(track_name)
					
		
		# --- D. 2-차 계산: 트랙 과목 / 트랙 외 과목 분리 처리 ---
		
		# 1) 1단계: 트랙 전공 과목
		track_courses = [c for c in final_candidates.values() if c.get('course_tracks')]
		for course in track_courses:
			score_data = calculate_score(course, term, user_track, WEIGHTS, True) 
			recommendation_scores.append(score_data)

		# 2) 2단계: 트랙 외/필수 과목 (전공 + 교양)
		non_track_courses = [c for c in final_candidates.values() if not c.get('course_tracks')]
		for course in non_track_courses:
			score_data = calculate_score(course, term, user_track, WEIGHTS, False)
			recommendation_scores.append(score_data)
			
		
		# --- E. 정렬 및 반환 (전체 통합 정렬) ---
		sorted_recommendations = sorted(
			recommendation_scores,
			key=lambda x: x['score'],
			reverse=True
		)
		
		return sorted_recommendations

	except Exception as e:
		print(f"추천 알고리즘 오류: {e}")
		if conn: conn.rollback()
		return None
	
	finally:
		if conn:
			try:
				conn.commit()
			except Exception as e:
				conn.rollback()
				print(f"커밋 중 오류 발생: {e}")
		if cursor: cursor.close()
		if conn: conn.close()

def get_cat(student_id, next_term):
	"""
	아직 이수하지 않은 과목 목록을 반환합니다.
	(단, 중영역 총학점을 만족한 과목 및 동일과목 그룹은 제외)
	"""
	conn = None
	cursor = None
	
	try:
		conn = get_db()
		cursor = conn.cursor(pymysql.cursors.DictCursor)

		# 1. 제외 대상(기이수 + 수강 중) 과목 코드 목록 가져오기 및 SQL IN 절 준비
		completed_courses = get_completed(student_id)
		
		
		# 수강 중인 과목 코드 목록
		enrolled_courses = get_enrolled(student_id)
		enrolled_sbj_code_list = [c['sbj_no'] for c in enrolled_courses] if enrolled_courses else []
		
		excluded_sbj_code_list = set([c['sbj_no'] for c in completed_courses] + enrolled_sbj_code_list)
		
		# SQL IN 절에 사용될 포맷 ('SBJ001', 'SBJ002')
		excluded_sbj_no_str = ', '.join([f"'{c}'" for c in excluded_sbj_code_list])
		if not excluded_sbj_no_str:
			excluded_sbj_no_str = "''"
		
		# 2. 기이수 과목의 동일과목(same) 번호 목록을 DB에서 조회
		sql_get_same_groups = f"""
			SELECT DISTINCT 동일과목 AS same
			FROM courses.course_cat
			WHERE 학수번호 IN ({excluded_sbj_no_str}) AND 동일과목 IS NOT NULL;
		"""
		cursor.execute(sql_get_same_groups)
		same_groups_result = cursor.fetchall()
		
		# Set으로 변환하여 파이썬 필터링에 사용
		excluded_same_groups = {row['same'] for row in same_groups_result}
		
		# 3. 모든 과목 목록 가져오기 및 중영역 충족 여부 필터링 (SQL)
		sql_all_cat = f"""
			WITH UserCompletedCredits AS (
				-- 기이수 과목 중 '중영역'이 있는 과목의 누적 학점 집계
				SELECT
					T1.중영역 AS mid_area,
					SUM(T1.학점) AS accumulated_credit
				FROM
					courses.course_cat AS T1
				WHERE
					T1.중영역 IS NOT NULL AND T1.학수번호 IN ({excluded_sbj_no_str})
				GROUP BY
					T1.중영역
			)
			SELECT
				T2.학수번호 AS sbj_no,
				T2.교과목명 AS name,
				T2.학점 AS credit,
				T2.총학점 AS total,
				T2.동일과목 AS same,
				T2.중영역 AS mid,
				T2.교과과정 AS category,
				CASE
					WHEN T2.학수번호 IN ('RGC1093', 'RGC1095', 'PRI4041') THEN 2
					ELSE 1
				END AS min_grade,
				
				CASE
					WHEN EXISTS (
						SELECT 1
						FROM courses.courses_2025term{next_term} AS T3
						WHERE T3.SBJ_NO COLLATE utf8mb4_general_ci = T2.학수번호
					) THEN 1
					ELSE 0
				END AS is_opened,
				T2.교과목해설 AS description
			FROM
				courses.course_cat AS T2
			LEFT JOIN
				UserCompletedCredits AS UCC ON T2.중영역 = UCC.mid_area
			WHERE
				-- 중영역 정보가 없는 과목은 무조건 포함
				T2.중영역 IS NULL
				OR (
					-- 중영역이 있는 경우, 누적 학점이 총학점보다 작은 경우에만 포함
					UCC.accumulated_credit IS NULL
					OR UCC.accumulated_credit < T2.총학점
				);
		"""
		cursor.execute(sql_all_cat)
		all_cat_courses = cursor.fetchall()
		
		# 4. 최종 필터링: 개별 과목 이수 여부, 수강 중 여부, 동일과목 그룹 필터링 (Python)
		untaken_cat_courses = []

		for course in all_cat_courses:
			# 1) 개설 여부 필터링
			if course['is_opened'] == 0:
				continue
			
			# 2) 기이수/수강 중 과목 코드 필터링
			if course['sbj_no'] in excluded_sbj_code_list:
				continue

			# 3) 동일과목 그룹 필터링: 이수한 과목과 동일한 그룹(same)에 속한 경우 제외
			if course['same'] is not None and course['same'] in excluded_same_groups:
				continue
			
			# 4) 상호 배타(Blocking) 과목 필터링
			current_sbj_no = course['sbj_no']
			
			if current_sbj_no == 'PRI4029':
				if 'PRI4002' in excluded_sbj_code_list or 'PRI4013' in excluded_sbj_code_list:
					continue

			if current_sbj_no == 'PRI4030':
				if 'PRI4003' in excluded_sbj_code_list or 'PRI4014' in excluded_sbj_code_list:
					continue

			if current_sbj_no == 'PRI4028':
				if 'PRI4004' in excluded_sbj_code_list or 'PRI4015' in excluded_sbj_code_list:
					continue
			
			untaken_cat_courses.append(course)
				
		return untaken_cat_courses

	except Exception as e:
		print(f"Error in get_cat: {e}")
		if conn: conn.rollback()
		return None
	
	finally:
		if conn:
			try:
				conn.commit()
			except Exception as e:
				conn.rollback()
				print(f"커밋 중 오류 발생 (get_cat): {e}")
		if cursor: cursor.close()
		if conn: conn.close()