import streamlit as st
from constants import MATERIAL_DATA, SCREW_DATA
from physics_engine import calculate_boss_stress

st.set_page_config(page_title="Boss Failure Sim", layout="centered")

st.title("⚙️ Boss Design & Failure Simulator")
st.info("기구 설계자를 위한 롯데케미칼 소재 기반 체결 시뮬레이터")

# 입력 섹션
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        selected_screw = st.selectbox("1. Screw 규격", list(SCREW_DATA.keys()))
        selected_mat = st.selectbox("2. Boss 재질", list(MATERIAL_DATA.keys()))
    with col2:
        screw_d = SCREW_DATA[selected_screw]['d']
        boss_id = st.number_input("3. Boss 내경(ID) mm", value=screw_d * 0.88, step=0.05)
        boss_od = st.number_input("4. Boss 외경(OD) mm", value=screw_d * 2.2, step=0.1)

# 유효성 검사 (M2.6 등 내경 오류 방지)
if boss_id >= screw_d:
    st.error(f"⚠️ 설계 오류: 내경({boss_id})이 나사 외경({screw_d})보다 큽니다. 체결력이 발생하지 않습니다.")
else:
    # 계산 실행
    yield_str = MATERIAL_DATA[selected_mat]['yield_strength']
    calc_stress = calculate_boss_stress(screw_d, boss_id, boss_od)
    safety_factor = yield_str / calc_stress if calc_stress > 0 else 0

    # 결과 출력
    st.divider()
    st.subheader("💡 분석 결과")
    
    m1, m2 = st.columns(2)
    m1.metric("발생 예상 응력", f"{calc_stress:.1f} MPa")
    m2.metric("안전율 (S.F)", f"{safety_factor:.2f}")

    if safety_factor < 1.0:
        st.error("🚨 파손 확정: Boss가 세로로 쪼개질(Cracking) 확률이 매우 높습니다.")
    elif safety_factor < 1.5:
        st.warning("⚠️ 주의: 백화 현상 혹은 조립 후 장기 크리프 파손이 우려됩니다.")
    else:
        st.success("✅ 안전: 적정 설계 범위입니다.")

    st.caption(f"소재 특징: {MATERIAL_DATA[selected_mat]['description']}")
