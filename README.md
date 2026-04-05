# Pepper Robot Movement Control

Interactive movement controller and web-based motion UI for **SoftBank Pepper Robot** (NAOqi 2.5).

## Features

- **Interactive CLI** — keyboard-driven terminal controller (WASD-style)
- **Web motion UI** — joystick and arrow button controls via browser
- **Modular motion system** — reusable `WalkController`, `BaseMotion` classes
- **Gesture library** — happy, angry, bow, wave, and 20+ built-in gestures
- **Diagnostic utilities** — movement diagnostics and animation listing

## Quick Start

### Prerequisites

- Pepper Robot with NAOqi 2.5+
- Python 2.7 (NAOqi SDK requirement)
- NAOqi SDK on PYTHONPATH

### Run the CLI controller

```bash
# On Pepper (via SSH)
python core/movement_controller.py --ip 127.0.0.1

# From PC
python core/movement_controller.py --ip <PEPPER_IP>
```

### Test the connection

```bash
python utils/test_connection.py --ip <PEPPER_IP>
```

### List available animations

```bash
python utils/list_animations.py --ip <PEPPER_IP>
python utils/list_animations.py --ip <PEPPER_IP> --by-category
```

### Use the web UI

Serve `frontend/` from a HTTP server and open `motion.html`:

```bash
cd frontend/
python -m SimpleHTTPServer 8080
```

Open `http://<PEPPER_IP>:8080/motion.html`

## CLI Commands

| Command | Shortcut | Description |
|---------|----------|-------------|
| `forward [dist]` | `w` | Move forward (default 0.5 m) |
| `backward [dist]` | `s` | Move backward |
| `left [dist]` | `a` | Strafe left |
| `right [dist]` | `d` | Strafe right |
| `turn_left [°]` | `q` | Turn left |
| `turn_right [°]` | `e` | Turn right |
| `stand` | — | Stand posture |
| `sit` | — | Sit posture |
| `crouch` | — | Crouch |
| `stop` | — | Emergency stop |
| `wake` | — | Enable motors |
| `rest` | — | Disable motors |
| `animations` | — | List available animations |
| `gesture <name>` | — | Run a named gesture |
| `exit` | — | Quit |

## Project Structure

```
pepper-movement/
├── core/
│   ├── movement_controller.py   # Interactive terminal controller
│   └── modules/
│       ├── base_motion.py       # Base class: wake, rest, posture, emergency stop
│       ├── walk.py              # WalkController: forward, backward, strafe, turn
│       └── __init__.py
├── frontend/
│   ├── motion.html              # Web motion control UI
│   ├── js/motion.js             # Joystick + arrow button logic
│   └── css/style.css
├── utils/
│   ├── diagnose_movement.py     # Movement diagnostics
│   ├── list_animations.py       # Discover Pepper's built-in animations
│   └── test_connection.py       # NAOqi connection test
└── requirements.txt
```

## Motion Coordinate System

```
      +X (forward)
         ↑
-Y ←—[Pepper]—→ +Y (left)
         ↓
      -X (backward)

Theta: + counter-clockwise, - clockwise
Units: metres for distance, radians for angle
```

## Related Projects

Part of the Wonderbyte Pepper Project ecosystem:

- [Dance routines](https://github.com/JesseChen543/naoqi-robot-dance)
- [Voice / Realtime API](https://github.com/JesseChen543/pepper-realtime-voice)
- [LED control](https://github.com/JesseChen543/pepper-led-control)
- [Camera + gallery](https://github.com/JesseChen543/pepper-robot-camera)
- [Full dashboard](https://github.com/JesseChen543/pepper-robot-dashboard)
- [YouTube player](https://github.com/JesseChen543/pepper-youtube-player)

## Safety Notes

- Ensure **2 m clear space** around Pepper before movement
- Always supervise during movement commands
- Press the **chest button** for emergency stop
- The controller temporarily adjusts collision protection — re-enabled on exit

## Keywords

`pepper robot` `softbank pepper` `naoqi` `naoqi python` `pepper movement` `robot movement` `motion control` `robot walking` `robot navigation` `humanoid robot` `social robot` `python robotics` `ALMotion` `joystick control` `websocket control`

## License

MIT
