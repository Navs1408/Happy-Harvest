import cv2
import mediapipe as mp

class HandTracker:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def get_index_tip(self, frame):
        # Do NOT flip here — frame is already flipped in game.py
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands.process(rgb)
        if result.multi_hand_landmarks:
            lm = result.multi_hand_landmarks[0].landmark
            # lm[8] = index fingertip
            # frame is already mirrored so x maps directly
            x = int(lm[8].x * self.screen_width)
            y = int(lm[8].y * self.screen_height)
            return (x, y)
        return None