from flask import Flask, render_template, request, jsonify, session
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

@app.route('/')
def index():
    """메인 페이지 - 신청서 작성 폼"""
    status = request.args.get('status', default='new', type=str)
    # 세션에서 저장된 데이터 가져오기
    saved_data = session.get('draft_data', None)
    return render_template('application_form.html', status=status, data=saved_data)

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

if __name__ == '__main__':
    app.run(debug=True, port=5000)

