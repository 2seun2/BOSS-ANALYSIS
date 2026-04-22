import streamlit as st
import pandas as pd
from constants import MATERIAL_DATA, SCREW_DATA

def calculate_hoop_stress(d_screw, id_boss, od_boss):
    """기구학적 Hoop Stress 계산 로직"""
    interference = d_screw - id_boss
    if interference <= 0:
        return 0
    
    # Lamé Equation: 내압에 의한 최대 원주 방향 응력
    # 간섭량에 비례하는 가상의 압력 P 산출 (단순화 모델)
    pressure = (interference / id_boss) * 100  # 계수는 재질 탄성계수에 따라 보정 가능
    stress = pressure * ((od_boss**2 + id_boss**2) / (od_boss**2 - id_boss**2))
    return stress

def main():
    st.set_page_config(page_title="Boss Design Simulator", page_icon="⚙️")
    st.title("🚀 Boss Failure Analysis Tool")
    st.markdown("---")

    # Sidebar: Input Parameters
    with st.sidebar:
        st.header("Project Settings")
        selected_mat = st.selectbox("Material (Lotte Chemical)", list(MATERIAL_DATA.keys()))
        selected_screw = st.selectbox("Screw Spec", list(SCREW_DATA.keys()))
        
        st.header("Geometry")
        boss_id = st.number_input("Boss ID (mm)", value=SCREW_DATA[selected_screw]['d'] * 0.8)
        boss_od = st.number_input("Boss OD (mm)", value=SCREW_DATA[selected_screw]['d'] * 2.0)

    # Calculation
    yield_str = MATERIAL_DATA[selected_mat]['yield_strength']
    screw_d = SCREW_DATA[selected_screw]['d']
    calc_stress = calculate_hoop_stress(screw_d, boss_id, boss_od)
    
    if calc_stress > 0:
        safety_factor = yield_str / calc_stress
    else:
        safety_factor = float('inf')

    # Dashboard Display
    st.subheader(f"Analysis: {selected_mat} + {selected_screw}")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Max Hoop Stress", f"{calc_stress:.1f} MPa")
    m2.metric("Yield Strength", f"{yield_str} MPa")
    m3.metric("Safety Factor", f"{safety_factor:.2f}")

    # GitHub 협업을 위한 피드백 섹션
    if safety_factor < 1.2:
        st.error("❗ 파손 위험: 보스 균열(Cracking) 가능성이 매우 높습니다.")
        st.info("💡 제안: OD를 키우거나, Screw 간섭량을 줄이기 위해 ID를 조정하세요.")
    elif safety_factor < 2.0:
        st.warning("⚠️ 주의: 장기 크리프(Creep)에 의한 백화 현상이 발생할 수 있습니다.")
    else:
        st.success("✅ 안전: 적정 설계 범위 내에 있습니다.")

if __name__ == "__main__":
    main()
