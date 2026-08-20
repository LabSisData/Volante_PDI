import cv2

from detector.config import FIST_MARGIN, ITEM_HOLD_SECONDS, KEY_MAP, NUM_HANDS, THUMB_MARGIN
from detector.controller import KeyController
from detector.gestures import is_thumb_up
from detector.hand_tracker import HandTracker
from detector.steering import compute_steering_action
from detector.ui import draw_controller_status, draw_gesture_status, draw_hand_landmarks, draw_wheel_indicator


def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Erro: não foi possível abrir a câmera.")
        return

    tracker = HandTracker(num_hands=NUM_HANDS)
    key_ctrl = KeyController(key_map=KEY_MAP, item_hold_seconds=ITEM_HOLD_SECONDS)

    print("Segure as mãos como se estivesse com um volante (uma de cada lado da tela).")
    print("Gire as mãos para fazer curvas, levante o polegar esquerdo para dar ré")
    print("e o polegar direito para lançar o item. Pressione 'q' ou ESC para sair.")

    prev_item_thumb_up = False
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Falha ao capturar frame da câmera.")
                break

            frame = cv2.flip(frame, 1)
            hands = tracker.process(frame)

            steering = compute_steering_action(hands)
            steer_action = steering[0] if steering else None

            reverse_active = False
            item_edge = False

            if len(hands) >= 1:
                reverse_active = is_thumb_up(hands[0]["landmarks"], THUMB_MARGIN, FIST_MARGIN)
            if len(hands) >= 2:
                item_thumb_up = is_thumb_up(hands[1]["landmarks"], THUMB_MARGIN, FIST_MARGIN)
                item_edge = item_thumb_up and not prev_item_thumb_up
                prev_item_thumb_up = item_thumb_up
            else:
                prev_item_thumb_up = False

            key_ctrl.update(steer_action, reverse_active, item_edge)

            draw_hand_landmarks(frame, hands)
            draw_wheel_indicator(frame, steering)
            draw_gesture_status(frame, reverse_active, key_ctrl.item_active())
            draw_controller_status(frame, key_ctrl)

            cv2.imshow("Mario Kart Controller", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q") or key == 27:
                break
    finally:
        try:
            key_ctrl.release_all()
        except Exception:
            pass
        tracker.close()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
