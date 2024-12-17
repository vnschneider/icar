import cv2
import mediapipe as mp
import serial
import time

# Configuração da porta serial (substitua 'COMx' pela sua porta Bluetooth)
bluetooth_port = "COM4"  # Exemplo: 'COM5' no Windows ou '/dev/ttyUSB0' no Linux
baudrate = 9600  # Velocidade de comunicação

# Inicia a conexão serial
ser = serial.Serial(bluetooth_port, baudrate)
time.sleep(2)  # Aguarda a inicialização da comunicação

# Inicializa a captura de vídeo
cap = cv2.VideoCapture(0)

# Inicializa mediapipe para detectar as mãos
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

# Função para enviar comandos para o Arduino via Bluetooth
def send_command(command):
    ser.write(command.encode())

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Converte a imagem para RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    # Desenha a mão detectada
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # Processa gestos com base nas coordenadas dos pontos de referência
        for hand_landmarks in results.multi_hand_landmarks:
            # Obtém a posição de alguns pontos de referência das mãos
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

            # Exemplo de gesto para controle (baseado na posição do polegar e indicador)
            if thumb_tip.y < index_tip.y:  # Gesto para frente
                send_command('F')  # Envia comando "FORWARD" para o Arduino
            elif thumb_tip.y > index_tip.y:  # Gesto para trás
                send_command('B')  # Envia comando "BACKWARD" para o Arduino
            else:
                send_command('S')  # Envia comando "STOP" para o Arduino

    # Exibe o frame com as mãos detectadas
    cv2.imshow("Hand Gesture Control", frame)

    # Interrompe com a tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
