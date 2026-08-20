"""Controlador de teclado: traduz ações lógicas (direção, ré, item) em
teclas de verdade pressionadas via `pynput`.

Usa `pynput` quando disponível; se não estiver instalado, vira um no-op
silencioso para o app continuar rodando (útil pra testar a visão
computacional sem travar tudo por causa do teclado).
"""
import time
from typing import Optional

try:
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except Exception:
    PYNPUT_AVAILABLE = False


class _NoOpController:
    def press(self, k):
        pass

    def release(self, k):
        pass


def _resolve_key(name: str):
    """Converte um nome do KEY_MAP (ex: 'up', 'space', 'e') numa tecla do pynput."""
    name = name.lower()
    if PYNPUT_AVAILABLE:
        special = {
            "up": keyboard.Key.up,
            "down": keyboard.Key.down,
            "left": keyboard.Key.left,
            "right": keyboard.Key.right,
            "space": keyboard.Key.space,
            "enter": keyboard.Key.enter,
            "shift": keyboard.Key.shift,
            "ctrl": keyboard.Key.ctrl,
        }
        if name in special:
            return special[name]
    return name  # tecla de caractere único, ex: 'e', 'z', 'w'


class KeyController:
    def __init__(self, key_map: dict, item_hold_seconds: float = 0.15):
        self._kb = keyboard.Controller() if PYNPUT_AVAILABLE else _NoOpController()
        self.key_map = {action: _resolve_key(key_name) for action, key_name in key_map.items()}
        self.item_hold_seconds = item_hold_seconds

        self._pressed = set()
        self._item_release_at: Optional[float] = None

    def update(self, steer_action: Optional[str], reverse_active: bool, item_edge: bool,
               now: Optional[float] = None):
        """Atualiza as teclas pressionadas para o estado atual.

        steer_action: 'LEFT' | 'RIGHT' | 'FORWARD' | None
        reverse_active: True enquanto o polegar esquerdo estiver levantado (segura a ré)
        item_edge: True só no frame em que o polegar direito acabou de subir (dispara o item)
        """
        now = time.time() if now is None else now

        desired = set()
        desired.add(self.key_map["REVERSE"] if reverse_active else self.key_map["FORWARD"])

        if steer_action == "LEFT":
            desired.add(self.key_map["LEFT"])
        elif steer_action == "RIGHT":
            desired.add(self.key_map["RIGHT"])

        if item_edge:
            self._item_release_at = now + self.item_hold_seconds
        if self._item_release_at is not None:
            if now < self._item_release_at:
                desired.add(self.key_map["ITEM"])
            else:
                self._item_release_at = None

        for key in list(self._pressed):
            if key not in desired:
                self._safe_release(key)
        for key in desired:
            if key not in self._pressed:
                self._safe_press(key)

    def item_active(self) -> bool:
        return self._item_release_at is not None

    def release_all(self):
        for key in list(self._pressed):
            self._safe_release(key)

    def active_actions(self):
        """Nomes das ações lógicas atualmente ativas (pra mostrar na tela)."""
        inverse = {key: action for action, key in self.key_map.items()}
        return sorted(inverse.get(k, str(k)) for k in self._pressed)

    def _safe_press(self, key):
        try:
            self._kb.press(key)
            self._pressed.add(key)
        except Exception:
            pass

    def _safe_release(self, key):
        try:
            self._kb.release(key)
        except Exception:
            pass
        self._pressed.discard(key)
