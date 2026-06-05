#  Happy Harvest

A real-time hand-tracking fruit slicing game built with Python. Use your webcam and index finger as a blade to slice flying fruits — but dodge the worms or lose a life!

---

##  How to Play

- **Slice fruits** (apple, watermelon, pineapple) with your index finger to earn **+1 point**
- **Miss a fruit** = **-1 point**
- **Slice a worm** = **-1 life** (shown as hearts at the top)
- **3 worms sliced** = Game Over
- Press **R** to restart
- Press **ESC** to quit

---

##  Features

-  **Hand tracking** — uses your webcam to track your index fingertip in real time
-  **Lives system** — 3 hearts displayed at the top, one disappears per worm sliced
-  **High score tracker** — your best score is saved and shown on the start screen
-  **Splash screen** — raise your finger to start the game
-  **Game Over screen** — shows your final score and best score with a cat meme

---

##  Project Structure


HappyHarvest/
├── assets/
│   ├── Apple.png
│   ├── Watermellon.png
│   ├── Pineapple.png
│   ├── Worm.png
│   └── Cat.jpg
├── game.py               # Main game loop
├── fruit.py              # Fruit class
├── hand_tracking.py      # Webcam + MediaPipe hand tracking
├── launch.command        # One-click launcher (Mac)
├── highscore.json        # Auto-generated, saves your best score
├── requirements.txt      # Python dependencies
└── README.md


---

##  Setup & Installation

### Requirements
- Mac (tested on MacBook Air M1)
- Anaconda / Miniconda
- Webcam

### First-time Setup

**1. Create a clean conda environment**
```bash
conda create -n happyharvest python=3.11 -y
conda activate happyharvest
```

**2. Install dependencies**
```bash
pip install pygame opencv-python mediapipe==0.10.9 pillow
```

---

##  Running the Game

### Option 1 — One-click launcher
Double click `launch.command` in your HappyHarvest folder in Finder.

### Option 2 — Terminal
```bash
conda activate happyharvest
cd /Users/navya/HappyHarvest
python game.py
```

---

##  Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.11 | Core language |
| Pygame | Game window and rendering |
| OpenCV (cv2) | Webcam feed capture |
| MediaPipe | Hand landmark detection |
| Pillow | Image loading |

---

##  Troubleshooting

**`numpy.core.umath failed to import`**
```bash
pip uninstall numpy -y && pip install numpy
```

**`module 'mediapipe' has no attribute 'solutions'`**
```bash
pip install mediapipe==0.10.9
```

**Game opens in wrong environment**
Make sure terminal shows `(happyharvest)` before running. If it says `(base)`, run `conda activate happyharvest` first.

