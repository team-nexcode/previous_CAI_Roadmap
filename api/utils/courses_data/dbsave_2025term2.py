import json
import pymysql

# 저장할 컬럼 목록
TARGET_COLUMNS = [
    "CDT", "CPDIV_CD_NM", "DETL_CURI_CD_NM", "TMTBL_ENG_DSC", "OBJ_SCHGRD",
    "DETL_CURI_CD", "COLG_NM", "CPDIV_CD", "DPT_NM", "EMP_NM", "LESN_STY_CD",
    "TMTBL_KOR_DSC", "OPEN_YY", "SBJ_NO", "SBJ_NM", "RECOD_GRD_TYP_CD_NM",
    "DVCLS", "ROOM_KOR_DSC", "RECOD_EVAL_METH_CD_NM", "PROF_KOR_DSC"
]

def get_db():
    return pymysql.connect(
        host="127.0.0.1", port=3306, user="",
        password="", db="", charset="utf8mb4"
    )

def insert_courses_from_json(json_file_path):
    conn = None
    cursor = None
    # 디버깅을 위해 함수 스코프에서 변수 선언
    current_course_for_debug = None
    
    try:
        # 1. JSON 파일 읽기
        with open(json_file_path, 'r', encoding='utf-8') as f:
            full_data = json.load(f)
            courses_data = full_data['dsMain'] # 여기서 courses_data 정의
        
        # 2. 데이터베이스 연결
        conn = get_db()
        cursor = conn.cursor()
        table_name = 'courses_2025term2'
        
        # 3. 루프 실행
        for course in courses_data:
            current_course_for_debug = course
            
            data_to_insert = {col: course.get(col) for col in TARGET_COLUMNS}

            columns = data_to_insert.keys()
            values = data_to_insert.values()
            
            query_columns = ', '.join([f'`{col}`' for col in columns])
            query_placeholders = ', '.join(['%s'] * len(values))
            
            update_clause = ', '.join([f'`{col}` = VALUES(`{col}`)' for col in columns])
            
            sql = (
                f"INSERT INTO `{table_name}` ({query_columns}) "
                f"VALUES ({query_placeholders}) "
                f"ON DUPLICATE KEY UPDATE {update_clause}"
            )
            
            cursor.execute(sql, tuple(values))

        # 4. 모든 작업이 성공했을 때만 최종 저장
        conn.commit()
        print(f"총 {len(courses_data)}개의 과목 데이터가 성공적으로 추가 또는 수정되었습니다.")

    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        # 파일 관련 오류 처리
        print(f"파일을 읽는 중 오류가 발생했습니다: {e}")

    except Exception as e:
        # 데이터베이스 작업 관련 오류 처리
        if conn: conn.rollback()
        
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!!!!!!!!!!!!! 데이터베이스 작업 중 오류 발생 !!!!!!!!!!!!!!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"오류 종류: {e}")
        print("--- 문제가 발생한 데이터 ---")
        if current_course_for_debug:
            print(f"  과목 번호 (SBJ_NO): {current_course_for_debug.get('SBJ_NO')}")
            print(f"  과목 이름 (SBJ_NM): {current_course_for_debug.get('SBJ_NM')}")
        print("--------------------------")

    finally:
        # 5. 연결 종료
        if cursor: cursor.close()
        if conn: conn.close()

if __name__ == "__main__":
    insert_courses_from_json('data.json')