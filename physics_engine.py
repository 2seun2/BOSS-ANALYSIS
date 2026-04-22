import numpy as np

def calculate_boss_stress(d_screw, id_boss, od_boss):
    """
    Hoop Stress(원주 응력) 계산
    간섭량(Interference)에 따른 내압을 추정하여 Boss에 걸리는 최대 응력 산출
    """
    interference = d_screw - id_boss
    if interference <= 0:
        return 0
    
    # 두께비에 따른 응력 집중 계수 반영 (Lamé's equation)
    # 실제 압력 P는 재질의 탄성 계수와 간섭량의 함수이나, 시뮬레이션을 위해 정규화된 압력 모델 적용
    ratio = (od_boss**2 + id_boss**2) / (od_boss**2 - id_boss**2)
    
    # 간섭률(Interference Rate) 기반 단순화된 stress 산출 공식
    stress = (interference / id_boss) * 1000 * ratio 
    return stress
