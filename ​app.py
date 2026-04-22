import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

# ==========================================
# 1. 소재 및 규격 데이터 (롯데케미칼 TDS 기반)
# ==========================================
MATERIAL_DATA = {
    "ABS (HG-0760)": {"yield_strength": 45, "modulus": 2300},
    "PC (SC-1100)": {"yield_strength": 62, "modulus": 2400},
    "PC/ABS (HAC-8250)": {"yield_strength": 55, "modulus": 2500},
    "PA6 (KN-120)": {"yield_strength": 70, "modulus": 2800},
    "PA66 (KN-330)": {"yield_strength": 80, "modulus": 3000},
    "PBT (4130G)": {"yield_strength": 50, "modulus": 2600},
    "POM (N-109)": {"yield_strength": 65, "modulus": 2700},
    "PP (J-340)": {"yield_strength": 30, "modulus": 1100},
    "HDPE (6060U)": {"yield_strength": 22, "modulus": 800},
    "HIPS (HI-425)": {"yield_strength": 25, "modulus": 1800}
}

SCREW_DATA = {
    "M2.0": {"d": 2.0, "p": 0.4},
    "M2.5": {"d": 2.5, "p": 0.45},
    "M2.6": {"d": 2.6, "p": 0.45},
    "M3.0": {"d": 3.0, "p": 0.5},
    "M4.0": {"d": 4.0, "p": 0.7}
}

# ==========================================
# 2. UI 및 설정
# ==========================================
st.set_page_config(page_title="Boss Design Simulator", layout="wide")
st.title("🛠️ Boss Section Preview & Assembly Simulator")

with st.sidebar:
    st.header("📐 Design Parameters")
    sel_screw = st.selectbox("Screw Spec", list(SCREW_DATA.keys()))
    sel_mat = st.selectbox("Material (Lotte Chemical)", list(MATERIAL_DATA.keys()))
    
    d_screw = SCREW_DATA[sel_screw]['d']
    b_id = st.number_input("Boss ID (mm)", value=round(d_screw * 0.88, 2), step=0.05)
    b_od = st.number_input("Boss OD (mm)", value=round(d_screw * 2.2, 2), step=0.1)
    b_chamfer = st.number_input("Chamfer Size (C)", value=0.3, step=0.1)
    b_height = st.number_input("Boss Height (mm)", value=8.0, step=0.5)

# ==========================================
# 3. 단면 시각화 함수
# ==========================================
def draw_section(progress=0, is_simulating=False):
    fig, ax = plt.subplots(figsize=(5, 7))
    
    # Boss 단면 좌표 계산 (Left & Right)
    # 외곽선 (Section View)
    left_x = [-b_od/2, -b_od/2, -b_id/2-b_chamfer, -b_id/2, -b_id/2]
    left_y = [0, b_height, b_height, b_height-b_chamfer, 0]
    
    right_x = [b_od/2, b_od/2, b_id/2+b_chamfer, b_id/2, b_id/2]
    right_y = [0, b_height, b_height, b_height-b_chamfer, 0]
    
    ax.plot(left_x, left_y, color='black', lw=2.5)
    ax.plot(right_x, right_y, color='black', lw=2.5)
    ax.fill_betweenx(left_y, left_x, -b_od/2, color='lightgray', alpha=0.3)
    ax.fill_betweenx(right_y, right_x, b_od/2, color='lightgray', alpha=0.3)
    
    # 치수선 표시
    ax.hlines(b_height, -b_od/2, b_od/2, linestyles='--', colors='gray', lw=0.5)
    ax.text(0, -0.8, f"ID {b_id} / OD {b_od}", ha='center', fontsize=10, fontweight='bold')
    
    # 시뮬레이션 시 Screw 삽입
    if is_simulating:
        # 나사가 위에서 아래로 내려오는 위치 계산
        screw_y_start = (b_height + 2) - (progress * (b_height + 1))
        # Screw Body
        rect = plt.Rectangle((-d_screw/2, screw_y_start), d_screw, b_height, color='steelblue', alpha=0.8, label='Screw')
        ax.add_patch(rect)
        # Screw Head
        head = plt.Rectangle((-d_screw, screw_y_start + b_height), d_screw*2, 0.8, color='black')
        ax.add_patch(head)

    ax.set_xlim(-b_od, b_od)
    ax.set_ylim(-1.5, b_height + 4)
    ax.set_aspect('equal')
    ax.axis('off')
    return fig

# ==========================================
# 4. 메인 실행부
# ==========================================
col_pre, col_res = st.columns([1, 1])

with col_pre:
    st.subheader("🖼️ Section Preview")
    preview_area = st.empty()
    preview_area.pyplot(draw_section())

with col_res:
    st.subheader("🚀 Assembly Simulation")
    st.write(f"현재 설정: {sel_mat} / {sel_screw}")
    
    if st.button("체결 시뮬레이션 시작"):
        # 5초 애니메이션 (약 50프레임)
        for i in range(51):
            preview_area.pyplot(draw_section(progress=i/50, is_simulating=True))
            time.sleep(0.08) # 약 4~5초 소요
        
        # 결과 판정
        interference = d_screw - b_id
        yield_str = MATERIAL_DATA[sel_mat]['yield_strength']
        
        if interference <= 0:
            st.error("❌ 체결 실패: 내경이 나사보다 커서 헛돕니다.")
        else:
            ratio = (b_od**2 + b_id**2) / (b_od**2 - b_id**2)
            stress = (interference / b_id) * 1000 * ratio
            sf = yield_str / stress
            
            st.divider()
            if sf < 1.0:
                st.error(f"🚨 파손 발생! (안전율: {sf:.2f})")
                st.write(f"발생 응력({stress:.1f}MPa) > 항복 강도({yield_str}MPa)")
                st.markdown("- **원인:** 과도한 간섭량으로 인해 보스가 세로로 할렬(Split)됨.")
            elif sf < 1.5:
                st.warning(f"⚠️ 백화 위험 (안전율: {sf:.2f})")
                st.write("조립은 성공했으나 응력 집중으로 인한 변색이 우려됩니다.")
            else:
                st.success(f"✅ 조립 성공 (안전율: {sf:.2f})")
                st.write("안정적인 설계 범위 내에 있습니다.")
