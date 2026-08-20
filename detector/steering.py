"""Estima a ação de direção a partir da posição das duas mãos, como se a
pessoa estivesse girando um volante invisível.

Convenção: `hands` é a lista de mãos detectadas pelo `HandTracker`, já
ordenada por posição X crescente (mão esquerda primeiro). O ângulo é
medido entre o centro da palma da mão esquerda e da direita: girar o
"volante" no sentido horário (mão direita desce, mão esquerda sobe) vira
à direita; o sentido anti-horário vira à esquerda -- igual a um volante
de verdade.
"""
import math
from typing import List, Optional, Tuple

from .config import STEER_DEAD_ZONE_DEG


def compute_steering_action(hands: List[dict]) -> Optional[Tuple[str, float]]:
    """Retorna (ação, ângulo_graus) ou None se as duas mãos não estiverem visíveis.

    ação ∈ {"FORWARD", "LEFT", "RIGHT"}.
    ângulo positivo = mão direita mais baixa que a esquerda (giro horário).
    """
    if len(hands) != 2:
        return None

    left, right = hands[0], hands[1]
    dx = right["cx"] - left["cx"]
    dy = right["cy"] - left["cy"]
    if dx == 0:
        dx = 1e-6

    angle_deg = math.degrees(math.atan2(dy, dx))

    if angle_deg > STEER_DEAD_ZONE_DEG:
        return "RIGHT", angle_deg
    if angle_deg < -STEER_DEAD_ZONE_DEG:
        return "LEFT", angle_deg
    return "FORWARD", angle_deg
