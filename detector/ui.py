import math

import cv2

from .hand_tracker import HandTracker


def draw_hand_landmarks(frame, hands):
    HandTracker.draw_landmarks(frame, hands)


def draw_wheel_indicator(frame, steering_result, radius=42):
    """Desenha um volante circular no canto superior esquerdo, girando de
    acordo com o ângulo detectado entre as duas mãos."""
    cx, cy = 20 + radius, 20 + radius
    cv2.circle(frame, (cx, cy), radius, (60, 60, 60), -1)
    cv2.circle(frame, (cx, cy), radius, (200, 200, 200), 2)

    if not steering_result:
        cv2.putText(frame, "Mostre as 2 maos", (cx - radius, cy + radius + 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 220), 2)
        return

    action, angle_deg = steering_result
    color = (0, 200, 0) if action == "FORWARD" else (0, 180, 255)

    angle_rad = math.radians(angle_deg)
    dx = math.cos(angle_rad) * radius
    dy = math.sin(angle_rad) * radius
    cv2.line(frame, (int(cx - dx), int(cy - dy)), (int(cx + dx), int(cy + dy)), color, 4)
    cv2.circle(frame, (cx, cy), 5, color, -1)

    label = {"FORWARD": "Reto", "LEFT": "Esquerda", "RIGHT": "Direita"}[action]
    cv2.putText(frame, label, (cx - radius, cy + radius + 22),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)


def draw_gesture_status(frame, reverse_active, item_active):
    """Mostra se a ré e o item estão ativos no canto superior direito."""
    h, w = frame.shape[:2]
    y = 30
    rev_color = (0, 0, 220) if reverse_active else (90, 90, 90)
    item_color = (0, 200, 255) if item_active else (90, 90, 90)
    cv2.putText(frame, "RE (polegar esq.)", (w - 260, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, rev_color, 2)
    cv2.putText(frame, "ITEM (polegar dir.)", (w - 260, y + 26),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, item_color, 2)


def draw_controller_status(frame, key_ctrl):
    """Mostra as ações lógicas atualmente ativas, pra depuração."""
    h, _ = frame.shape[:2]
    try:
        actions = key_ctrl.active_actions()
        onoff = "ON" if getattr(key_ctrl, "_kb", None) is not None else "OFF"
        cv2.putText(frame, f"Teclado:{onoff}  Ativo: {','.join(actions) if actions else '-'}",
                    (8, h - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (220, 220, 220), 1)
    except Exception:
        pass
