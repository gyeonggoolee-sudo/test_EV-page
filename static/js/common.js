/**
 * EV 보조금 신청서 공통 JavaScript
 */

$(document).ready(function() {
    // Datepicker 초기화
    initDatepicker();
    
    // 폼 유효성 검사
    initFormValidation();
    
    // 동적 필드 표시/숨김
    initDynamicFields();
    
    // 숫자 입력 필드 포맷팅
    initNumberFormatting();
});

/**
 * Datepicker 초기화
 */
function initDatepicker() {
    // 계약일자
    $('#contract_day').datepicker({
        dateFormat: 'yy-mm-dd',
        changeMonth: true,
        changeYear: true,
        yearRange: '2020:2030',
        showButtonPanel: true
    });
    
    // 출고예정일자
    $('#delivery_sch_day').datepicker({
        dateFormat: 'yy-mm-dd',
        changeMonth: true,
        changeYear: true,
        yearRange: '2020:2030',
        showButtonPanel: true
    });
    
    // 생년월일
    $('#birth1').datepicker({
        dateFormat: 'yy-mm-dd',
        changeMonth: true,
        changeYear: true,
        yearRange: '1900:2025',
        showButtonPanel: true,
        onSelect: function(dateText, inst) {
            $('#birth').val(dateText);
        }
    });
}

/**
 * 폼 유효성 검사 초기화
 */
function initFormValidation() {
    // 폼 제출 시 유효성 검사
    $('#editForm').on('submit', function(e) {
        if (!validateForm()) {
            e.preventDefault();
            return false;
        }
    });
    
    // 필수 필드 실시간 검사
    $('input[required], select[required]').on('blur', function() {
        validateField($(this));
    });
    
    // 휴대폰 번호 포맷팅
    $('#mobile, #contact_mobile').on('input', function() {
        formatPhoneNumber($(this));
    });
}

/**
 * 폼 유효성 검사
 */
function validateForm() {
    let isValid = true;
    const errors = [];
    
    // 신청 유형 검사
    if (!$('#req_kind').val()) {
        errors.push('신청 유형을 선택해주세요.');
        isValid = false;
    }
    
    // 성명 검사
    if (!$('#req_nm').val().trim()) {
        errors.push('성명을 입력해주세요.');
        isValid = false;
    }
    
    // 생년월일 검사
    if (!$('#birth').val()) {
        errors.push('생년월일을 입력해주세요.');
        isValid = false;
    }
    
    // 성별 검사
    if (!$('input[name="req_sex"]:checked').length) {
        errors.push('성별을 선택해주세요.');
        isValid = false;
    }
    
    // 주소 검사
    if (!$('#addr').val().trim()) {
        errors.push('주소를 입력해주세요.');
        isValid = false;
    }
    
    // 연락처 검사
    if (!$('#phone').val().trim()) {
        errors.push('전화번호를 입력해주세요.');
        isValid = false;
    }
    
    if (!$('#mobile').val().trim()) {
        errors.push('휴대폰 번호를 입력해주세요.');
        isValid = false;
    }
    
    if (!$('#email').val().trim()) {
        errors.push('이메일을 입력해주세요.');
        isValid = false;
    }
    
    // 이메일 형식 검사
    if ($('#email').val() && !isValidEmail($('#email').val())) {
        errors.push('올바른 이메일 형식을 입력해주세요.');
        isValid = false;
    }
    
    // 신청차종 검사
    if (!$('#model_cd').val()) {
        errors.push('신청차종을 선택해주세요.');
        isValid = false;
    }
    
    // 신청대수 검사
    if (!$('#req_cnt').val() || parseInt($('#req_cnt').val()) <= 0) {
        errors.push('신청대수를 입력해주세요.');
        isValid = false;
    }
    
    if (errors.length > 0) {
        alert(errors.join('\n'));
    }
    
    return isValid;
}

/**
 * 개별 필드 유효성 검사
 */
function validateField($field) {
    const value = $field.val().trim();
    const isRequired = $field.prop('required') || $field.hasClass('required');
    
    if (isRequired && !value) {
        $field.addClass('error');
        return false;
    }
    
    $field.removeClass('error');
    return true;
}

/**
 * 이메일 유효성 검사
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * 휴대폰 번호 포맷팅
 */
function formatPhoneNumber($input) {
    let value = $input.val().replace(/[^0-9]/g, '');
    
    if (value.length >= 11) {
        value = value.substring(0, 11);
        value = value.replace(/(\d{3})(\d{4})(\d{4})/, '$1-$2-$3');
    } else if (value.length >= 7) {
        value = value.replace(/(\d{3})(\d{4})(\d+)/, '$1-$2-$3');
    } else if (value.length >= 3) {
        value = value.replace(/(\d{3})(\d+)/, '$1-$2');
    }
    
    $input.val(value);
}

/**
 * 동적 필드 표시/숨김 초기화
 */
function initDynamicFields() {
    // 신청 유형 변경 시
    $('#req_kind').on('change', function() {
        const reqKind = $(this).val();
        
        if (reqKind === 'G') {
            // 단체 선택 시
            $('.p_birth2').show();
            $('.p_birth1').hide();
            $('.p_ceo').show();
            $('.tr_grp_reqst').show();
        } else {
            // 개인 선택 시
            $('.p_birth1').show();
            $('.p_birth2').hide();
            $('.p_ceo').hide();
            $('.tr_grp_reqst').hide();
        }
    });
    
    // 개인사업자 체크박스 변경 시
    $('#pri_business_yn1').on('change', function() {
        if ($(this).is(':checked')) {
            $('#pri_business_yn').val('Y');
            $('.p_pri_busi_1').show();
        } else {
            $('#pri_business_yn').val('N');
            $('.p_pri_busi_1').hide();
        }
    });
    
    // 사회계층 여부 변경 시
    $('input[name="social_yn"]').on('change', function() {
        if ($(this).val() === 'Y') {
            $('#social_kind').prop('disabled', false);
        } else {
            $('#social_kind').prop('disabled', true);
            $('#social_kind').val('');
        }
    });
    
    // 미세먼지 개선효과가 높은 차량 구매자 여부 변경 시
    $('input[name="improve_fd_yn"]').on('change', function() {
        if ($(this).val() === 'Y') {
            $('#div_improve_fd_yn').show();
        } else {
            $('#div_improve_fd_yn').hide();
        }
    });
}

/**
 * 숫자 입력 필드 포맷팅
 */
function initNumberFormatting() {
    // 숫자만 입력 가능한 필드
    $('.intCheck').on('input', function() {
        $(this).val($(this).val().replace(/[^0-9]/g, ''));
    });
    
    // 금액 필드 포맷팅
    $('#req_total_amt_1, #req_gamt_1, #req_lamt_1, #req_add_lamt_1, #ext_req_add_lamt_1').on('blur', function() {
        formatAmount($(this));
    });
}

/**
 * 금액 포맷팅
 */
function formatAmount($input) {
    let value = $input.val().replace(/[^0-9]/g, '');
    if (value) {
        value = parseInt(value).toLocaleString('ko-KR');
        $input.val(value);
    }
}

/**
 * 주소 검색 팝업
 */
function popupAddress() {
    // 주소 검색 API 연동 (예: 다음 주소 API)
    // 실제 구현 시 주소 검색 API를 연동해야 합니다.
    alert('주소 검색 기능은 실제 주소 API 연동이 필요합니다.\n예: 다음 주소 API, 카카오 주소 API 등');
    
    // 예시: 다음 주소 API 사용 시
    /*
    new daum.Postcode({
        oncomplete: function(data) {
            $('#zipno').val(data.zonecode);
            $('#addr').val(data.address);
            $('#addr_detail').focus();
        }
    }).open();
    */
}

/**
 * 임시저장
 */
function goSave() {
    if (confirm('임시저장 하시겠습니까?')) {
        $('#saveGubun').val('temp');
        
        // AJAX로 임시저장
        const formData = $('#editForm').serialize();
        
        $.ajax({
            url: '/submit',
            type: 'POST',
            data: formData,
            success: function(response) {
                alert('임시저장이 완료되었습니다.');
            },
            error: function(xhr, status, error) {
                alert('임시저장 중 오류가 발생했습니다.');
                console.error(error);
            }
        });
    }
}

/**
 * 목록으로 이동
 */
function goList() {
    if (confirm('목록으로 이동하시겠습니까?\n입력한 내용이 저장되지 않을 수 있습니다.')) {
        window.location.href = '/';
    }
}

/**
 * 숫자만 입력 허용
 */
function onlyNumber(event) {
    const char = String.fromCharCode(event.which);
    if (!/[0-9]/.test(char)) {
        event.preventDefault();
    }
}

/**
 * 전화번호 포맷팅
 */
function formatPhone($input) {
    let value = $input.val().replace(/[^0-9]/g, '');
    
    if (value.length >= 10) {
        if (value.length === 10) {
            value = value.replace(/(\d{3})(\d{3})(\d{4})/, '$1-$2-$3');
        } else {
            value = value.replace(/(\d{3})(\d{4})(\d{4})/, '$1-$2-$3');
        }
    }
    
    $input.val(value);
}

/**
 * 사업자등록번호 포맷팅
 */
function formatBusinessNumber($input) {
    let value = $input.val().replace(/[^0-9]/g, '');
    
    if (value.length >= 10) {
        value = value.substring(0, 10);
        value = value.replace(/(\d{3})(\d{2})(\d{5})/, '$1-$2-$3');
    }
    
    $input.val(value);
}

/**
 * 법인등록번호 포맷팅
 */
function formatCorporateNumber($input) {
    let value = $input.val().replace(/[^0-9]/g, '');
    
    if (value.length >= 13) {
        value = value.substring(0, 13);
        value = value.replace(/(\d{6})(\d{7})/, '$1-$2');
    }
    
    $input.val(value);
}

/**
 * 폼 데이터 수집
 */
function collectFormData() {
    const formData = {};
    
    $('#editForm').find('input, select, textarea').each(function() {
        const $field = $(this);
        const name = $field.attr('name');
        const type = $field.attr('type');
        
        if (!name) return;
        
        if (type === 'checkbox' || type === 'radio') {
            if ($field.is(':checked')) {
                formData[name] = $field.val();
            }
        } else {
            formData[name] = $field.val();
        }
    });
    
    return formData;
}

/**
 * 폼 초기화
 */
function resetForm() {
    if (confirm('입력한 모든 내용을 초기화하시겠습니까?')) {
        $('#editForm')[0].reset();
        $('.error').removeClass('error');
    }
}

// 전역 함수로 export
window.popupAddress = popupAddress;
window.goSave = goSave;
window.goList = goList;
window.onlyNumber = onlyNumber;
window.formatPhone = formatPhone;
window.formatBusinessNumber = formatBusinessNumber;
window.formatCorporateNumber = formatCorporateNumber;
window.collectFormData = collectFormData;
window.resetForm = resetForm;

