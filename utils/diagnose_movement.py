#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
diagnose_movement.py - Diagnostic tool for Pepper movement issues

Run this to check why Pepper can't move
"""

import qi
import sys
import argparse


def diagnose_movement(ip="127.0.0.1", port=9559):
    """Run comprehensive movement diagnostics"""

    print("\n" + "="*60)
    print("  Pepper Movement Diagnostics")
    print("="*60 + "\n")

    # Connect
    try:
        print("Connecting to Pepper at {}:{}...".format(ip, port))
        session = qi.Session()
        session.connect("tcp://{}:{}".format(ip, port))
        print("Connected!\n")
    except RuntimeError as e:
        print("CONNECTION FAILED:", str(e))
        return

    # Get services
    try:
        motion = session.service("ALMotion")
        memory = session.service("ALMemory")
        autonomous_life = session.service("ALAutonomousLife")
    except Exception as e:
        print("ERROR getting services:", str(e))
        return

    # Check 1: Autonomous Life
    print("[1] Autonomous Life State:")
    try:
        state = autonomous_life.getState()
        print("    State: {}".format(state))
        if state != "disabled":
            print("    *** WARNING: Should be 'disabled' for manual movement ***")
    except Exception as e:
        print("    Error:", str(e))

    # Check 2: Motion state
    print("\n[2] Motion State:")
    try:
        is_awake = motion.robotIsWakeUp()
        print("    Robot is awake: {}".format(is_awake))
        if not is_awake:
            print("    *** WARNING: Robot needs to be woken up ***")
    except Exception as e:
        print("    Error:", str(e))

    # Check 3: Stiffness
    print("\n[3] Stiffness (Motor Power):")
    try:
        body_names = ["LLeg", "RLeg", "LArm", "RArm"]
        for body in body_names:
            stiffness = motion.getStiffnesses(body)
            avg_stiff = sum(stiffness) / len(stiffness) if stiffness else 0
            print("    {}: {:.2f}".format(body, avg_stiff))
            if avg_stiff < 0.5:
                print("       *** WARNING: Low stiffness, motors may be off ***")
    except Exception as e:
        print("    Error:", str(e))

    # Check 4: Collision Protection
    print("\n[4] Collision Protection:")
    try:
        # Check different types
        try:
            arms_collision = motion.getCollisionProtectionEnabled("Arms")
            print("    Arms collision: {}".format(arms_collision))
        except:
            print("    Arms collision: N/A")

        try:
            move_collision = motion.getCollisionProtectionEnabled("Move")
            print("    Move collision: {}".format(move_collision))
            if move_collision:
                print("    *** WARNING: Move collision protection ON - may block movement ***")
        except:
            print("    Move collision: N/A")

        try:
            # External collision is more restrictive
            external = motion.getExternalCollisionProtectionEnabled("All")
            print("    External collision: {}".format(external))
            if external:
                print("    *** WARNING: External collision ON - may block movement ***")
        except:
            print("    External collision: N/A")

    except Exception as e:
        print("    Error:", str(e))

    # Check 5: Move capabilities
    print("\n[5] Move Capabilities:")
    try:
        move_enabled = motion.getMoveArmsEnabled("LArm", "RArm")
        print("    Move arms enabled: {}".format(move_enabled))
    except Exception as e:
        print("    Error:", str(e))

    # Check 6: Tactile/Bumper sensors
    print("\n[6] Tactile Sensors (Bumpers):")
    try:
        # Check if any bumpers are pressed
        bumpers = [
            "FrontTactilTouched",
            "RearTactilTouched",
            "RightBumperPressed",
            "LeftBumperPressed"
        ]
        for bumper in bumpers:
            try:
                value = memory.getData(bumper)
                print("    {}: {}".format(bumper, value))
                if value:
                    print("       *** WARNING: Bumper is pressed - blocks movement! ***")
            except:
                pass
    except Exception as e:
        print("    Error:", str(e))

    # Check 7: Orthogonal security
    print("\n[7] Orthogonal Security Distance:")
    try:
        distance = motion.getOrthogonalSecurityDistance()
        print("    Distance: {} meters".format(distance))
        print("    (Pepper won't move if obstacles within this distance)")
    except Exception as e:
        print("    Error:", str(e))

    # Check 8: Current posture
    print("\n[8] Current Posture:")
    try:
        posture_service = session.service("ALRobotPosture")
        current_posture = posture_service.getPosture()
        print("    Posture: {}".format(current_posture))
        if current_posture not in ["Stand", "StandInit", "StandZero"]:
            print("    *** WARNING: Robot should be in standing posture to move ***")
    except Exception as e:
        print("    Error:", str(e))

    # Check 9: Movement history
    print("\n[9] Movement Status:")
    try:
        is_moving = motion.moveIsActive()
        print("    Currently moving: {}".format(is_moving))
    except Exception as e:
        print("    Error:", str(e))

    # Check 10: Try actual move test
    print("\n[10] Movement Test:")
    print("    Attempting small forward movement (0.1m)...")
    try:
        result = motion.moveTo(0.1, 0.0, 0.0, 5.0)
        if result:
            print("    *** SUCCESS: Movement worked! ***")
        else:
            print("    *** FAILED: moveTo() returned False ***")
            print("    This means NAOqi is blocking the movement")
            print("\n    Possible causes:")
            print("    - Obstacle detected in front")
            print("    - Bumper being pressed")
            print("    - External collision protection")
            print("    - Robot not balanced properly")
    except Exception as e:
        print("    *** ERROR:", str(e))

    # Summary
    print("\n" + "="*60)
    print("DIAGNOSTIC COMPLETE")
    print("="*60)
    print("\nQuick Fixes to Try:")
    print("1. Check for physical obstacles or items touching bumpers")
    print("2. Ensure robot is on flat, stable ground")
    print("3. Run: motion.setExternalCollisionProtectionEnabled('All', False)")
    print("4. Run: autonomous_life.setState('disabled')")
    print("5. Check if someone is holding/touching the robot")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1", help="Pepper IP")
    parser.add_argument("--port", type=int, default=9559, help="NAOqi port")
    args = parser.parse_args()

    diagnose_movement(ip=args.ip, port=args.port)
