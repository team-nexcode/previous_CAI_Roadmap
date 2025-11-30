import json, os, pymysql
from datetime import datetime

# -------- DB 연결 --------
conn = pymysql.connect(
    host="127.0.0.1",
    port=3306,
    user="",
    password="",
    db="",
    charset="utf8mb4"
)
cur = conn.cursor()


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

# [수정] 인자 변경: birth_date 대신 birth를 받도록 수정
def upsert_student(student_id, bas, college, faculty, major, birth):
    sql = """
    INSERT INTO students
      (student_id, name, email, phone, sex, campus, entry_date, entry_yy_sem, foreign_yn,
       club_name, address_full, bank_name, bank_account_enc, level_test_teps, deep_yn,
       ENT_TOPIK_GRD_CD_NM, GRAD_TOPIK_GRD_CD_NM, GRAD_TOPIK_GAIN_DT, ENT_TOPIK_GAIN_DT,
       colleges, faculties, majors, birth) -- [수정] 컬럼명 변경
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
      majors=VALUES(majors), birth=VALUES(birth); -- [수정] 업데이트 구문
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

def ensure_term(year, sem_cd, yy_sem_name):
    if not (year and sem_cd): return
    sql = "INSERT INTO terms (year, sem_cd, yy_sem_name) VALUES (%s,%s,%s) ON DUPLICATE KEY UPDATE yy_sem_name=VALUES(yy_sem_name);"
    cur.execute(sql, (int(year), sem_cd, yy_sem_name))

def upsert_course(row):
    course_key = f"{row.get('SBJ_NO')}:{row.get('DVCLS')}:{row.get('OPEN_YY')}:{row.get('OPEN_SEM_CD')}"
    sql = """
    INSERT INTO courses
      (course_key, sbj_no, dvcls, name, cpdv_nm, dept_all_nm, dpt_nm, colg_nm, cors_nm,
       detl_curi_nm, main_prof_nm, credit, open_year, sem_cd, open_yy_sem, timetable,
       recrs_recod_yn, sys_ins_dttm)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s, %s,%s,%s,%s,%s,%s,%s,%s,%s)
    ON DUPLICATE KEY UPDATE
      name=VALUES(name), cpdv_nm=VALUES(cpdv_nm), dept_all_nm=VALUES(dept_all_nm),
      dpt_nm=VALUES(dpt_nm), colg_nm=VALUES(colg_nm), cors_nm=VALUES(cors_nm),
      detl_curi_nm=VALUES(detl_curi_nm), main_prof_nm=VALUES(main_prof_nm),
      credit=VALUES(credit), open_year=VALUES(open_year), sem_cd=VALUES(sem_cd),
      open_yy_sem=VALUES(open_yy_sem), timetable=VALUES(timetable),
      recrs_recod_yn=VALUES(recrs_recod_yn), sys_ins_dttm=VALUES(sys_ins_dttm);
    """
    cur.execute(sql, (
        course_key, row.get("SBJ_NO"), row.get("DVCLS"), row.get("SBJ_NM"),
        row.get("CPDIV_NM"), row.get("DEPT_ALL_NM"), row.get("DPT_NM"),
        row.get("COLG_NM"), row.get("CORS_NM"), row.get("DETL_CURI_NM"),
        row.get("MAIN_PROF_NM"), float(row["CDT"]) if row.get("CDT") else None,
        int(row["OPEN_YY"]) if row.get("OPEN_YY") else None, row.get("OPEN_SEM_CD"),
        row.get("OPEN_YY_SEM"), row.get("TMTBL_KOR_DSC"), row.get("RECRS_RECOD_YN"),
        row.get("SYS_INS_DTTM"),
    ))
    return course_key

def upsert_enrollment(student_id, course_key, year, sem_cd, open_yy_sem, status, grade_cd, credit):
    sql = """
    INSERT INTO enrollments
      (student_id, course_key, year, sem_cd, open_yy_sem, status, grade_cd, credit)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    ON DUPLICATE KEY UPDATE
      grade_cd=VALUES(grade_cd), credit=VALUES(credit), open_yy_sem=VALUES(open_yy_sem);
    """
    cur.execute(sql, (
        int(student_id), course_key, int(year), sem_cd, open_yy_sem, status, grade_cd,
        float(credit) if credit is not None else None
    ))

def upsert_term_summary(student_id, year, sem_cd, yy_sem_name=None, applied=None, gained=None, gpa=None, rank_text=None, dept_rank=None, per_sco=None):
    if not yy_sem_name:
        yy_sem_name = f"{year}-{sem_cd}"
    sql = """
    INSERT INTO term_summaries
      (student_id, year, sem_cd, yy_sem_name, applied_cdt, gained_cdt, gpa, rank_text, dept_rank, per_sco)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ON DUPLICATE KEY UPDATE
      applied_cdt = VALUES(applied_cdt), gained_cdt  = VALUES(gained_cdt),
      gpa = VALUES(gpa), rank_text = VALUES(rank_text), dept_rank = VALUES(dept_rank),
      per_sco = VALUES(per_sco);
    """
    cur.execute(sql, (
        int(student_id), int(year), sem_cd, yy_sem_name,
        float(applied) if applied is not None else None,
        float(gained) if gained is not None else None,
        float(gpa) if gpa is not None else None,
        rank_text, dept_rank, float(per_sco) if per_sco is not None else None
    ))

# -------- JSON 로드 --------
with open("response_1.json", "r", encoding="utf-8") as f:
    res1 = json.load(f)
with open("response_2.json", "r", encoding="utf-8") as f:
    res2 = json.load(f)
with open("response_3.json", "r", encoding="utf-8") as f:
    res3 = json.load(f)
with open("extracted_personal+info.json", "r", encoding="utf-8") as f:
    personal_info_list = json.load(f)

# 1) 학번(student_id) 추출
rec_list = res3.get("dsMainRec", [])
if not rec_list: raise RuntimeError("dsMainRec가 비어 있어 학번 추출 불가")
student_id = rec_list[0].get("STD_NO")
if not student_id: raise RuntimeError("STD_NO 없음")

# 2) 학생 기본사항 upsert
bas = (res1.get("dsMainBas") or [{}])[0]
personal_data = (personal_info_list or [{}])[0]
name = bas.get("DPSTR_NM")

department_full_name = personal_data.get("DPTMJR_NM")
parsed_dept = parse_department(department_full_name)

rsdn_dt_sex_full = personal_data.get("RSDN_DT_SEX")
birth_date_value = None
if rsdn_dt_sex_full:
    birth_date_value = rsdn_dt_sex_full.split('(')[0] 

# [수정] upsert_student 호출 방식 변경
upsert_student(
    student_id,
    bas,
    college=parsed_dept['college'],
    faculty=parsed_dept['faculty'],
    major=parsed_dept['major'],
    birth=birth_date_value # [수정] 키워드 변경
)

# 3) term 마스터
for t in res2.get("dsMainTkcrsYy", []):
    yy, sem_cd = t.get("YY"), t.get("SEM_CD")
    if yy and sem_cd and yy.isdigit():
        ensure_term(int(yy), sem_cd, t.get("YY_SEM"))

# 4) 수강신청/수강중
for c in res2.get("dsMainTkcrs", []):
    course_key = upsert_course(c)
    yy, sem_cd = c.get("OPEN_YY"), c.get("OPEN_SEM_CD")
    if yy and sem_cd:
        ensure_term(int(yy), sem_cd, c.get("OPEN_YY_SEM"))
    upsert_enrollment(
        student_id=student_id, course_key=course_key, year=int(yy) if yy else None,
        sem_cd=sem_cd, open_yy_sem=c.get("OPEN_YY_SEM"), status="registered",
        grade_cd=None, credit=c.get("CDT")
    )

# 5) 성적(이수 완료)
for r in res3.get("dsMainRec", []):
    open_yy_sem = r.get("OPEN_YY_SEM")
    year = int(open_yy_sem.split("-")[0]) if open_yy_sem and "-" in open_yy_sem else int(r.get("YY"))
    sem_cd, dvcls, sbj_no = r.get("SEM_CD"), r.get("DVCLS"), r.get("SBJ_NO")
    course_row_min = {
        "SBJ_NO": sbj_no, "DVCLS": dvcls, "SBJ_NM": r.get("SBJ_NM"),
        "CPDIV_NM": r.get("CPDIV_CD"), "DEPT_ALL_NM": r.get("ADMT_RECOD_CLSF_NM"),
        "DPT_NM": None, "COLG_NM": None, "CORS_NM": None,
        "DETL_CURI_NM": r.get("DETL_CUTI_CD"), "MAIN_PROF_NM": r.get("EMP_NM"),
        "CDT": r.get("CDT"), "OPEN_YY": year, "OPEN_SEM_CD": sem_cd,
        "OPEN_YY_SEM": open_yy_sem, "TMTBL_KOR_DSC": None,
        "RECRS_RECOD_YN": r.get("RECRS_YY_SEM"), "SYS_INS_DTTM": None
    }
    course_key = upsert_course(course_row_min)
    ensure_term(year, sem_cd, open_yy_sem or (str(year)))
    upsert_enrollment(
        student_id=student_id, course_key=course_key, year=year, sem_cd=sem_cd,
        open_yy_sem=open_yy_sem or "", status="completed",
        grade_cd=r.get("RECOD_GRD_CD"), credit=r.get("CDT")
    )

# 6) 학기별 요약
for s in res3.get("dsMainRecYySem", []):
    if s.get("YY") == "%" or s.get("SEM_CD") == "%": continue
    upsert_term_summary(
        student_id=student_id, year=int(s["YY"]), sem_cd=s["SEM_CD"],
        yy_sem_name=s.get("YY_SEM_NM"), applied=s.get("APPL_CDT"),
        gained=s.get("GAIN_CDT"), gpa=s.get("AVG_MRK")
    )

for ss in res3.get("dsSubRec", []):
    if ss.get("SEM_CD"):
        upsert_term_summary(
            student_id=student_id, year=int(ss["YY"]), sem_cd=ss["SEM_CD"],
            applied=ss.get("APPL_CDT"), gained=ss.get("GAIN_CDT"),
            gpa=ss.get("AVG_MRK"), rank_text=ss.get("RANK"),
            dept_rank=ss.get("DPT_RANK"), per_sco=ss.get("PER_SCO")
        )

conn.commit()
cur.close()
conn.close()
print(f"{student_id}, {name} DB Manual Save Done!")