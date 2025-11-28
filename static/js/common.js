/**
 * 새로운 공동명의자 정보 추가
 */
function createNewJointInfo() {
    var count = $('#jn_cnt').val();
    var tbody = $('#jnBody');
    tbody.empty(); // 기존 내용 삭제

    if (count > 0) {
        $('#t_jnInfo').show();
        $('#l_jnCount').hide();
    } else {
        $('#t_jnInfo').hide();
        $('#l_jnCount').show();
        return;
    }

    for (var i = 1; i <= count; i++) {
        var newRow = '<tr class="c_jnInfo">' +
            '<td class="c_jn_num">' + i + '</td>' +
            '<td><input type="text" class="text c_jn_name" name="jn_name" value="" style="width:150px;" maxlength="40" title="성명"></td>' +
            '<td><input type="text" class="c_jn_birth datepicker" style="width: 130px" name="jn_birth" value="" title="생년월일" readonly="readonly"></td>' +
            '<td><button type="button" class="btn-round btn-base" name="btnJnDel" onclick="deleteJNRow(this);return false;">삭제</button></td>' +
            '</tr>';
        tbody.append(newRow);
    }

    // 동적으로 생성된 datepicker에만 datepicker 적용
    tbody.find('.datepicker').datepicker({
        dateFormat: 'yy-mm-dd',
        changeMonth: true,
        changeYear: true,
        yearRange: 'c-100:c+10'
    });
}

/**
 * 공동명의자 정보 삭제
 */
function deleteJointInfo(button) {
    if (confirm('공동명의자 정보를 삭제하시겠습니까?')) {
        $(button).closest('tr').remove();
        if ($('#jnBody tr').length === 0) {
            $('#t_jnInfo').hide();
        }
        // 순번 재정렬 로직 필요
    }
}

function deleteJNRow(button) {
    // 가장 가까운 <tr> 요소를 찾아서 삭제합니다.
    $(button).closest('tr').remove();
    
    // 남은 행의 개수를 셉니다.
    var rowCount = $('#jnBody tr').length;
    
    // '공동명의자 수' 입력 필드의 값을 업데이트합니다.
    $('#jn_cnt').val(rowCount);

    // 만약 남은 행이 없다면, 테이블을 숨기고 안내 문구를 표시합니다.
    if (rowCount === 0) {
        $('#t_jnInfo').hide();
        $('#l_jnCount').show();
    } else {
        // 행이 남아있다면, 순번을 다시 정렬합니다.
        $('#jnBody tr').each(function(index) {
            $(this).find('.c_jn_num').text(index + 1);
        });
    }
}

$(document).ready(function() {
    // Datepicker 초기화
    $(".datepicker, .datepickerBirth").datepicker({
        dateFormat: 'yy-mm-dd',
        changeMonth: true,
        changeYear: true,
        yearRange: 'c-100:c+10'
    });

    // 신청 유형 변경 시 이벤트 처리
    $('#req_kind').on('change', function() {
        var selectedValue = $(this).val();
        var previousValue = $(this).data('previous-value');
        
        // 이전 값과 다를 때만 초기화 (처음 로드 시에는 초기화 안 함)
        if (previousValue !== undefined && previousValue !== selectedValue) {
            // 필드 초기화
            $('#req_nm').val(''); // 성명/기관명
            $('#birth1').val(''); // 생년월일 (화면 표시용)
            $('#birth').val(''); // 생년월일 (hidden)
            $('#ceo').val(''); // 대표자
            $('#birth2').val(''); // 법인등록번호
            $('#busi_no').val(''); // 사업자등록번호
            $('#pri_busi_nm').val(''); // 개인사업장명
            $('#grp_reqst_se').val(''); // 신청구분
            
            // 라디오 버튼 초기화
            $('input[name="req_sex"]').prop('checked', false);
            $('#req_sex3').prop('checked', true); // '없음' 선택
            
            // 체크박스 초기화
            $('#pri_business_yn1').prop('checked', false);
            $('#pri_business_yn').val('N');
            $('#profit_yn1').prop('checked', false);
            $('#profit_yn').val('N');
        }
        
        // 이전 값 저장
        $(this).data('previous-value', selectedValue);
        
        if (selectedValue === 'P') { // 개인
            $('#div_jnInfo').show();
            $('.p_birth1').show();
            $('.p_birth2').hide();
            $('.p_ceo').hide();
            $('.p_pri_busi').show();
            $('.p_pri_busi_1').hide(); // 사업자등록번호, 개인사업장명 숨김
            $('.tr_grp_reqst').hide();
            $('#profit_yn_label').hide();
        } else if (selectedValue === 'G') { // 단체
            $('#div_jnInfo').hide();
            $('.p_birth1').hide();
            $('.p_birth2').show();
            $('.p_ceo').show();
            $('.p_pri_busi').hide();
            $('.p_pri_busi_1').show(); // 사업자등록번호, 개인사업장명 표시
            $('.tr_grp_reqst').show();
            $('#profit_yn_label').show();
        } else { // 선택 안함
            $('#div_jnInfo').hide();
            $('.p_birth1').show();
            $('.p_birth2').hide();
            $('.p_ceo').hide();
            $('.p_pri_busi').show();
            $('.p_pri_busi_1').hide(); // 사업자등록번호, 개인사업장명 숨김
            $('.tr_grp_reqst').hide();
            $('#profit_yn_label').hide();
        }
    });

    // 개인사업자 체크박스 변경 시 이벤트 처리
    $('#pri_business_yn1').on('change', function() {
        if ($(this).is(':checked')) {
            $('.p_pri_busi_1').show();
            $('#pri_business_yn').val('Y');
        } else {
            $('.p_pri_busi_1').hide();
            $('#pri_business_yn').val('N');
        }
    });

    // 페이지 로드 시 초기 상태 설정
    var initialReqKind = $('#req_kind').val();
    $('#req_kind').data('previous-value', initialReqKind); // 초기값 저장
    
    if (initialReqKind === 'P') {
        $('#div_jnInfo').show();
    } else {
        $('#div_jnInfo').hide();
    }

    // 사회계층 여부' 라디오 버튼 변경 시 이벤트 처리
    $('input[name="social_yn"]').on('change', function() {
        if (this.value === 'Y') {
            $('#social_kind').prop('disabled', false);
        } else {
            $('#social_kind').prop('disabled', true);
            $('#social_kind').val(''); // 값을 초기화합니다.
        }
    });

    // 페이지 로드 시 '사회계층 여부' 초기 상태 확인
    if ($('input[name="social_yn"]:checked').val() === 'N') {
        $('#social_kind').prop('disabled', true);
    }

    // '사회계층 유형' 변경 시 이벤트 처리
    $('#social_kind').on('change', function() {
        if ($(this).val() === '3') {
            $('#children_cnt').show();
        } else {
            $('#children_cnt').hide();
            $('#children_cnt').val(''); // 값을 초기화합니다.
        }
    });

    // 페이지 로드 시 '사회계층 유형' 초기 상태 확인
    if ($('#social_kind').val() !== '3') {
        $('#children_cnt').hide();
    }

    // 우선순위 배정·집행 선택을 업데이트하는 함수
    function updatePrioritySelection() {
        const isImproveFd = $('input[name="improve_fd_yn"]:checked').val() === 'Y';
        const isFirstBuy = $('input[name="first_buy_yn"]:checked').val() === 'Y';
        const isSocial = $('input[name="social_yn"]:checked').val() === 'Y';

        if (isImproveFd || isFirstBuy || isSocial) {
            $('#priority_type1').prop('disabled', false).prop('checked', true);
        } else {
            $('#priority_type1').prop('disabled', true);
            $('#priority_type4').prop('checked', true);
        }
    }

    // 조건 변경 시 우선순위 업데이트
    $('input[name="improve_fd_yn"], input[name="first_buy_yn"], input[name="social_yn"]').on('change', function() {
        updatePrioritySelection();
    });

    // 페이지 로드 시 초기 상태 설정
    updatePrioritySelection();
});