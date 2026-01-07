from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# 업로드 폴더 설정
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    status = request.args.get('status', 'new')
    # 임시 데이터 (실제로는 DB에서 가져오게 됨)
    data = {
        'req_nm': '이경구',
        'birth': '1990-01-01',
        'req_kind': 'P'
    } if status in ['saved', 'finished'] else None
    
    applied_at = ""
    if status == 'finished':
        from datetime import datetime, timedelta
        # 한국 시간 계산 (UTC+9)
        now = datetime.utcnow() + timedelta(hours=9)
        applied_at = now.strftime('%Y-%m-%d %H:%M:%S')
        
    return render_template('application_form.html', status=status, data=data, applied_at=applied_at)

@app.route('/save-draft', methods=['POST'])
def save_draft():
    """폼 데이터를 세션에 임시 저장"""
    session['draft_data'] = request.form.to_dict()
    # 최종 제출 시에는 세션 데이터를 삭제할 수 있습니다.
    return jsonify({"status": "success"})

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
