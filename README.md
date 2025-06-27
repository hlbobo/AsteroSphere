# 🚀 AsteroSphere

**AsteroSphere** is a fast-paced 2D arcade-style space shooter, inpired by Flappy Bird, Hill Climb Racing and Asteroids, where you pilot a spaceship, dodge asteroids, manage fuel, and blast obstacles to survive and score points.

## 🎮 Features

- Dynamic space-themed gameplay
- 3 rotation-based control modes
- Bullet firing and asteroid destruction
- Fuel management system
- Dash mechanics and power-ups
- Menu system with volume and control settings
- Local highscore saving

## 🛠 Requirements

- Python 3.8 or higher

## 📦 Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/hlbobo/asterosphere.git
   cd asterosphere
    ````

2. **Install dependencies:**

   ```bash
   pip install pygame
   ```

3. **Run the game:**

   ```bash
   python AsteroSphere.py
   ```

## 🎮 Controls

### The ship has 3 rotation states, each with different controls:

#### Rotation 1 (Default)

* `SPACE` – Jump
* `W` – Shoot
* `A` – Dash right
* `D` – Dash left

#### Rotation 2

* `SPACE` – Jump
* `D` – Shoot
* `A` – Dash right
* `W` – Dash downward

#### Rotation 3

* `SPACE` – Jump

* `A` – Shoot

* `D` – Dash left

* `W` – Dash downward

* Press `R` to cycle between rotations.


## 🧭 Objective

* Avoid hitting asteroids or running out of fuel.
* Collect fuel canisters to refill.
* Shoot asteroids to earn points.
* Try to beat the highscore!


## 📁 Assets

All assets should be placed in the following structure:

```
assets/
├── Audio/
│   ├── bgm.mp3
│   └── laser.mp3
├── Fonts/
│   └── Gamer.ttf
├── Images/
│   ├── icon.ico
│   ├── bg.png
│   ├── button.png
│   ├── button1.png
│   ├── fuel.png
│   ├── asteroid.png
│   └── ship/
│       ├── ship-0.png
│       ├── ship-7.png
│       └── ship-8.png
```

Make sure this folder structure exists or update paths in `AsteroSphere.py` accordingly.



## 🔊 Options Menu

* Adjust SFX and BGM volume
* Toggle fullscreen
* View control schemes


## 🙌 Credits

Music and sound effects are made by me
