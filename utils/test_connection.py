#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
test_connection.py - Test NAOqi Connection

DESCRIPTION:
    Simple script to test connection to Pepper and verify the movement
    modules are working correctly.

USAGE:
    # Test connection to Pepper (via SSH on Pepper)
    python test_connection.py --ip 127.0.0.1

    # Test connection from PC
    python test_connection.py --ip <PEPPER_IP>
"""

import sys
import argparse
from modules.base_motion import connect_to_pepper
from modules.walk import WalkController


def test_connection(ip, port):
    """Test connection to Pepper"""
    print("\n" + "="*60)
    print("Testing Connection to Pepper")
    print("="*60)

    # Test 1: Connect to Pepper
    print("\n[Test 1] Connecting to Pepper at {}:{}...".format(ip, port))
    session = connect_to_pepper(ip=ip, port=port)

    if not session:
        print("[FAILED] Could not connect to Pepper")
        return False

    print("[PASSED] Connected successfully!")

    # Test 2: Initialize WalkController
    print("\n[Test 2] Initializing WalkController...")
    try:
        walker = WalkController(session)
        print("[PASSED] WalkController initialized")
    except Exception as e:
        print("[FAILED] Error initializing WalkController:", str(e))
        return False

    # Test 3: Wake up robot
    print("\n[Test 3] Waking up robot...")
    if walker.wake_up():
        print("[PASSED] Robot woken up successfully")
    else:
        print("[FAILED] Could not wake up robot")
        return False

    # Test 4: Get current posture
    print("\n[Test 4] Getting current posture...")
    posture = walker.get_posture()
    if posture:
        print("[PASSED] Current posture:", posture)
    else:
        print("[WARNING] Could not get posture")

    # Test 5: Change posture
    print("\n[Test 5] Changing to StandInit posture...")
    if walker.go_to_posture("StandInit", 1.0):
        print("[PASSED] Posture changed successfully")
    else:
        print("[FAILED] Could not change posture")
        return False

    print("\n" + "="*60)
    print("All tests passed! Movement system is ready.")
    print("="*60)
    print("\nYou can now run:")
    print("  python movement_controller.py --ip {}".format(ip))
    print("\nCleaning up...")

    # Rest the robot
    walker.rest()
    print("Done!")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Test connection to Pepper robot"
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

    try:
        success = test_connection(args.ip, args.port)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted!")
        sys.exit(1)
    except Exception as e:
        print("\nError:", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
