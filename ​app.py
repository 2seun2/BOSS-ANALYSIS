import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# 1. 아세아볼트/KS 표준 규격 기반 데이터 (태핑 나사 2종 기준)
# ==========================================
SCREW_SPEC_DB = {
    "M2.0": {"major_d": 2.0, "minor_d": 1.4, "pitch": 0.4, "head_d": 3.5},
    "M2.6": {"major_d": 2.6, "minor_d": 1.9, "pitch": 0.45, "head_d": 4.5},
    "M3.0": {"major_d": 3.0, "minor_d": 2.2, "pitch": 0.5, "head_d": 5.5},
    "M4.0": {"major_d": 4.0, "minor_d": 2.9, "pitch": 0.7, "head_d": 7.0}
}

MATERIAL_DB = {
    "ABS (Lotte HG-0760)": {"yield": 45, "modulus": 2300},
    "PC (Lotte SC-1100)": {"yield": 62, "modulus": 2400},
    "PC/ABS (Lotte HAC-8250)": {"yield": 55, "modulus": 2500},
    "PA6 (Lotte KN-120)": {"yield": 70, "modulus": 2800},
    "POM (Lotte N-109)": {"yield": 65, "modulus": 2700}
}

st.set_page_config(page_title="Engineer Boss Sim", layout="wide")
st.title("🔩 Professional Boss-Screw Analysis (KS/Asia Bolt Standard)")

# 사이드바 설정
with st.sidebar:
    st.header("⚙️ Screw Specification")
    sel_name = st.selectbox("Screw Size", list(SCREW_SPEC_DB.keys()))
    spec = SCREW_SPEC_DB[sel_name]
    
    s_len = st.number_input("Nominal Length (L)", value=8.0, step=0.5)
    s_effective = s_len - (spec['pitch'] * 2) # 불완전 나사부 제외 유효 길이 추정
    
    st.header("🏗️ Boss Design")
    b_id = st.number_input("Boss Inner Dia (ID)", value=round(spec['major_d']*0.85, 2), step=0.05)
    b_od = st.number_input("Boss Outer Dia (OD)", value=round(spec['major_d']*2.2, 2), step=0.1)
    b_depth = st.number_input("Hole Depth", value=s_len + 1.0, step=0.5)
    b_c = st.number_input("Chamfer (C)", value=0.3, step=0.1)
    
    sel_mat = st.selectbox("Material", list(MATERIAL_DB.keys()))
    mat = MATERIAL_DB[sel_mat]

# ==========================================
# 2. 정밀 해석 및 시각화 로직
# ==========================================
def draw_detailed_view():
    fig, ax = plt.subplots(figsize=(4, 6))
    
    # 1. Boss Drawing
    ax.plot([-b_od/2, -b_od/2, -b_id/2-b_c, -b_id/2, -b_id/2, b_id/2, b_id/2, b_id/2+b_c, b_od/2, b_od/2],
            [0, b_depth, b_depth, b_depth-b_c, 0, 0, b_depth-b_c, b_depth, b_depth, 0], color='black', lw=2)
    
    # 2. Screw Drawing (Assembly State)
    screw_y_top = b_depth
    screw_y_bot = b_depth - s_len
    
    # Major/Minor Dia 표현
    ax.add_patch(plt.Rectangle((-spec['minor_d']/2, screw_y_bot), spec['minor_d'], s_len, color='gray', alpha=0.5))
    
    # Threads (나사산 zigzag)
    thread_y = np.arange(screw_y_bot + 0.5, screw_y_top, spec['pitch'])
    for y in thread_y:
        ax.plot([-spec['major_d']/2, spec['major_d']/2], [y, y + spec['pitch']/2], color='darkblue', lw=0.8)
    
    # Head
    ax.add_patch(plt.Rectangle((-spec['head_d']/2, screw_y_top), spec['head_d'], 1.2, color='black'))

    ax.set_xlim(-b_od, b_od)
    ax.set_ylim(-1, b_depth + 4)
    ax.set_aspect('equal')
    ax.axis('off')
    return fig

# ==========================================
# 3. 메인 화면 출력
# ==========================================
col1, col2 = st.columns([4, 6])

with col1:
    st.subheader("📐 Assembly Section")
    st.pyplot(draw_detailed_view())

with col2:
    st.subheader("📊 Engineering Analysis")
    
    # 정확한 간섭량 해석 (Interference Analysis)
    # 나사산이 파고드는 깊이가 핵심
    engagement = (spec['major_d'] - b_id) / 2
    
    # Hoop Stress calculation (Thick-walled cylinder theory)
    # P = E * (interference) / ID 공식 응용
    interference_ratio = (spec['major_d'] - b_id) / b_id
    stress = mat['modulus'] * interference_ratio * ((b_od**2 + b_id**2) / (b_od**2 - b_id**2)) * 0.1 # 실험적 보정 계수
    
    sf = mat['yield'] / stress

    # 결과 대시보드
    st.write(f"**Target Screw:** {sel_name} ({spec['major_d']} x {s_len}L)")
    c1, c2, c3 = st.columns(3)
    c1.metric("Screw 골경 ($d_1$)", f"{spec['minor_d']} mm")
    c2.metric("나사산 높이 ($h$)", f"{(spec['major_d']-spec['minor_d'])/2:.2f} mm")
    c3.metric("실제 산 걸림량", f"{engagement:.2f} mm")

    st.divider()
    
    if sf < 1.0:
        st.error(f"❌ 파손 위험 (안전율: {sf:.2f})")
        st.markdown(f"- **해석:** 발생 응력(**{stress:.1f} MPa**)이 소재 항복 강도(**{mat['yield']} MPa**)를 초과합니다.")
        st.markdown("- **조치:** Boss 내경(ID)을 확대하여 나사산 걸림량을 줄이거나 OD를 보강하십시오.")
    elif sf < 1.5:
        st.warning(f"⚠️ 설계 주의 (안전율: {sf:.2f})")
        st.write("조립은 가능하나 환경 응력 균열(ESC) 또는 백화 현상이 발생할 수 있습니다.")
    else:
        st.success(f"✅ 설계 적합 (안전율: {sf:.2f})")

    st.info(f"💡 **기구 팁:** {sel_mat} 소재에서 {sel_name} 체결 시, 추천 Boss ID는 {spec['major_d']*0.88:.2f}mm 내외입니다.")
