from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# 업로드 폴더 설정
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

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

@app.route('/save-draft', methods=['POST'])
def save_draft():
    """폼 데이터를 세션에 저장하고 로컬 JSON 파일로도 저장"""
    try:
        data = request.form.to_dict()
        
        # 1. 세션에 저장 (기존 로직 유지)
        session['draft_data'] = data
        
        # 2. 로컬 JSON 파일로 저장
        drafts_dir = 'drafts'
        os.makedirs(drafts_dir, exist_ok=True)
        
        # 성함(req_nm)과 타임스탬프를 이용한 파일명 생성
        req_nm = data.get('req_nm', 'unknown').strip()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"draft_{req_nm}_{timestamp}.json"
        
        file_path = os.path.join(drafts_dir, filename)
        
        # JSON 파일 저장 (한글 깨짐 방지)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        print(f"Draft saved to: {file_path}")
        
        return jsonify({"status": "success", "file": filename})
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
