#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
movement_controller.py - Terminal-Based Movement Controller for Pepper Robot

DESCRIPTION:
    Interactive terminal application for controlling Pepper's movements.
    Provides a simple command-line interface to test and use the modular
    movement system.

FEATURES:
    - Interactive command-line interface
    - Forward, backward, strafe, and rotation commands
    - Quick shortcuts (WASD-style controls)
    - Help system
    - Safe connection handling
    - Posture management

HOW TO RUN ON PEPPER (via SSH):
    1. SSH to Pepper:
       ssh nao@<PEPPER_IP>

    2. Navigate to the movement directory:
       cd ~/pepper_movement

    3. Run the controller:
       python movement_controller.py --ip 127.0.0.1

HOW TO RUN FROM PC (controlling remote Pepper):
    python movement_controller.py --ip <PEPPER_IP>

COMMANDS:
    Movement:
        forward [distance]      - Move forward (default: 0.5m)
        backward [distance]     - Move backward (default: 0.5m)
        left [distance]         - Strafe left (default: 0.2m)
        right [distance]        - Strafe right (default: 0.2m)
        turn_left [degrees]     - Turn left (default: 90°)
        turn_right [degrees]    - Turn right (default: 90°)

    Shortcuts:
        w [dist]    - Same as forward
        s [dist]    - Same as backward
        a [dist]    - Same as left
        d [dist]    - Same as right
        q [deg]     - Same as turn_left
        e [deg]     - Same as turn_right

    Posture:
        stand       - Stand up (StandInit posture)
        sit         - Sit down
        crouch      - Crouch position
        standzero   - Stand with arms down

    Control:
        stop        - Emergency stop
        wake        - Wake up motors
        rest        - Rest (disable motors)
        help        - Show this help
        exit        - Quit controller

USAGE EXAMPLES:
    Command: forward 1.0
    Command: w 0.5
    Command: turn_left 45
    Command: q 90
    Command: stand
    Command: exit

DEPENDENCIES:
    - Python 2.7 (NAOqi SDK)
    - qi
    - modules/base_motion.py
    - modules/walk.py

NOTES:
    - Runs on Python 2.7 (NAOqi environment)
    - Can run ON Pepper or FROM PC
    - Use --ip 127.0.0.1 when running ON Pepper
    - Use --ip <PEPPER_IP> when running FROM PC
"""

import sys
import argparse
import random
from modules.base_motion import connect_to_pepper
from modules.walk import WalkController
from animations import build_animation_catalog


class MovementController(object):
    """Terminal-based movement controller for Pepper"""

    def __init__(self, session):
        """
        Initialize movement controller

        Args:
            session: qi.Session connected to Pepper
        """
        self.walker = WalkController(session)
        self.session = session
        try:
            self.animation_player = session.service("ALAnimationPlayer")
        except Exception:
            self.animation_player = None
            print("[MovementController] Warning: ALAnimationPlayer service unavailable")
        try:
            self.behavior_manager = session.service("ALBehaviorManager")
        except Exception:
            self.behavior_manager = None
            print("[MovementController] Warning: ALBehaviorManager service unavailable")
        try:
            self.tts = session.service("ALTextToSpeech")
        except Exception:
            self.tts = None
            print("[MovementController] Warning: ALTextToSpeech service unavailable")
        self._animation_catalog = None
        self._animation_catalog_depth = None
        self._animation_catalog_source = None
        self._animation_catalog_errors = None
        self._animation_lookup = None
        self._animation_full_set = None
        self._last_action_meta = None
        self.gesture_map = {
            "angry": [
                ("random_path", [
                    "animations/Stand/Emotions/Negative/Angry_1",
                    "animations/Stand/Emotions/Negative/Angry_2",
                    "animations/Stand/Emotions/Negative/Angry_3",
                    "animations/Stand/Emotions/Negative/Angry_4"
                ])
            ],
            "surprise": [
                ("random_path", [
                    "animations/Stand/Emotions/Negative/Surprise_1",
                    "animations/Stand/Emotions/Negative/Surprise_2",
                    "animations/Stand/Emotions/Negative/Surprise_3"
                ])
            ],
            "ask_attention": [
                ("path", "animations/Stand/Emotions/Neutral/AskForAttention_2")
            ],
            "sneeze": [
                ("path", "animations/Stand/Emotions/Neutral/Sneeze"),
                ("speech", "Ah-choo!")
            ],
            "amused": [
                ("path", "animations/Stand/Emotions/Positive/Amused_1")
            ],
            "happy": [
                ("random_path", [
                    "animations/Stand/Emotions/Positive/Happy_1",
                    "animations/Stand/Emotions/Positive/Happy_2",
                    "animations/Stand/Emotions/Positive/Happy_3",
                    "animations/Stand/Emotions/Positive/Happy_4"
                ])
            ],
            "interested": [
                ("path", "animations/Stand/Emotions/Positive/Interested_2")
            ],
            "laugh": [
                ("random_path", [
                    "animations/Stand/Emotions/Positive/Laugh_1",
                    "animations/Stand/Emotions/Positive/Laugh_2",
                    "animations/Stand/Emotions/Positive/Laugh_3"
                ])
            ],
            "mocker": [
                ("path", "animations/Stand/Emotions/Positive/Mocker_1")
            ],
            "winner": [
                ("random_path", [
                    "animations/Stand/Emotions/Positive/Winner_1",
                    "animations/Stand/Emotions/Positive/Winner_2"
                ]),
                ("speech", "We did it!")
            ],
            "angry_gesture": [
                ("random_path", [
                    "animations/Stand/Gestures/Angry_1",
                    "animations/Stand/Gestures/Angry_2",
                    "animations/Stand/Gestures/Angry_3"
                ])
            ],
            "bow": [
                ("random_path", [
                    "animations/Stand/Gestures/BowShort_1",
                    "animations/Stand/Gestures/BowShort_2",
                    "animations/Stand/Gestures/BowShort_3"
                ])
            ],
            "hey": [
                ("random_path", [
                    "animations/Stand/Gestures/Hey_1",
                    "animations/Stand/Gestures/Hey_2",
                    "animations/Stand/Gestures/Hey_3",
                    "animations/Stand/Gestures/Hey_4",
                    "animations/Stand/Gestures/Hey_6",
                    "animations/Stand/Gestures/Hey_7",
                    "animations/Stand/Gestures/Hey_8",
                    "animations/Stand/Gestures/Hey_9",
                    "animations/Stand/Gestures/Hey_10"
                ])
            ],
            "salute": [
                ("path", "animations/Stand/Gestures/Salute_1")
            ],
            "hide": [
                ("path", "animations/Stand/Gestures/Hide_1")
            ],
            "hot": [
                ("path", "animations/Stand/Gestures/Hot_2")
            ],
            "joy": [
                ("path", "animations/Stand/Gestures/Joy_1")
            ],
            "kisses": [
                ("path", "animations/Stand/Gestures/Kisses_1"),
                ("speech", "Sending kisses!")
            ],
            "shy": [
                ("path", "animations/Stand/Emotions/Positive/Shy_1")
            ],
            "stretch": [
                ("random_path", [
                    "animations/Stand/Gestures/Stretch_1",
                    "animations/Stand/Gestures/Stretch_2"
                ])
            ],
            "whisper": [
                ("path", "animations/Stand/Gestures/Whisper_1"),
                ("speech", "I'll keep it quiet.")
            ],
            "shake": [
                ("path", "animations/Stand/Reactions/ShakeBody_1")
            ],
            "touch_head": [
                ("path", "animations/Stand/Reactions/TouchHead_1")
            ],
            "air_guitar": [
                ("path", "animations/Stand/Waiting/AirGuitar_1"),
                ("speech", "Rock on!")
            ],
            "scratch": [
                ("random_path", [
                    "animations/Stand/Waiting/ScratchBack_1",
                    "animations/Stand/Waiting/ScratchBottom_1",
                    "animations/Stand/Waiting/ScratchEye_1",
                    "animations/Stand/Waiting/ScratchHand_1",
                    "animations/Stand/Waiting/ScratchHead_1",
                    "animations/Stand/Waiting/ScratchLeg_1"
                ]),
                ("speech", "Ah, my back is itchy!")
            ],
            "call_someone": [
                ("path", "animations/Stand/Waiting/CallSomeone_1"),
                ("speech", "Let me give someone a call.")
            ],
            "bandmaster": [
                ("path", "animations/Stand/Waiting/Bandmaster_1"),
                ("speech", "Let's play some music!")
            ],
            "drink": [
                ("path", "animations/Stand/Waiting/Drink_1"),
                ("speech", "Cheers!")
            ],
            "drive_car": [
                ("path", "animations/Stand/Waiting/DriveCar_1")
            ],
            "funny_dancer": [
                ("path", "animations/Stand/Waiting/FunnyDancer_1"),
                ("speech", "Check out this move!")
            ],
            "helicopter": [
                ("path", "animations/Stand/Waiting/Helicopter_1")
            ],
            "knock_eye": [
                ("path", "animations/Stand/Waiting/KnockEye_1")
            ],
            "hug": [
                ("path", "animations/Stand/Waiting/LoveYou_1"),
                ("speech", "Sending you a hug!")
            ],
            "monster": [
                ("path", "animations/Stand/Waiting/Monster_1")
            ],
            "mystical": [
                ("path", "animations/Stand/Waiting/MysticalPower_1")
            ],
            "relaxation": [
                ("random_path", [
                    "animations/Stand/Waiting/Relaxation_1",
                    "animations/Stand/Waiting/Relaxation_2",
                    "animations/Stand/Waiting/Relaxation_3",
                    "animations/Stand/Waiting/Relaxation_4"
                ]),
                ("speech", "Relax with me.")
            ],
            "robot": [
                ("path", "animations/Stand/Waiting/Robot_1")
            ],
            "show_muscles": [
                ("random_path", [
                    "animations/Stand/Waiting/ShowMuscles_1",
                    "animations/Stand/Waiting/ShowMuscles_2",
                    "animations/Stand/Waiting/ShowMuscles_3",
                    "animations/Stand/Waiting/ShowMuscles_4",
                    "animations/Stand/Waiting/ShowMuscles_5"
                ]),
                ("speech", "Look at these muscles!")
            ],
            "flying": [
                ("path", "animations/Stand/Waiting/SpaceShuttle_1"),
                ("speech", "Preparing for take-off!")
            ],
            "take_picture": [
                ("path", "animations/Stand/Waiting/TakePicture_1"),
                ("speech", "Say cheese!")
            ],
            "taxi": [
                ("path", "animations/Stand/Waiting/Taxi_1"),
                ("speech", "Taxi is on the way!")
            ],
            "wake_up": [
                ("path", "animations/Stand/Waiting/WakeUp_1"),
                ("speech", "Time to wake up!")
            ],
            "zombie": [
                ("path", "animations/Stand/Waiting/Zombie_1")
            ],
            "sad": [
                ("path", "animations/Stand/Emotions/Negative/Sad_1")
            ],
        }
        self.running = False

    def show_welcome(self):
        """Display welcome message"""
        print("\n" + "="*60)
        print("  Pepper Movement Controller v1.0")
        print("="*60)
        print("\nType 'help' for commands, 'exit' to quit\n")

    def show_help(self, topic=None):
        """Display contextual help information."""
        sections = self._help_section_data()
        section_map = {key: data for key, data in sections}

        if topic:
            key = topic.strip().lower()
            data = section_map.get(key)
            if not data:
                print("Unknown help topic '{}'. Available categories: {}".format(
                    key,
                    ", ".join(section_map.keys())
                ))
                return
            self._print_help_section(data["title"], data["entries"], data.get("notes"))
            return

        print("\nHelp Categories:")
        for key, data in sections:
            print("  {:<12} - {}".format(key, data["summary"]))
        print("\nType 'help <category>' for details (e.g., 'help gestures').")

    def _help_section_data(self):
        """Return ordered help section metadata."""
        gesture_hint = (
            "Run 'gestures' to list configured names. "
            "Use 'gesture <name> [<speech>]' for actions like angry, surprise, hey, hug, happy, laugh, scratch, take_picture, and more."
        )

        return [
            ("movement", {
                "title": "Movement Commands",
                "summary": "Move Pepper forward/backward, strafe, and rotate.",
                "entries": [
                    "forward [dist] | w [dist]    -> Move forward (default 0.5m)",
                    "backward [dist] | s [dist]   -> Move backward (default 0.5m)",
                    "left [dist] | a [dist]       -> Strafe left (default 0.2m)",
                    "right [dist] | d [dist]      -> Strafe right (default 0.2m)",
                    "turn_left [deg] | q [deg]    -> Rotate left (default 90 deg)",
                    "turn_right [deg] | e [deg]   -> Rotate right (default 90 deg)",
                ],
                "notes": "Distances are in meters; degrees specify rotation."
            }),
            ("posture", {
                "title": "Posture Commands",
                "summary": "Switch between standard postures.",
                "entries": [
                    "stand       -> StandInit posture",
                    "sit         -> Sit posture",
                    "crouch      -> Crouch posture",
                    "standzero   -> StandZero posture",
                ],
            }),
            ("gestures", {
                "title": "Gesture Commands",
                "summary": "Trigger predefined gesture bundles.",
                "entries": [
                    "gestures                          -> Show configured gesture names",
                    "gesture <name> [<speech>]         -> Run gesture; optional speech in <>",
                    "<gesture alias> [<speech>]        -> Run by alias (angry, hey, hug, etc.)",
                    "gesture hey<Hello everyone>       -> Example combining motion + speech",
                ],
                "notes": gesture_hint
            }),
            ("animations", {
                "title": "Animation Catalog & Tags",
                "summary": "Browse and run animation paths or tags.",
                "entries": [
                    "animations [depth|refresh]        -> Show cached catalog (default depth 3)",
                    "animations 2                      -> Rebuild catalog limited to two folders",
                    "animate <package/path>            -> Run NAOqi animation path",
                    "tag <name>                        -> Run animation tag via ALAnimationPlayer",
                    "<animation_name>                  -> Type the filename (e.g., fitness_1) to auto-run",
                    "python list_animations.py [...]   -> CLI utility with --by-category option",
                ],
                "notes": (
                    "Catalog is sourced from ALAnimationPlayer or ALBehaviorManager "
                    "if list APIs are unavailable."
                )
            }),
            ("control", {
                "title": "Control & Status",
                "summary": "Power, safety, and lifecycle operations.",
                "entries": [
                    "stop        -> Emergency stop movement",
                    "wake        -> Wake up robot motors",
                    "rest        -> Rest (motors off)",
                    "disable     -> Disable autonomous life",
                    "enable      -> Enable movement (disables collision protection)",
                    "status      -> Show movement status report",
                    "exit | quit -> Exit controller",
                ],
            }),
            ("speech", {
                "title": "Speech & Interaction",
                "summary": "Speak text and pair it with motions.",
                "entries": [
                    "speak <text> | say <text>         -> Speak text using ALTextToSpeech",
                    "gesture <name><text>              -> Gesture while speaking inline text",
                ],
                "notes": "Combine with gesture aliases or tags for richer interactions."
            }),
        ]

    def _print_help_section(self, title, entries, notes=None):
        """Pretty-print a help section."""
        print("\n{}".format(title))
        print("-" * len(title))
        for line in entries:
            print("  {}".format(line))
        if notes:
            print("\n{}".format(notes))
        print("")

    def parse_command(self, cmd_string):
        """
        Parse command string into command and argument

        Args:
            cmd_string: str - Raw command string from user

        Returns:
            tuple - (command, argument) or (command, None)
        """
        parts = cmd_string.strip().split()
        if not parts:
            return None, None

        command = parts[0].lower()
        argument = " ".join(parts[1:]) if len(parts) > 1 else None

        return command, argument

    def load_animation_catalog(self, depth=None, refresh=False):
        """Fetch and cache Pepper's animation catalog."""
        if not self.animation_player:
            print("Animation service unavailable; cannot load catalog.")
            return None

        if depth is None:
            depth = 3

        if (not refresh and
                self._animation_catalog is not None and
                self._animation_catalog_depth == depth):
            return self._animation_catalog

        try:
            catalog, fetch_result = build_animation_catalog(
                self.session,
                depth=depth,
                player=self.animation_player
            )
        except RuntimeError as err:
            print("Failed to build animation catalog: {}".format(err))
            return None

        self._animation_catalog = catalog
        self._animation_catalog_depth = depth
        self._animation_catalog_source = fetch_result.source
        self._animation_catalog_errors = fetch_result.errors or []
        lookup = {}
        for items in catalog.values():
            for path in items:
                slug = path.split("/")[-1].lower()
                lookup.setdefault(slug, set()).add(path)
        self._animation_lookup = lookup
        self._animation_full_set = set(p.lower() for p in fetch_result.animations)

        if (fetch_result.source != "ALAnimationPlayer" and
                fetch_result.errors):
            print("Note: catalog built via {} because ALAnimationPlayer list "
                  "methods are unavailable.".format(fetch_result.source))

        return catalog

    def show_animation_catalog(self, depth=None, refresh=False):
        """Display a summary of the categorized animation catalog."""
        catalog = self.load_animation_catalog(depth=depth, refresh=refresh)
        if not catalog:
            return

        source = self._animation_catalog_source or "Unknown"
        depth = self._animation_catalog_depth
        print("\nAnimation Catalog ({} categories, source: {}, depth: {})".format(
            len(catalog),
            source,
            depth
        ))

        for category, items in catalog.items():
            print("  - {} ({} animations)".format(category, len(items)))
            preview = ", ".join(items[:3])
            if len(items) > 3:
                preview += ", ..."
            print("      {}".format(preview))

        if self._animation_catalog_errors:
            print("\nCatalog diagnostics:")
            for entry in self._animation_catalog_errors:
                for line in entry.splitlines():
                    print("  {}".format(line))

    def get_animation_catalog_data(self, depth=None, refresh=False):
        """
        Return the categorized animation catalog as a list of dictionaries.

        Useful for UI layers that need structured data instead of console
        output.
        """
        catalog = self.load_animation_catalog(depth=depth, refresh=refresh)
        if catalog is None:
            return None

        data = []
        for category, items in catalog.items():
            data.append({
                "category": category,
                "count": len(items),
                "animations": list(items)
            })
        return data

    def handle_animations_command(self, argument):
        """
        Parse and execute the 'animations' command.

        Usage:
            animations              -> show catalog with cached depth (default 3)
            animations 2            -> rebuild catalog limited to depth 2
            animations refresh      -> refresh the current catalog depth
        """
        depth = None
        refresh = False

        if argument:
            token = argument.strip().lower()
            if token == "refresh":
                refresh = True
            else:
                try:
                    depth = int(token)
                except ValueError:
                    print("Usage: animations [depth|refresh]")
                    return

        self.show_animation_catalog(depth=depth, refresh=refresh)

    def try_run_animation_alias(self, command, argument):
        """
        Attempt to treat an unknown command as an animation shortcut.

        Returns True if an animation was executed.
        """
        token = (command or "").strip()
        if not token:
            return False

        # If the user supplied a full path, run it directly.
        if "/" in token:
            path_candidate = token
            if argument:
                path_candidate = "{} {}".format(path_candidate, argument)
            success = self._try_run_animation_path(path_candidate)
            if success:
                print("Animation '{}' finished.".format(
                    self._normalize_animation_path(path_candidate)
                ))
            return success

        # Ensure catalog is loaded for lookup.
        catalog = self.load_animation_catalog()
        if catalog is None or not self._animation_lookup:
            return False

        lookup_key = token.lower()
        matches = self._animation_lookup.get(lookup_key)
        if not matches:
            return False

        if len(matches) > 1:
            print("Multiple animations match '{}':".format(token))
            for path in sorted(matches):
                print("  - {}".format(path))
            print("Use 'animate <path>' to specify the exact animation.")
            return True

        path = next(iter(matches))
        if self._try_run_animation_path(path):
            print("Animation '{}' finished.".format(path))
        return True

    def execute_command(self, command, argument):
        """
        Execute a movement command

        Args:
            command: str - Command name
            argument: str - Command argument (distance/angle)

        Returns:
            bool - True to continue, False to exit
        """
        # Exit commands
        if command in ["exit", "quit"]:
            return False

        # Help
        elif command == "help":
            self.show_help(argument)

        # Stop
        elif command == "stop":
            self.walker.stop()

        # Wake/Rest
        elif command == "wake":
            self.walker.wake_up()

        elif command == "rest":
            self.walker.rest()

        # Disable autonomous life
        elif command == "disable":
            self.walker.disable_autonomous_life()

        # Enable movement
        elif command == "enable":
            self.walker.enable_movement()

        # Check status
        elif command == "status":
            self.walker.check_move_enabled()

        # Postures
        elif command == "stand":
            self.walker.go_to_posture("StandInit", 1.0)

        elif command == "sit":
            self.walker.go_to_posture("Sit", 1.0)

        elif command == "crouch":
            self.walker.go_to_posture("Crouch", 1.0)

        elif command == "standzero":
            self.walker.go_to_posture("StandZero", 1.0)

        # Forward movement
        elif command in ["forward", "w"]:
            distance = float(argument) if argument else 0.5
            self.walker.forward(distance)

        # Backward movement
        elif command in ["backward", "s"]:
            distance = float(argument) if argument else 0.5
            self.walker.backward(distance)

        # Left strafe
        elif command in ["left", "a"]:
            distance = float(argument) if argument else 0.2
            self.walker.strafe_left(distance)

        # Right strafe
        elif command in ["right", "d"]:
            distance = float(argument) if argument else 0.2
            self.walker.strafe_right(distance)

        # Turn left
        elif command in ["turn_left", "q"]:
            degrees = float(argument) if argument else 90.0
            self.walker.turn_degrees_left(degrees)

        # Turn right
        elif command in ["turn_right", "e"]:
            degrees = float(argument) if argument else 90.0
            self.walker.turn_degrees_right(degrees)

        elif command == "gestures":
            self.list_gestures()

        elif command == "gesture":
            if not argument:
                print("Usage: gesture <name> [<speech>]")
                self.list_gestures()
            else:
                name, message = self._parse_gesture_args(argument)
                if not name:
                    print("Usage: gesture <name> [<speech>]")
                    self.list_gestures()
                else:
                    self.run_gesture(name, message)

        elif command in self.gesture_map:
            name, message = self._parse_gesture_args("{} {}".format(command, argument or "").strip())
            self.run_gesture(name or command, message)

        elif command == "animate":
            if not argument:
                print("Usage: animate <package/path>")
            else:
                self.run_animation_path(argument)

        elif command == "animations":
            self.handle_animations_command(argument)

        elif command == "tag":
            if not argument:
                print("Usage: tag <tag_name>")
            else:
                self.run_animation_tag(argument)

        elif command in ["speak", "say"]:
            if not argument:
                print("Usage: speak <text>")
            elif not self.tts:
                print("Text-to-speech service unavailable")
            else:
                self.tts.say(argument)

        else:
            if self.try_run_animation_alias(command, argument):
                return True
            print("Unknown command: '{}'. Type 'help' for available commands.".format(command))

        return True

    def list_gestures(self):
        """List available gesture names."""
        names = sorted(self.gesture_map.keys())
        if not names:
            print("No gestures configured.")
        else:
            print("\nAvailable gestures:")
            print("  " + ", ".join(names) + "\n")

    def _parse_gesture_args(self, raw_text):
        """Split a gesture string into name and optional speech message."""
        if not raw_text:
            return None, None
        text = raw_text.strip()
        if not text:
            return None, None
        if "<" in text:
            before, _, rest = text.partition("<")
            name = before.strip().lower()
            message = rest.rstrip(">").strip()
            return name if name else None, (message if message else None)
        parts = text.split()
        name = parts[0].lower()
        message = " ".join(parts[1:]).strip() if len(parts) > 1 else None
        return name, (message if message else None)

    def run_gesture(self, name, message=None):
        """Execute a gesture by name."""
        if not name:
            return False, {"error": "missing name"}
        key = name.lower()
        entry = self.gesture_map.get(key)
        if not entry:
            print("Unknown gesture '{}'. Type 'gestures' to list options.".format(key))
            return False, {"error": "unknown gesture", "name": key}

        success = False
        failure_notes = []
        default_message = None
        chosen_path = None

        for kind, value in entry:
            if kind == "posture":
                if self.walker.go_to_posture(value, 0.8):
                    success = True
                    chosen_path = value
                    break
                continue

            if kind == "speech":
                default_message = value
                continue

            if kind == "path":
                if self._try_run_animation_path(value, quiet=True):
                    success = True
                    chosen_path = value
                    break
                failure_notes.append("path '{}'".format(value))
                continue

            if kind == "random_path":
                if not value:
                    failure_notes.append("random path list empty")
                    continue
                candidate = random.choice(value)
                if self._try_run_animation_path(candidate, quiet=True):
                    success = True
                    chosen_path = candidate
                    break
                failure_notes.append("path '{}'".format(candidate))
                continue

            if kind == "tag":
                if not self.animation_player:
                    failure_notes.append("tag '{}' (animation player unavailable)".format(value))
                    continue
                try:
                    self.animation_player.runTag(value)
                    success = True
                    chosen_path = value
                    break
                except Exception as exc:
                    failure_notes.append("tag '{}': {}".format(value, exc))
                    continue

        if success:
            print("Gesture '{}' executed.".format(key))
            spoken = message if message is not None else default_message
            if spoken:
                if self.tts:
                    self.tts.say(spoken)
                else:
                    print("TTS unavailable; message not spoken: {}".format(spoken))
            meta = {"name": key}
            if chosen_path:
                meta["path"] = chosen_path
            if spoken:
                meta["speech"] = spoken
            self._last_action_meta = meta
            return True, meta

        if failure_notes:
            print("Unable to run gesture '{}':\n  {}".format(
                key,
                "\n  ".join(failure_notes)
            ))
            meta = {"error": "execution_failed", "details": failure_notes, "name": key}
        else:
            print("Unable to run gesture '{}'. Try 'animate <path>'.".format(key))
            meta = {"error": "execution_failed", "name": key}
        self._last_action_meta = None
        return False, meta

    def stop_current_action(self):
        """Attempt to stop the current running animation/behavior."""
        stopped = False
        notes = []

        if self.animation_player:
            try:
                self.animation_player.stopAll()
                stopped = True
            except Exception as exc:
                notes.append("ALAnimationPlayer.stopAll: {}".format(exc))

        if self.behavior_manager:
            try:
                if hasattr(self.behavior_manager, "stopAllBehaviors"):
                    self.behavior_manager.stopAllBehaviors()
                    stopped = True
            except Exception as exc:
                notes.append("ALBehaviorManager.stopAllBehaviors: {}".format(exc))

        if self.walker:
            try:
                if self.walker.stop():
                    stopped = True
            except Exception as exc:
                notes.append("WalkController.stop: {}".format(exc))

        if stopped:
            meta = {"stopped": True}
            if self._last_action_meta:
                meta["previous"] = self._last_action_meta
            self._last_action_meta = None
            print("Current action stopped.")
            return True, meta

        meta = {"error": "unable_to_stop"}
        if notes:
            meta["details"] = notes
        print("No running action to stop or stop failed.")
        return False, meta

    def run_animation_path(self, path):
        """Run an animation path directly."""
        normalized = self._normalize_animation_path(path)
        if self._try_run_animation_path(normalized):
            print("Animation '{}' finished.".format(normalized))

    def run_animation_tag(self, tag):
        """Run an animation tag directly."""
        if not self.animation_player:
            print("Animation service unavailable")
            return
        try:
            self.animation_player.runTag(tag)
            print("Tag '{}' finished.".format(tag))
        except Exception as exc:
            print("Failed to run tag '{}': {}".format(tag, exc))

    def _normalize_animation_path(self, path):
        """Ensure animation paths include the 'animations/' prefix."""
        if not path:
            return ""
        normalized = path.strip()
        if not normalized.startswith("animations/"):
            normalized = "animations/" + normalized.lstrip("/")
        return normalized

    def _try_run_animation_path(self, path, quiet=False):
        """Attempt to run an animation path via available services."""
        normalized = self._normalize_animation_path(path)
        if not normalized:
            if not quiet:
                print("No animation path provided.")
            return False

        errors = []

        if self.animation_player:
            try:
                self.animation_player.run(normalized)
                return True
            except Exception as exc:
                errors.append("ALAnimationPlayer: {}".format(exc))

        if self.behavior_manager:
            try:
                if hasattr(self.behavior_manager, "isBehaviorInstalled"):
                    if not self.behavior_manager.isBehaviorInstalled(normalized):
                        raise RuntimeError("Behavior '{}' not installed".format(normalized))
                self.behavior_manager.runBehavior(normalized)
                return True
            except Exception as exc:
                errors.append("ALBehaviorManager: {}".format(exc))

        if not quiet:
            if errors:
                print("Failed to run animation '{}':\n  {}".format(
                    normalized,
                    "\n  ".join(errors)
                ))
            else:
                print("No animation services available to run '{}'.".format(normalized))
        return False

    def run(self):
        """Run the interactive controller"""
        self.show_welcome()
        self.running = True

        # Initialize: wake up and stand
        print("Initializing robot...")
        self.walker.wake_up()
        print("Disabling autonomous life...")
        self.walker.disable_autonomous_life()
        print("Enabling movement (disabling collision protection)...")
        self.walker.enable_movement()
        print("Moving to standing posture...")
        self.walker.go_to_posture("StandInit", 1.0)
        print("Ready!\n")

        while self.running:
            try:
                # Get command from user
                cmd_string = raw_input("Command: ")

                # Parse and execute
                command, argument = self.parse_command(cmd_string)

                if command:
                    self.running = self.execute_command(command, argument)

            except KeyboardInterrupt:
                print("\n\nInterrupted! Type 'exit' to quit safely.")
                continue

            except ValueError as e:
                print("Invalid argument:", str(e))
                continue

            except Exception as e:
                print("Error:", str(e))
                continue

        # Cleanup
        print("\nShutting down...")
        self.walker.rest()
        print("Goodbye!")


def main():
    """Main entry point"""
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Terminal-based movement controller for Pepper Robot"
    )
    parser.add_argument(
        "--ip",
        type=str,
        default="127.0.0.1",
        help="Pepper's IP address (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=9559,
        help="NAOqi port (default: 9559)"
    )

    args = parser.parse_args()

    # Connect to Pepper
    print("Connecting to Pepper at {}:{}...".format(args.ip, args.port))
    session = connect_to_pepper(ip=args.ip, port=args.port)

    if not session:
        print("\nFailed to connect to Pepper!")
        print("Make sure:")
        print("  1. Pepper is powered on")
        print("  2. You're on the same network")
        print("  3. The IP address is correct")
        print("  4. NAOqi is running on port", args.port)
        sys.exit(1)

    # Run controller
    try:
        controller = MovementController(session)
        controller.run()
    except Exception as e:
        print("\nError running controller:", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
