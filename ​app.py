import streamlit as st
import numpy as np

# ==========================================
# 1. 소재 및 규격 데이터 (롯데케미칼 TDS 기반)
# ==========================================
MATERIAL_DATA = {
    "ABS (HG-0760)": {"yield_strength": 45, "modulus": 2300, "desc": "범용, 우수한 밸런스"},
    "PC (SC-1100)": {"yield_strength": 62, "modulus": 2400, "desc": "고내열, 고충격 강도"},
    "PC/ABS (HAC-8250)": {"yield_strength": 55, "modulus": 2500, "desc": "가공성 및 내열성 조화"},
    "PA6 (KN-120)": {"yield_strength": 70, "modulus": 2800, "desc": "고강성, 기계적 강도 우수"},
    "PA66 (KN-330)": {"yield_strength": 80, "modulus": 3000, "desc": "엔지니어링 플라스틱의 표준"},
    "PBT (4130G)": {"yield_strength": 50, "modulus": 2600, "desc": "치수 안정성 및 전기 특성"},
    "POM (N-109)": {"yield_strength": 65, "modulus": 2700, "desc": "낮은 마찰 계수, 내마모성"},
    "PP (J-340)": {"yield_strength": 30, "modulus": 1100, "desc": "내화학성, 비중 낮음"},
    "HDPE (6060U)": {"yield_strength": 22, "modulus": 800, "desc": "저온 충격 강도 우수"},
    "HIPS (HI-425)": {"yield_strength": 25, "modulus": 1800, "desc": "우수한 성형성"}
}

SCREW_DATA = {
    "M2.0": {"d": 2.0, "p": 0.4},
    "M2.5": {"d": 2.5, "p": 0.45},
    "M2.6": {"d": 2.6, "p": 0.45},
    "M3.0": {"d": 3.0, "p": 0.5},
    "M4.0": {"d": 4.0, "p": 0.7}
}

# ==========================================
# 2. 핵심 계산 로직 (Physics Engine)
# ==========================================
def calculate_analysis(d_screw, id_boss, od_boss, yield_str):
    # 간섭량 계산
    interference = d_screw - id_boss
    
    # 1단계: 체결 불가능성 체크 (M2.6 이슈 반영)
    if interference <= 0:
        return None, "Error: Screw가 Boss 내경보다 작거나 같습니다. (체결력 없음)"
    
    # 2단계: Hoop Stress 계산 (Lamé's Thick-walled Cylinder Theory)
    # 실제 기구 설계에서는 간섭량에 의한 변형률(Strain)을 응력으로 변환
    try:
        ratio = (od_boss**2 + id_boss**2) / (od_boss**2 - id_boss**2)
        # 압력 P를 간섭량과 비례관계로 가정한 단순화 모델
        stress = (interference / id_boss) * 1000 * ratio 
        safety_factor = yield_str / stress
        return {"stress": stress, "sf": safety_factor}, "Success"
    except ZeroDivisionError:
        return None, "Error: 치수 입력 오류 (OD와 ID가 동일함)"

# ==========================================
# 3. UI 구성 (Streamlit)
# ==========================================
st.set_page_config(page_title="Boss Failure Sim", page_icon="⚙️")

st.title("⚙️ Boss Failure Simulator")
st.markdown("---")

# 레이아웃 분할
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 Design Input")
    sel_screw = st.selectbox("Screw 규격 선택", list(SCREW_DATA.keys()))
    sel_mat = st.selectbox("Boss 재질 선택", list(MATERIAL_DATA.keys()))
    
    screw_d = SCREW_DATA[sel_screw]['d']
    mat_yield = MATERIAL_DATA[sel_mat]['yield_strength']
    
    # 입력값 가이드 제공
    b_id = st.number_input(f"Boss 내경 (추천: {screw_d*0.85:.2f}~{screw_d*0.9:.2f})", 
                           value=round(screw_d * 0.88, 2), step=0.01)
    b_od = st.number_input(f"Boss 외경 (추천: {screw_d*2.0:.1f} 이상)", 
                           value=round(screw_d * 2.2, 2), step=0.1)

# 계산 실행
result, status = calculate_analysis(screw_d, b_id, b_od, mat_yield)

with col2:
    st.subheader("🔍 Analysis Result")
    if "Error" in status:
        st.error(status)
    else:
        stress = result['stress']
        sf = result['sf']
        
        st.metric("발생 예상 응력 (Hoop)", f"{stress:.1f} MPa")
        st.metric("안전율 (Safety Factor)", f"{sf:.2f}")

        if sf < 1.0:
            st.error("🚨 CRITICAL: 보스 즉시 파손 위험! (내경 확대 또는 외경 보강 필요)")
        elif sf < 1.5:
            st.warning("⚠️ WARNING: 백화 현상 및 장기 크리프 파손 주의")
        else:
            st.success("✅ SAFE: 안정적인 설계 범위입니다.")

st.markdown("---")
st.caption(f"**Selected Material Note:** {MATERIAL_DATA[sel_mat]['desc']}")
