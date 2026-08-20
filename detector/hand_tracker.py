"""Detecção de mãos usando a MediaPipe Tasks API (HandLandmarker).

Devolve, a cada frame, a lista de mãos detectadas ordenada da esquerda
para a direita na imagem. Como o frame da câmera é espelhado antes de
chegar aqui (efeito selfie), "mais à esquerda na imagem" já corresponde à
mão esquerda da pessoa -- não precisamos do rótulo de handedness do
MediaPipe, que fica pouco confiável justamente por causa do espelhamento.
"""
import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

from .config import MIN_DETECTION_CONFIDENCE, MIN_TRACKING_CONFIDENCE, MODEL_PATH

# Pontos usados para estimar o centro da palma (mais estável que o pulso
# sozinho): pulso + as quatro bases dos dedos.
PALM_LANDMARKS = (0, 5, 9, 13, 17)

CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),          # polegar
    (0, 5), (5, 6), (6, 7), (7, 8),          # indicador
    (5, 9), (9, 10), (10, 11), (11, 12),     # médio
    (9, 13), (13, 14), (14, 15), (15, 16),   # anelar
    (13, 17), (17, 18), (18, 19), (19, 20),  # mínimo
    (0, 17),
]


class HandTracker:
    def __init__(self, num_hands=2, min_detection_confidence=None, min_tracking_confidence=None):
        base_options = mp_python.BaseOptions(model_asset_path=MODEL_PATH)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=num_hands,
            min_hand_detection_confidence=min_detection_confidence or MIN_DETECTION_CONFIDENCE,
            min_hand_presence_confidence=min_detection_confidence or MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=min_tracking_confidence or MIN_TRACKING_CONFIDENCE,
        )
        self._landmarker = vision.HandLandmarker.create_from_options(options)
        self._timestamp_ms = 0

    def process(self, frame_bgr):
        """Roda a detecção num frame BGR (formato do OpenCV) e devolve a
        lista de mãos ordenada por X crescente (esquerda -> direita).

        Cada mão é um dict com:
          'landmarks': os 21 pontos normalizados (x, y, z em 0-1) do MediaPipe
          'cx', 'cy': centro da palma em pixels, usado para ordenar as mãos
                      e medir o ângulo do volante
        """
        h, w = frame_bgr.shape[:2]
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        self._timestamp_ms += 1
        result = self._landmarker.detect_for_video(mp_image, self._timestamp_ms)

        hands = []
        for landmarks in result.hand_landmarks:
            palm_x = sum(landmarks[i].x for i in PALM_LANDMARKS) / len(PALM_LANDMARKS)
            palm_y = sum(landmarks[i].y for i in PALM_LANDMARKS) / len(PALM_LANDMARKS)
            hands.append({
                "landmarks": landmarks,
                "cx": palm_x * w,
                "cy": palm_y * h,
            })

        hands.sort(key=lambda hand: hand["cx"])
        return hands

    @staticmethod
    def draw_landmarks(frame_bgr, hands, colors=((0, 200, 0), (255, 160, 0))):
        h, w = frame_bgr.shape[:2]
        for idx, hand in enumerate(hands):
            color = colors[idx % len(colors)]
            points = [(int(lm.x * w), int(lm.y * h)) for lm in hand["landmarks"]]
            for a, b in CONNECTIONS:
                cv2.line(frame_bgr, points[a], points[b], color, 2)
            for x, y in points:
                cv2.circle(frame_bgr, (x, y), 3, (0, 120, 255), -1)

    def close(self):
        self._landmarker.close()
