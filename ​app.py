import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

# 1. 소재 데이터 (롯데케미칼 TDS 기반)
MATERIAL_DATA = {
    "ABS (HG-0760)": {"yield_strength": 45, "modulus": 2300},
    "PC (SC-1100)": {"yield_strength": 62, "modulus": 2400},
    "PC/ABS (HAC-8250)": {"yield_strength": 55, "modulus": 2500},
    "PA6 (KN-120)": {"yield_strength": 70, "modulus": 2800},
    "POM (N-109)": {"yield_strength": 65, "modulus": 2700}
}

SCREW_DATA = {
    "M2.0": {"d": 2.0, "p": 0.4},
    "M2.6": {"d": 2.6, "p": 0.45},
    "M3.0": {"d": 3.0, "p": 0.5}
}

st.set_page_config(page_title="Boss Assembly Sim", layout="wide")
st.title("🛠️ Boss Section Preview & Assembly Simulator")

# 사이드바 설정
with st.sidebar:
    st.header("📐 Design Parameters")
    sel_screw = st.selectbox("Screw Spec", list(SCREW_DATA.keys()))
    sel_mat = st.selectbox("Material", list(MATERIAL_DATA.keys()))
    
    d_screw = SCREW_DATA[sel_screw]['d']
    b_id = st.number_input("Boss ID (mm)", value=d_screw * 0.85, step=0.05)
    b_od = st.number_input("Boss OD (mm)", value=d_screw * 2.2, step=0.1)
    b_chamfer = st.number_input("Chamfer Size (C)", value=0.3, step=0.1)
    b_height = st.number_input("Boss Height (mm)", value=8.0, step=0.5)

# 2. 보스 단면 시각화 함수
def draw_section(progress=0, is_simulating=False):
    fig, ax = plt.subplots(figsize=(6, 8))
    
    # Boss 외곽 (Section)
    ax.plot([-b_od/2, -b_od/2, -b_id/2-b_chamfer, -b_id/2, -b_id/2, b_id/2, b_id/2, b_id/2+b_chamfer, b_od/2, b_od/2], 
            [0, b_height, b_height, b_height-b_chamfer, 0, 0, b_height-b_chamfer, b_height, b_height, 0], color='black', lw=2)
    
    # 치수 표기
    ax.annotate(f'OD {b_od}', xy=(b_od/2, b_height/2), xytext=(b_od/2+1, b_height/2), arrowprops=dict(arrowstyle='->'))
    ax.annotate(f'ID {b_id}', xy=(b_id/2, b_height/4), xytext=(b_id/2-2, b_height/4), arrowprops=dict(arrowstyle='->'))
    ax.annotate(f'C {b_chamfer}', xy=(b_id/2+b_chamfer/2, b_height-b_chamfer/2), color='blue')

    # 시뮬레이션 시 Screw 그리기
    if is_simulating:
        screw_y = b_height + 2 - (progress * (b_height + 1))
        # Screw Body
        ax.add_patch(plt.Rectangle((-d_screw/2, screw_y), d_screw, b_height, color='gray', alpha=0.7))
        # Screw Head (간략화)
        ax.add_patch(plt.Rectangle((-d_screw, screw_y + b_height), d_screw*2, 1, color='darkgray'))

    ax.set_xlim(-b_od, b_od)
    ax.set_ylim(-1, b_height + 5)
    ax.set_aspect('equal')
    ax.axis('off')
    return fig

# 메인 화면 구성
col_pre, col_res = st.columns([1, 1])

with col_pre:
    st.subheader("🖼️ Section Preview")
    preview_placeholder = st.empty()
    preview_placeholder.pyplot(draw_section())

with col_res:
    st.subheader("🚀 Assembly Simulation")
    if st.button("Start Assembly Simulation"):
        # 5초간 애니메이션 수행
        for i in range(101):
            preview_placeholder.pyplot(draw_section(progress=i/100, is_simulating=True))
            time.sleep(0.05) # 0.05 * 100 = 5초
        
        # 결과 계산
        interference = d_screw - b_id
        yield_str = MATERIAL_DATA[sel_mat]['yield_strength']
        ratio = (b_od**2 + b_id**2) / (b_od**2 - b_id**2)
        stress = (interference / b_id) * 1000 * ratio
        sf = yield_str / stress

        if sf < 1.0:
            st.error(f"❌ 파손 발생! (Safety Factor: {sf:.2f})")
            st.write("보스가 확장 응력을 견디지 못하고 세로로 쪼개졌습니다.")
        elif sf < 1.5:
            st.warning(f"⚠️ 백화 현상 주의 (Safety Factor: {sf:.2f})")
            st.write("조립은 되었으나 응력이 높아 조립부가 하얗게 변할 수 있습니다.")
        else:
            st.success(f"✅ 조립 성공! (Safety Factor: {sf:.2f})")
