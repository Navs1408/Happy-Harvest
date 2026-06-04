#  Happy Harvest

A hand-tracking fruit slicing game built with Python, OpenCV, MediaPipe, and Pygame. Slice fruits flying across your webcam feed using just your index finger — but watch out for worms!

---

##  How to Play

- **Slice fruits** (apple, watermelon, pineapple) with your index finger to earn points
- Miss a fruit= -1 point
- Slice a worm = -1 point + 1 worm strike
- 3 worm strikes = Game Over
- Press R to restart
- Press ESC to quit

---

##  Project Structure

```
HappyHarvest/
├── game.py               # Main game loop
├── fruit.py              # Fruit class (movement, drawing, hit detection)
├── hand_tracking.py      # Webcam hand tracking via MediaPipe
├── launch.command        # One-click launcher (Mac)
├── requirements.txt      # Python dependencies
├── Apple.png             # Fruit image
├── Watermellon.png       # Fruit image
├── Pineapple.png         # Fruit image
├── Worm.png              # Worm image (the bomb!)
└── Cat.jpg               # Game Over screen image
```

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

### Option 1 — One-click launcher (easiest)
Double click `launch.command` in your HappyHarvest folder in Finder.

### Option 2 — Terminal
```bash
conda activate happyharvest
cd /Users/navya/HappyHarvest
python game.py
```

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.11 | Core language |
| Pygame | Game window, rendering, input |
| OpenCV (cv2) | Webcam feed capture |
| MediaPipe | Hand landmark detection |
| Pillow | Image loading support |

---

##  Troubleshooting

`numpy.core.umath failed to import`
```bash
pip uninstall numpy -y
pip install numpy
```

`module 'mediapipe' has no attribute 'solutions'`
```bash
pip install mediapipe==0.10.9
```

Game opens in wrong environment
Always make sure you see `(happyharvest)` in your terminal before running. If it says `(base)`, run `conda activate happyharvest` first.

Hand tracking feels off
Make sure your webcam is unobstructed and you're in decent lighting. Hold your index finger clearly extended and move slowly at first to calibrate.