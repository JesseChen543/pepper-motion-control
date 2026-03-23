#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
walk.py - Basic Walking and Movement Control for Pepper Robot

DESCRIPTION:
    Provides simple, easy-to-use functions for Pepper's basic locomotion:
    - Forward/backward movement
    - Left/right strafing
    - Rotation (turning)
    - Combined movements

    Based on existing code from ImageFeedbackSocketModule.py and QSP.py,
    extracted into a clean, reusable module.

FEATURES:
    - Simple movement commands with distance/angle parameters
    - Safety timeouts to prevent infinite motion
    - Automatic retry on failed movements
    - Clear feedback and error handling

MOTION COORDINATE SYSTEM:
    - X axis: Forward (+) / Backward (-)
    - Y axis: Left (+) / Right (-)
    - Theta: Counter-clockwise (+) / Clockwise (-)
    - Units: meters for distance, radians for angles

HOW TO USE:
    from modules.walk import WalkController
    from modules.base_motion import connect_to_pepper

    # Connect to Pepper
    session = connect_to_pepper(ip="<PEPPER_IP>")
    walker = WalkController(session)

    # Wake up and stand
    walker.wake_up()
    walker.go_to_posture("Stand")

    # Basic movements
    walker.forward(0.5)      # Move 0.5m forward
    walker.backward(0.3)     # Move 0.3m backward
    walker.strafe_left(0.2)  # Strafe 0.2m left
    walker.strafe_right(0.2) # Strafe 0.2m right
    walker.turn_left(1.57)   # Turn 90 degrees left (π/2 radians)
    walker.turn_right(1.57)  # Turn 90 degrees right

    # Combined movement
    walker.move(0.5, 0.2, 0.0)  # Forward 0.5m, left 0.2m, no rotation

DEPENDENCIES:
    - Python 2.7 (NAOqi SDK)
    - qi, naoqi
    - base_motion.py

NOTES:
    - All movements are blocking (wait for completion)
    - Automatic timeout based on distance/angle
    - Retry logic for failed movements
"""

import math
from base_motion import BaseMotion


class WalkController(BaseMotion):
    """Walking and basic movement controller for Pepper"""

    def __init__(self, session):
        """
        Initialize walk controller

        Args:
            session: qi.Session object connected to Pepper
        """
        super(WalkController, self).__init__(session)
        print("[WalkController] Initialized")

    def move(self, x, y, theta, timeout_multiplier=5.0):
        """
        Move robot in any direction with rotation

        Args:
            x: float - Distance in meters (+ forward, - backward)
            y: float - Distance in meters (+ left, - right)
            theta: float - Rotation in radians (+ counter-clockwise, - clockwise)
            timeout_multiplier: float - Multiplier for timeout calculation

        Returns:
            bool - True if movement successful

        COORDINATE SYSTEM:
            X: Forward(+) / Backward(-)
            Y: Left(+) / Right(-)
            Theta: Counter-clockwise(+) / Clockwise(-)
        """
        # Calculate timeout based on distance
        duration = abs(x) + abs(y) + abs(theta) * 0.4
        timeout = duration * timeout_multiplier

        try:
            print("[WalkController] Moving: x={}, y={}, theta={} (timeout: {}s)".format(
                x, y, theta, timeout))

            # Check if movement is enabled
            try:
                move_enabled = self.motion.getMoveArmsEnabled()
                print("[WalkController] Move arms enabled:", move_enabled)
            except:
                pass

            result = self.motion.moveTo(x, y, theta, timeout)

            if result == False:
                print("[WalkController] Movement failed (returned False), retrying...")
                # Retry once
                result = self.motion.moveTo(x, y, theta, timeout)

            if result:
                print("[WalkController] Movement completed successfully")
                return True
            else:
                print("[WalkController] Movement failed after retry")
                print("[WalkController] Tip: Try 'enable' command first, or check for obstacles")
                return False

        except Exception as e:
            print("[WalkController] Error during movement:", str(e))
            return False

    def forward(self, distance):
        """
        Move forward

        Args:
            distance: float - Distance in meters (positive value)

        Returns:
            bool - True if successful
        """
        return self.move(abs(distance), 0.0, 0.0)

    def backward(self, distance):
        """
        Move backward

        Args:
            distance: float - Distance in meters (positive value)

        Returns:
            bool - True if successful
        """
        return self.move(-abs(distance), 0.0, 0.0)

    def strafe_left(self, distance):
        """
        Strafe left (sideways movement)

        Args:
            distance: float - Distance in meters (positive value)

        Returns:
            bool - True if successful
        """
        return self.move(0.0, abs(distance), 0.0)

    def strafe_right(self, distance):
        """
        Strafe right (sideways movement)

        Args:
            distance: float - Distance in meters (positive value)

        Returns:
            bool - True if successful
        """
        return self.move(0.0, -abs(distance), 0.0)

    def turn_left(self, angle):
        """
        Turn left (counter-clockwise)

        Args:
            angle: float - Angle in radians (positive value)
                          Common: 1.57 rad ≈ 90°, 3.14 rad ≈ 180°

        Returns:
            bool - True if successful
        """
        return self.move(0.0, 0.0, abs(angle))

    def turn_right(self, angle):
        """
        Turn right (clockwise)

        Args:
            angle: float - Angle in radians (positive value)
                          Common: 1.57 rad ≈ 90°, 3.14 rad ≈ 180°

        Returns:
            bool - True if successful
        """
        return self.move(0.0, 0.0, -abs(angle))

    def turn_degrees_left(self, degrees):
        """
        Turn left by degrees (convenience function)

        Args:
            degrees: float - Angle in degrees (positive value)

        Returns:
            bool - True if successful
        """
        radians = math.radians(abs(degrees))
        return self.turn_left(radians)

    def turn_degrees_right(self, degrees):
        """
        Turn right by degrees (convenience function)

        Args:
            degrees: float - Angle in degrees (positive value)

        Returns:
            bool - True if successful
        """
        radians = math.radians(abs(degrees))
        return self.turn_right(radians)

    def circle_left(self, radius, angle):
        """
        Walk in a circle to the left

        Args:
            radius: float - Radius in meters
            angle: float - Arc angle in radians

        Returns:
            bool - True if successful
        """
        # Calculate arc length
        arc_length = radius * angle
        # Move forward while turning
        return self.move(arc_length, 0.0, angle)

    def circle_right(self, radius, angle):
        """
        Walk in a circle to the right

        Args:
            radius: float - Radius in meters
            angle: float - Arc angle in radians

        Returns:
            bool - True if successful
        """
        arc_length = radius * angle
        return self.move(arc_length, 0.0, -angle)

    def stop(self):
        """
        Stop all movement immediately

        Returns:
            bool - True if successful
        """
        return self.emergency_stop()


# Helper functions for quick testing
def degrees_to_radians(degrees):
    """Convert degrees to radians"""
    return math.radians(degrees)


def radians_to_degrees(radians):
    """Convert radians to degrees"""
    return math.degrees(radians)


# Common angles as constants
ANGLE_90_DEG = math.pi / 2   # 1.57 radians
ANGLE_180_DEG = math.pi      # 3.14 radians
ANGLE_270_DEG = 3 * math.pi / 2  # 4.71 radians
ANGLE_360_DEG = 2 * math.pi  # 6.28 radians
ANGLE_45_DEG = math.pi / 4   # 0.785 radians


if __name__ == "__main__":
    # Simple test when run directly
    import sys
    from base_motion import connect_to_pepper

    # Check for IP argument
    ip = "127.0.0.1"
    if len(sys.argv) > 1:
        ip = sys.argv[1]

    print("Connecting to Pepper at", ip)
    session = connect_to_pepper(ip=ip)

    if session:
        walker = WalkController(session)
        walker.wake_up()
        walker.go_to_posture("Stand", 1.0)

        print("\nWalk Controller Test")
        print("Commands:")
        print("  forward 0.5")
        print("  backward 0.3")
        print("  left 0.2")
        print("  right 0.2")
        print("  turn_left 90")
        print("  turn_right 45")
        print("  stop")
        print("  exit")

        while True:
            try:
                cmd = raw_input("\nCommand: ").strip().lower()

                if cmd == "exit":
                    break
                elif cmd == "stop":
                    walker.stop()
                elif cmd.startswith("forward"):
                    dist = float(cmd.split()[1]) if len(cmd.split()) > 1 else 0.5
                    walker.forward(dist)
                elif cmd.startswith("backward"):
                    dist = float(cmd.split()[1]) if len(cmd.split()) > 1 else 0.5
                    walker.backward(dist)
                elif cmd.startswith("left"):
                    dist = float(cmd.split()[1]) if len(cmd.split()) > 1 else 0.2
                    walker.strafe_left(dist)
                elif cmd.startswith("right"):
                    dist = float(cmd.split()[1]) if len(cmd.split()) > 1 else 0.2
                    walker.strafe_right(dist)
                elif cmd.startswith("turn_left"):
                    angle = float(cmd.split()[1]) if len(cmd.split()) > 1 else 90
                    walker.turn_degrees_left(angle)
                elif cmd.startswith("turn_right"):
                    angle = float(cmd.split()[1]) if len(cmd.split()) > 1 else 90
                    walker.turn_degrees_right(angle)
                else:
                    print("Unknown command:", cmd)

            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print("Error:", str(e))

        walker.rest()
        print("Done!")
