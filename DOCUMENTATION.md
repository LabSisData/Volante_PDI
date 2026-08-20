# Mario Kart — Documentação técnica

Controlador de teclado por visão computacional: a webcam capta as duas
mãos, a MediaPipe Hands extrai os pontos de referência (landmarks) de
cada uma, e esses pontos viram ações de jogo (direção, ré, item) que são
enviadas como teclas simuladas via `pynput`.

## Estrutura

- `main.py`: laço principal — captura o frame, roda a detecção, traduz
  gestos em teclas e desenha a interface de depuração.
- `detector/hand_tracker.py`: `HandTracker` — encapsula a MediaPipe Tasks
  API (`HandLandmarker`), devolve as mãos detectadas ordenadas da
  esquerda pra direita na imagem (`cx`, `cy` em pixels + os 21 landmarks
  normalizados).
- `detector/steering.py`: `compute_steering_action(hands)` — calcula o
  ângulo entre a mão esquerda e a direita e decide `FORWARD`/`LEFT`/`RIGHT`,
  como se fosse o giro de um volante.
- `detector/gestures.py`: `is_thumb_up(landmarks, ...)` — detecta o gesto
  de "polegar pra cima" (4 dedos fechados + polegar apontando pra cima).
- `detector/controller.py`: `KeyController` — mantém o estado de quais
  teclas devem estar pressionadas e sincroniza isso com `pynput`. A ré é
  "segurada" enquanto o gesto persistir; o item é disparado uma vez por
  borda de subida do gesto e mantido pressionado por `ITEM_HOLD_SECONDS`.
- `detector/ui.py`: desenhos de depuração (esqueleto das mãos, indicador
  de volante, status de ré/item, teclas ativas).
- `detector/config.py`: todos os parâmetros ajustáveis.
- `models/hand_landmarker.task`: modelo oficial da MediaPipe para detecção
  de mãos, incluso no projeto (não precisa baixar nada em tempo de
  execução).

## Como executar

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

## Lógica de direção (volante)

A mão esquerda e a direita são identificadas pela posição X na imagem já
espelhada (efeito selfie) — não pelo rótulo de handedness da MediaPipe,
que fica pouco confiável justamente por causa do espelhamento.

O ângulo é `atan2(right.cy - left.cy, right.cx - left.cx)`, em graus:

- Dentro de `STEER_DEAD_ZONE_DEG` (padrão 8°) → `FORWARD` (reto).
- Ângulo positivo (mão direita mais baixa, giro horário) → `RIGHT`.
- Ângulo negativo (mão direita mais alta, giro anti-horário) → `LEFT`.

Isso corresponde à forma natural de girar um volante físico.

## Lógica do gesto de polegar

`is_thumb_up` recebe os 21 landmarks de uma mão e considera o gesto
positivo quando:

1. Os 4 dedos (indicador, médio, anelar, mínimo) estão fechados — ponta
   (`tip`) abaixo da articulação intermediária (`pip`) na imagem.
2. O polegar aponta pra cima — cada junta (`MCP → IP → TIP`) fica
   progressivamente mais alta, e a ponta fica claramente acima do pulso.

`THUMB_MARGIN` e `FIST_MARGIN` (em `config.py`) controlam a folga contra
oscilação perto do limiar.

- Mão esquerda com polegar pra cima → `reverse_active = True` (ré,
  mantida enquanto durar o gesto).
- Mão direita com polegar pra cima → dispara o item na borda de subida
  do gesto (detectada em `main.py` comparando o frame atual com o
  anterior), mantido pressionado por `ITEM_HOLD_SECONDS`.

## Parâmetros e como ajustar (`detector/config.py`)

- `NUM_HANDS`, `MIN_DETECTION_CONFIDENCE`, `MIN_TRACKING_CONFIDENCE`:
  parâmetros de detecção da MediaPipe.
- `STEER_DEAD_ZONE_DEG`: quão inclinado o "volante" precisa ficar antes
  de virar — aumente se estiver virando sem querer, diminua se as curvas
  estiverem "duras".
- `THUMB_MARGIN`, `FIST_MARGIN`: folga da detecção de polegar — aumente
  se estiver disparando ré/item à toa; diminua se o gesto não estiver
  sendo reconhecido.
- `ITEM_HOLD_SECONDS`: por quanto tempo a tecla de item fica pressionada
  a cada lançamento.
- `KEY_MAP`: qual tecla cada ação (`FORWARD`, `REVERSE`, `LEFT`, `RIGHT`,
  `ITEM`) dispara — ajuste para bater com o seu jogo/emulador.

## Dicas de calibração

- Iluminação: a MediaPipe Hands é bem mais robusta a iluminação do que a
  antiga segmentação por cor de pele, mas ainda prefere um ambiente sem
  contraluz forte.
- Distância: mantenha as duas mãos visíveis por inteiro na câmera,
  mais ou menos na altura do peito, como se estivesse mesmo segurando um
  volante.
- Falsos positivos de item/ré: se o punho meio fechado já disparar o
  gesto sem querer, aumente `THUMB_MARGIN`/`FIST_MARGIN`.

## Próximos passos sugeridos

- Suporte a `pydirectinput`/`SendInput` como alternativa ao `pynput` em
  jogos Windows que não reagem a eventos de teclado padrão.
- Zona de "curva fechada" (ângulo grande) mapeada pra um segundo nível de
  giro, se o jogo suportar entrada analógica de direção.
- Calibração automática: usar o primeiro frame com as duas mãos visíveis
  para definir o ângulo neutro, corrigindo pequenas inclinações naturais
  da pessoa.
