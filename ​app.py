import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

# ==========================================
# 1. 소재 및 규격 데이터
# ==========================================
MATERIAL_DATA = {
    "ABS (HG-0760)": {"yield_strength": 45},
    "PC (SC-1100)": {"yield_strength": 62},
    "PC/ABS (HAC-8250)": {"yield_strength": 55},
    "PA6 (KN-120)": {"yield_strength": 70},
    "POM (N-109)": {"yield_strength": 65}
}

SCREW_DATA = {
    "M2.0": {"d": 2.0, "p": 0.4},
    "M2.6": {"d": 2.6, "p": 0.45},
    "M3.0": {"d": 3.0, "p": 0.5},
    "M4.0": {"d": 4.0, "p": 0.7}
}

st.set_page_config(page_title="Boss Sim Pro", layout="wide")
st.title("🔩 Boss Assembly Simulator Pro")

# 사이드바: 상세 설정
with st.sidebar:
    st.header("📐 Hardware Spec")
    sel_screw = st.selectbox("Screw 규격", list(SCREW_DATA.keys()))
    s_length = st.number_input("Screw 유효 길이 (mm)", value=6.0, step=0.5)
    
    st.header("🏗️ Boss Design")
    d_screw = SCREW_DATA[sel_screw]['d']
    p_screw = SCREW_DATA[sel_screw]['p']
    
    b_id = st.number_input("Boss ID (내경)", value=round(d_screw * 0.88, 2), step=0.05)
    b_od = st.number_input("Boss OD (외경)", value=round(d_screw * 2.2, 2), step=0.1)
    b_height = st.number_input("Boss Hole Depth (깊이)", value=s_length + 2.0, step=0.5)
    b_chamfer = st.number_input("Chamfer (C)", value=0.3, step=0.1)
    
    sel_mat = st.selectbox("Material", list(MATERIAL_DATA.keys()))

# ==========================================
# 3. 시각화 함수 (나사선 및 사이즈 표기)
# ==========================================
def draw_assembly(progress=0, is_simulating=False):
    # 창 크기를 줄이기 위해 figsize 조정 (5, 7 -> 4, 6)
    fig, ax = plt.subplots(figsize=(4, 6))
    
    # Boss 그리기
    boss_color = 'silver'
    ax.plot([-b_od/2, -b_od/2, -b_id/2-b_chamfer, -b_id/2, -b_id/2], [0, b_height, b_height, b_height-b_chamfer, 0], color='black', lw=2)
    ax.plot([b_od/2, b_od/2, b_id/2+b_chamfer, b_id/2, b_id/2], [0, b_height, b_height, b_height-b_chamfer, 0], color='black', lw=2)
    
    # Screw 정보 텍스트 (명시적 표기)
    info_text = f"Spec: {sel_screw}\nPitch: {p_screw}mm\nLength: {s_length}mm"
    ax.text(-b_od*1.2, b_height+2, info_text, fontsize=9, bbox=dict(facecolor='white', alpha=0.5))

    if is_simulating:
        # 2초 시뮬레이션을 위한 위치 계산 (y축 이동)
        start_y = b_height + 1
        end_y = b_height - s_length
        current_y = start_y - (progress * (start_y - end_y))
        
        # Screw Body (나사선 표현)
        ax.add_patch(plt.Rectangle((-d_screw/2, current_y), d_screw, s_length, color='gray', alpha=0.9))
        
        # 나사선(Thread) 시각화: 지그재그 패턴
        thread_steps = int(s_length / p_screw)
        for j in range(thread_steps):
            ty = current_y + (j * p_screw)
            ax.plot([-d_screw/2, d_screw/2], [ty, ty + p_screw/2], color='white', lw=0.5, alpha=0.6)
            
        # Screw Head
        ax.add_patch(plt.Rectangle((-d_screw, current_y + s_length), d_screw*2, 0.8, color='black'))

    ax.set_xlim(-b_od * 1.5, b_od * 1.5)
    ax.set_ylim(-1, b_height + 5)
    ax.set_aspect('equal')
    ax.axis('off')
    return fig

# ==========================================
# 4. 실행부
# ==========================================
col_view, col_stat = st.columns([1, 1])

with col_view:
    st.subheader("🔍 Section View")
    plot_spot = st.empty()
    plot_spot.pyplot(draw_assembly())

with col_stat:
    st.subheader("📈 Simulation Control")
    if st.button("체결 시뮬레이션 실행 (2s)"):
        # 2초 시뮬레이션: 0.05초 간격으로 40프레임
        for i in range(41):
            plot_spot.pyplot(draw_assembly(progress=i/40, is_simulating=True))
            time.sleep(0.05)
        
        # 공학적 결과 분석
        interference = d_screw - b_id
        yield_str = MATERIAL_DATA[sel_mat]['yield_strength']
        
        st.divider()
        if s_length > b_height:
            st.error("🚨 설계 오류: Screw 길이가 Boss 홀 깊이보다 깁니다! (Bottoming Out)")
        elif interference <= 0:
            st.warning("⚠️ 체결력 없음: 내경이 너무 큽니다.")
        else:
            ratio = (b_od**2 + b_id**2) / (b_od**2 - b_id**2)
            stress = (interference / b_id) * 1000 * ratio
            sf = yield_str / stress
            
            if sf < 1.0:
                st.error(f"❌ 파손: 안전율 {sf:.2f} (응력 {stress:.1f}MPa)")
            elif sf < 1.5:
                st.warning(f"⚠️ 경고: 안전율 {sf:.2f} (백화 발생 가능)")
            else:
                st.success(f"✅ 양호: 안전율 {sf:.2f}")
