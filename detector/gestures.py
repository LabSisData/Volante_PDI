"""Detecção do gesto de "polegar para cima" a partir dos pontos de
referência da mão (MediaPipe Hand Landmarker).

Índices usados:
  0        = pulso
  2, 3, 4  = polegar (MCP, IP, TIP)
  6, 8     = indicador (PIP, TIP)
  10, 12   = médio (PIP, TIP)
  14, 16   = anelar (PIP, TIP)
  18, 20   = mínimo (PIP, TIP)
"""

FINGER_TIPS = [8, 12, 16, 20]
FINGER_PIPS = [6, 10, 14, 18]


def _fist_curled(landmarks, margin):
    """Os 4 dedos (fora o polegar) estão dobrados, como ao segurar o volante."""
    return all(landmarks[tip].y > landmarks[pip].y - margin for tip, pip in zip(FINGER_TIPS, FINGER_PIPS))


def is_thumb_up(landmarks, thumb_margin=0.03, fist_margin=0.02):
    """True quando os 4 dedos estão fechados e o polegar aponta pra cima.

    O polegar "aponta pra cima" quando cada junta fica progressivamente
    mais alta que a anterior (ponta acima da IP, IP acima do MCP) e a ponta
    fica claramente acima do pulso. Isso é robusto o bastante para a pose
    de "mão fechada no volante, levanta o polegar" sem exigir a mão
    perfeitamente vertical.
    """
    if not landmarks:
        return False
    if not _fist_curled(landmarks, fist_margin):
        return False

    wrist = landmarks[0]
    thumb_mcp, thumb_ip, thumb_tip = landmarks[2], landmarks[3], landmarks[4]

    pointing_up = (thumb_tip.y < thumb_ip.y - thumb_margin and
                   thumb_ip.y < thumb_mcp.y - thumb_margin)
    above_wrist = thumb_tip.y < wrist.y - thumb_margin
    return pointing_up and above_wrist
