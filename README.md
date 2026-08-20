# Mario Kart — Controlador por Visão Computacional

Controla um jogo de corrida (ex: Mario Kart, num emulador) usando as mãos
na frente da webcam, como se estivesse segurando um volante de verdade.

## Gestos

| Gesto | Ação |
|---|---|
| Girar as duas mãos como um volante | Vira à esquerda / direita |
| Mãos niveladas | Segue reto (acelera) |
| Levantar o polegar da mão esquerda | Ré (segura enquanto o polegar estiver levantado) |
| Levantar o polegar da mão direita | Lança o item (um toque por gesto) |

A detecção usa a MediaPipe Hands (`models/hand_landmarker.task`, incluído
no projeto) para localizar os 21 pontos de cada mão. O ângulo do "volante"
é medido entre o centro da palma da mão esquerda e da direita; o gesto de
polegar é reconhecido quando os outros 4 dedos estão fechados e o polegar
aponta claramente pra cima.

As teclas são simuladas com `pynput`. O mapeamento padrão usa as setas do
teclado para direção/ré e espaço para o item — ajuste em
`detector/config.py` (`KEY_MAP`) para bater com o seu jogo ou emulador.

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Execução

```bash
python3 main.py
```

Uso

- Sente-se de frente pra câmera e levante as duas mãos como se estivesse
  segurando um volante, uma de cada lado da tela.
- Gire as mãos (uma sobe, a outra desce) para fazer curvas.
- Levante o polegar esquerdo para dar ré; levante o direito para lançar
  o item.
- Pressione `q` ou `ESC` para encerrar.

Observações

- Se a câmera não abrir, verifique se outro programa não está usando-a.
- No Linux, pode ser necessário permissão para acessar dispositivos de vídeo.
- `pynput` envia eventos de teclado padrão do SO; a maioria dos emuladores
  reconhece normalmente, mas alguns jogos com captura de input mais
  restrita (DirectInput/raw input) podem não responder — nesse caso,
  troque as teclas em `KEY_MAP` até achar uma combinação que o jogo aceite.
