import os

# Caminho do modelo de detecção de mãos (MediaPipe Tasks HandLandmarker)
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "hand_landmarker.task")

# Detecção de mãos
NUM_HANDS = 2
MIN_DETECTION_CONFIDENCE = 0.6
MIN_TRACKING_CONFIDENCE = 0.5

# Volante: ângulo (graus) entre o centro da mão esquerda e da mão direita.
# Abaixo desse limite o volante é considerado "reto".
STEER_DEAD_ZONE_DEG = 8

# Gesto de polegar para cima (margens em coordenadas normalizadas 0-1,
# contra oscilação perto do limiar)
THUMB_MARGIN = 0.03
FIST_MARGIN = 0.02

# Quantos segundos a tecla de item fica pressionada a cada lançamento
ITEM_HOLD_SECONDS = 0.15

# Mapeamento de ações para teclas -- ajuste para bater com o seu jogo/emulador.
# Aceita nomes especiais (up/down/left/right/space/enter/shift/ctrl) ou uma
# tecla de caractere único (ex: 'e', 'z', 'w').
KEY_MAP = {
    "FORWARD": "w",
    "REVERSE": "s",
    "LEFT": "a",
    "RIGHT": "d",
    "ITEM": "k",
}
