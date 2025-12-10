"""
Conceptual Example 1: Simple Robot Perception-Action Loop

This example demonstrates the fundamental perception-action loop that is
central to embodied AI and physical AI systems. The loop consists of:
1. Sensing the environment
2. Processing the sensory information
3. Making a decision based on the processed information
4. Acting in the environment
5. Repeating the cycle

This is a simplified simulation that illustrates these concepts.
"""

import time
import random
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class SensorData:
    """Represents sensor data from the robot's environment."""
    proximity_sensors: List[float]  # Distance readings from proximity sensors (0.0 to 1.0)
    light_sensors: List[float]      # Light intensity readings (0.0 to 1.0)
    sound_direction: float          # Direction of loudest sound (-1.0 to 1.0, left to right)


@dataclass
class Action:
    """Represents an action the robot can take."""
    forward_speed: float           # Forward/backward speed (-1.0 to 1.0)
    turn_direction: float          # Turning direction (-1.0 to 1.0, left to right)
    arm_position: float            # Arm position (0.0 to 1.0)


class SimpleRobot:
    """A simple robot that demonstrates the perception-action loop."""

    def __init__(self, name: str):
        self.name = name
        self.position = [0.0, 0.0]  # x, y coordinates
        self.orientation = 0.0      # Facing direction in radians
        self.battery_level = 100.0  # Battery percentage

    def sense(self) -> SensorData:
        """Simulate sensing the environment."""
        # Simulate proximity sensors (front, left, right)
        proximity = [
            random.uniform(0.2, 0.8),  # Front
            random.uniform(0.1, 0.9),  # Left
            random.uniform(0.1, 0.9)   # Right
        ]

        # Simulate light sensors (left, center, right)
        light = [
            random.uniform(0.0, 1.0),  # Left
            random.uniform(0.0, 1.0),  # Center
            random.uniform(0.0, 1.0)   # Right
        ]

        # Simulate sound direction
        sound_direction = random.uniform(-1.0, 1.0)

        return SensorData(
            proximity_sensors=proximity,
            light_sensors=light,
            sound_direction=sound_direction
        )

    def process_sensory_data(self, sensor_data: SensorData) -> Action:
        """Process sensory data and decide on an action."""
        # Simple behavior: Move toward light, avoid obstacles
        front_proximity = sensor_data.proximity_sensors[0]
        left_light = sensor_data.light_sensors[0]
        center_light = sensor_data.light_sensors[1]
        right_light = sensor_data.light_sensors[2]

        # Avoid obstacles if too close
        if front_proximity < 0.3:
            # Turn away from obstacle
            turn_direction = random.choice([-0.5, 0.5])
            forward_speed = -0.3  # Move backward slightly
        else:
            # Move toward brighter light
            if center_light > max(left_light, right_light):
                # Light is ahead, move forward
                forward_speed = 0.5
                turn_direction = 0.0
            elif left_light > right_light:
                # Light is to the left
                forward_speed = 0.3
                turn_direction = -0.3
            else:
                # Light is to the right
                forward_speed = 0.3
                turn_direction = 0.3

        # Simple arm movement based on sound
        arm_position = abs(sensor_data.sound_direction) * 0.5 + 0.25

        return Action(
            forward_speed=forward_speed,
            turn_direction=turn_direction,
            arm_position=arm_position
        )

    def act(self, action: Action):
        """Execute the action in the environment."""
        # Update position based on action
        self.position[0] += action.forward_speed * 0.1
        self.position[1] += action.turn_direction * 0.05

        # Update orientation
        self.orientation += action.turn_direction * 0.05

        # Consume battery
        self.battery_level -= 0.1

        # Print current state
        print(f"{self.name}: Pos=({self.position[0]:.2f}, {self.position[1]:.2f}), "
              f"Orient={self.orientation:.2f}, Battery={self.battery_level:.1f}%")

    def perception_action_loop(self, iterations: int = 10):
        """Run the perception-action loop for a number of iterations."""
        print(f"Starting perception-action loop for {self.name}")

        for i in range(iterations):
            print(f"\n--- Iteration {i+1} ---")

            # Sense the environment
            sensor_data = self.sense()
            print(f"Sensor data: Proximity={sensor_data.proximity_sensors}, "
                  f"Light={sensor_data.light_sensors}, SoundDir={sensor_data.sound_direction:.2f}")

            # Process sensory data and decide on action
            action = self.process_sensory_data(sensor_data)
            print(f"Action: Forward={action.forward_speed:.2f}, "
                  f"Turn={action.turn_direction:.2f}, Arm={action.arm_position:.2f}")

            # Execute the action
            self.act(action)

            # Brief pause to simulate real-time operation
            time.sleep(0.1)

            # Stop if battery is low
            if self.battery_level <= 10.0:
                print(f"{self.name}: Battery low, stopping.")
                break


def main():
    """Main function to demonstrate the perception-action loop."""
    print("Physical AI Conceptual Example 1: Perception-Action Loop")
    print("=" * 55)

    # Create a simple robot
    robot = SimpleRobot("EmbodiedAI_Robot")

    # Run the perception-action loop
    robot.perception_action_loop(iterations=15)

    print(f"\nFinal state: Position={robot.position}, Orientation={robot.orientation:.2f}")


if __name__ == "__main__":
    main()