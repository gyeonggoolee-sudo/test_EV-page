from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# 업로드 폴더 설정 (공유 폴더 경로)
UPLOAD_FOLDER = r'\\DESKTOP-KEHQ34D\Users\com\Desktop\GreetLounge\25q4_test\uploaded_file'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/notice-management')
def notice_management():
    conn = get_db_connection()
    regions = []
    if conn:
        try:
            cur = conn.cursor()
            # region_metadata와 ev_info를 조인하여 file_paths 정보를 함께 가져옴
            query = """
                SELECT rm.region_id, rm.region, ei.file_paths 
                FROM region_metadata rm
                LEFT JOIN ev_info ei ON rm.region_id = ei.region_id
                ORDER BY rm.region
            """
            cur.execute(query)
            regions = cur.fetchall()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Error fetching regions: {e}")
    
    # regions 구조: [(id, name, file_paths_json), ...]
    return render_template('notice_management.html', regions=regions)

@app.route('/api/notice/<int:region_id>')
def get_notice_detail(region_id):
    """특정 지자체의 상세 공고 정보를 가져오는 API"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "DB connection failed"}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT file_paths, bigo FROM ev_info WHERE region_id = %s", (region_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        
        if row:
            return jsonify({
                "file_paths": row[0],
                "bigo": row[1]
            })
        return jsonify({"file_paths": {}, "bigo": ""})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/applyform')
def apply_form():
    status = request.args.get('status', 'new')
    local_nm = request.args.get('local_nm', '성남시')
    
    if status == 'new':
        # 새 신청인 경우 기존 세션 데이터 및 업로드 파일 정보 삭제
        session.pop('draft_data', None)
        session.pop('uploaded_files', None)
        data = None
    else:
        # 세션에서 임시저장된 데이터 가져오기
        data = session.get('draft_data')
    
    # 데이터가 아예 없을 때(None)만 기본 예시 데이터 설정 (최초 테스트용/status가 saved/finished일 때)
    if data is None and status in ['saved', 'finished']:
        data = {
            'req_nm': '이경구',
            'birth': '1990-01-01',
            'req_kind': 'P'
        }
    
    applied_at = ""
    if status == 'finished':
        from datetime import datetime, timedelta
        # 한국 시간 계산 (UTC+9)
        now = datetime.utcnow() + timedelta(hours=9)
        applied_at = now.strftime('%Y-%m-%d %H:%M:%S')
        
    return render_template('application_form.html', status=status, data=data, applied_at=applied_at, local_nm=local_nm)

# 기본 DB 설정
DB_CONFIG = {
    "host": "192.168.0.92",
    "database": "postgres",
    "user": "postgres",
    "password": "greet1202!@",
    "port": "5432",
    "connect_timeout": 3
}

def get_db_connection():
    import psycopg2
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

@app.route('/save-draft', methods=['POST'])
def save_draft():
    """폼 데이터를 세션에 저장하고 로컬 JSON 파일 및 PostgreSQL DB로 저장"""
    try:
        data = request.form.to_dict()
        
        # 공동명의자 정보는 중복 키가 존재하므로 리스트로 별도 처리
        if 'jn_name' in request.form:
            data['jn_name'] = request.form.getlist('jn_name')
        if 'jn_birth' in request.form:
            data['jn_birth'] = request.form.getlist('jn_birth')

        # 1. 세션에 저장 (기존 로직 유지)
        session['draft_data'] = data
        
        # 2. 로컬 JSON 파일 및 DB로 저장 (save_json 플래그가 'Y'인 경우에만)
        if request.form.get('save_json') == 'Y':
            # 최종 구조화할 딕셔너리 생성
            structured_data = {}
            
            # 섹션별 필드 정의
            sections = {
                'management_info': ['local_nm', 'app_step', 'contract_day'],
                'application_info': [
                    'req_kind', 'profit_yn', 'grp_reqst_se', 'req_nm', 'birth', 'ceo', 'req_sex', 
                    'pri_business_yn', 'birth2', 'busi_no', 'pri_busi_nm', 'model_cd', 'req_cnt', 
                    'delivery_sch_day', 'zipno', 'addr', 'addr_detail', 'req_total_amt', 'phone', 
                    'mobile', 'email'
                ],
                'joint_owner_info': ['jn_cnt', 'jn_name', 'jn_birth'],
                'condition_info': [
                    'improve_fd_yn', 'first_buy_yn', 'social_yn', 'social_kind', 'children_cnt', 
                    'exchange_yn', 'school_bus_yn', 'in_facility_yn', 'disaster_scrap_yn', 'bms_yn'
                ],
                'priority_info': ['priority_type'],
                'lease_rental_info': [
                    'ls_user_yn', 'ls_user_kind', 'ls_user_type', 'ls_user_nm_chk', 'cntrctr_yn', 
                    'ls_user_nm', 'ls_user_busi_no', 'ls_user_birth2', 'ls_user_zipno', 
                    'ls_user_addr', 'ls_user_addr_detail'
                ],
                'seller_info': ['seller_phone', 'contact_nm', 'contact_mobile', 'seller_mgrid'],
                'memo_info': ['req_memo', 'seller_memo']
            }

            # 섹션별로 데이터 분류
            for section_name, fields in sections.items():
                section_dict = {}
                for field in fields:
                    if field in data:
                        section_dict[field] = data[field]
                if section_dict: # 데이터가 있는 섹션만 추가
                    structured_data[section_name] = section_dict

            # 소요 시간 처리
            process_seconds_val = 0
            process_seconds_str = request.form.get('process_seconds')
            if process_seconds_str is not None:
                try:
                    process_seconds_val = int(process_seconds_str)
                except ValueError:
                    pass

            # 3. PostgreSQL DB 저장
            writer = structured_data.get('seller_info', {}).get('contact_nm', 'unknown')
            
            conn = get_db_connection()
            if conn:
                try:
                    cur = conn.cursor()
                    insert_query = """
                        INSERT INTO application_drafts (writer, process_seconds, data)
                        VALUES (%s, %s, %s)
                    """
                    cur.execute(insert_query, (writer, process_seconds_val, json.dumps(structured_data, ensure_ascii=False)))
                    conn.commit()
                    cur.close()
                    conn.close()
                    print("Data inserted into PostgreSQL successfully.")
                except Exception as e:
                    print(f"Error inserting into PostgreSQL: {e}")
            
            # JSON 저장 시에는 process_seconds를 포함 (요청 사항에 따라 최하단에 위치)
            structured_data['process_seconds'] = process_seconds_val

            drafts_dir = 'drafts'
            os.makedirs(drafts_dir, exist_ok=True)
            
            # 성함(req_nm)은 application_info 안에 있으므로 경로 맞춰서 가져오기
            req_nm = structured_data.get('application_info', {}).get('req_nm', 'unknown').strip()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"draft_{req_nm}_{timestamp}.json"
            
            file_path = os.path.join(drafts_dir, filename)
            
            # JSON 파일 저장
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(structured_data, f, ensure_ascii=False, indent=4)
                
            print(f"Structured draft saved to: {file_path}")
            return jsonify({"status": "success", "file": filename})
        
        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Error saving draft: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/submit', methods=['POST'])
def submit_form():
    """폼 제출 처리"""
    data = request.form.to_dict()
    # 여기에 실제 처리 로직 추가
    print("Received form data:", data)
    return jsonify({"status": "success", "message": "신청서가 제출되었습니다."})

@app.route('/api/local-info', methods=['GET'])
def get_local_info():
    """지자체 정보 API"""
    # 실제 API 연동 로직 추가
    return jsonify({"local_cd": "4113", "local_nm": "성남시"})

@app.route('/juso/popup')
def juso_popup():
    """주소 입력 팝업창"""
    return render_template('juso_popup.html')

@app.route('/popup/security')
def security_popup():
    """보안코드 입력 팝업창"""
    return render_template('security_popup.html')

@app.route('/popup/attach')
def attach_popup():
    """첨부파일 업로드 팝업창"""
    file_type = request.args.get('type')
    return render_template('attach_popup.html', file_type=file_type)

@app.route('/popup/municipality')
def municipality_popup():
    """지자체 선택 팝업창"""
    return render_template('municipality_popup.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """파일 업로드 처리"""
    if 'file' not in request.files:
        return '<script>alert("파일이 없습니다.");history.back();</script>'
    file = request.files['file']
    file_type = request.form.get('file_type')
    
    if file.filename == '':
        return '<script>alert("선택된 파일이 없습니다.");history.back();</script>'
        
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # 업로드 성공 후 부모창 함수 호출 및 팝업 닫기
        return f"""
        <!DOCTYPE html>
        <html>
        <body>
            <script>
                alert('파일이 성공적으로 업로드되었습니다.');
                if(window.opener && !window.opener.closed) {{
                    window.opener.handlePopupResult('{file_type}', '{filename}');
                }}
                window.close();
            </script>
        </body>
        </html>
        """
    return 'Upload failed'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
