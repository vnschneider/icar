import cv2
import mediapipe as mp
import serial
import time

# Configuração da comunicação serial com o Arduino
arduino = serial.Serial('COM7', 9600)  # Altere para a porta serial do seu Arduino
time.sleep(2)  # Aguardar a conexão serial estabilizar

# Inicia a captura da câmera
cap = cv2.VideoCapture(0)

# Inicializando MediaPipe para detecção de mãos
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

gesto = ""  # Variável para armazenar o gesto detectado

def detectar_gesto(landmarks):
    # Função para determinar o gesto com base nos pontos de referência
    thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    middle_tip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    ring_tip = landmarks[mp_hands.HandLandmark.RING_FINGER_TIP]
    pinky_tip = landmarks[mp_hands.HandLandmark.PINKY_TIP]
    
    # Posições dos pontos do dedo indicador e polegar
    thumb_ip = landmarks[mp_hands.HandLandmark.THUMB_IP]
    index_ip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_IP]
    middle_ip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_IP]
    
    # Detectando gestos com base nos pontos dos dedos
    if thumb_tip.y < index_tip.y and middle_tip.y < index_tip.y and ring_tip.y < middle_tip.y and pinky_tip.y < ring_tip.y:
        return "Mao Fechada"  # Todos os dedos fechados
    elif thumb_tip.y > index_tip.y and middle_tip.y > index_tip.y and ring_tip.y > middle_tip.y and pinky_tip.y > ring_tip.y:
        return "Mao Aberta"  # Todos os dedos estendidos
    elif index_tip.y < thumb_tip.y and middle_tip.y < index_tip.y and ring_tip.y < middle_tip.y and pinky_tip.y < ring_tip.y:
        return "Paz e Amor"  # Indicador e médio estendidos (V)
    elif pinky_tip.y < index_tip.y and thumb_tip.y < pinky_tip.y and middle_tip.y < pinky_tip.y and ring_tip.y < middle_tip.y:
        return "Rock"  # Indicador e mínimo estendidos
    elif thumb_tip.y < index_tip.y and pinky_tip.y < index_tip.y and middle_tip.y < index_tip.y and ring_tip.y < middle_tip.y:
        return "Hangloose"  # Polegar e mínimo estendidos
    else:
        return "Gestos Incompletos"  # Caso não detecte um gesto claro

while True:
    ret, frame = cap.read()
    
    if not ret:
        break

    # Convertendo o quadro para RGB (necessário para o MediaPipe)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Processando a imagem para detectar as mãos
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for landmarks in result.multi_hand_landmarks:
            # Desenhando os pontos de referência das mãos
            mp_draw.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Determinando o gesto com base nos pontos de referência
            gesto = detectar_gesto(landmarks.landmark)
            print(f"Gesto detectado: {gesto}")
            
            # Exibindo o gesto na tela
            cv2.putText(frame, gesto, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
            
            # Enviar o gesto para o Arduino
            arduino.write((gesto + '\n').encode())

    # Exibindo o vídeo com o gesto reconhecido
    cv2.imshow('Gestos', frame)

    # Saindo do loop quando pressionar a tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
