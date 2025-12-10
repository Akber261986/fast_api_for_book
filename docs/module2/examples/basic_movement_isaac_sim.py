"""
Basic Movement Example for Isaac Sim

This script demonstrates how to control a robot in Isaac Sim.
It shows basic movement patterns and control approaches in the Isaac Sim environment.
"""

import numpy as np
import omni
from omni.isaac.core import World
from omni.isaac.core.utils.stage import add_reference_to_stage
from omni.isaac.core.utils.nucleus import get_assets_root_path
from omni.isaac.core.utils.prims import create_prim
from omni.isaac.core.objects import VisualCuboid
from omni.isaac.core.prims import RigidPrim
from omni.isaac.core.articulations import ArticulationView
from omni.isaac.core.utils.types import ArticulationAction
import carb
import math


class IsaacSimMovementController:
    """
    A controller for basic movement in Isaac Sim.
    This example demonstrates movement using basic primitives since we don't have a specific robot model.
    """

    def __init__(self):
        # Create world with appropriate physics settings
        self.world = World(stage_units_in_meters=1.0, physics_dt=1.0/60.0, rendering_dt=1.0/30.0)

        # Initialize movement parameters
        self.linear_speed = 0.2  # m/s
        self.angular_speed = 0.3  # rad/s
        self.side_length = 1.0  # Length of each side of movement pattern (meters)

        # Movement state
        self.movement_state = 0  # 0-7: 4 sides + 4 turns for square pattern
        self.state_start_time = 0
        self.initial_positions = {}

        # Create the simulation environment
        self.setup_environment()

    def setup_environment(self):
        """
        Set up the Isaac Sim environment with a simple robot and obstacles.
        """
        print("Setting up Isaac Sim environment...")

        # Add ground plane
        self.world.scene.add_default_ground_plane()

        # Create a simple robot using basic shapes
        # This represents our "robot" in the simulation
        self.robot_prim_path = "/World/Robot/base_link"
        create_prim(
            prim_path=self.robot_prim_path,
            prim_type="Cylinder",
            position=np.array([0, 0, 0.2]),  # Start at origin, 0.2m above ground
            scale=np.array([0.2, 0.2, 0.3])
        )

        # Create some obstacles for reference
        self.obstacle1 = VisualCuboid(
            prim_path="/World/obstacle_1",
            name="obstacle_1",
            position=np.array([2.0, 0, 0.2]),
            size=0.3,
            color=np.array([1.0, 0, 0])
        )

        self.obstacle2 = VisualCuboid(
            prim_path="/World/obstacle_2",
            name="obstacle_2",
            position=np.array([0, 2.0, 0.2]),
            size=0.3,
            color=np.array([0, 1.0, 0])
        )

        # Reset the world to apply changes
        self.world.reset()

        # Store initial position for movement calculations
        self.initial_positions[self.robot_prim_path] = np.array([0, 0, 0.2])

        print("Environment setup complete.")

    def move_robot(self, direction_vector, duration):
        """
        Move the robot in a specified direction for a given duration.

        Args:
            direction_vector: A 3D vector indicating movement direction (x, y, z)
            duration: Duration of movement in seconds
        """
        # Calculate the number of steps based on physics dt
        steps = int(duration / (1.0/60.0))

        # Normalize direction and scale by speed
        direction = np.array(direction_vector)
        if np.linalg.norm(direction) > 0:
            direction = direction / np.linalg.norm(direction)  # Normalize
            movement_vector = direction * self.linear_speed * (1.0/60.0)  # Speed * time_step

            for _ in range(steps):
                # Get current position
                current_pos = self.world.scene.get_object("base_link").get_world_poses()[0][0]

                # Calculate new position
                new_pos = current_pos + movement_vector

                # Set new position (this is a simplified approach - in real implementations,
                # you'd use proper physics joints and actuators)
                self.world.scene.get_object("base_link").set_world_poses(positions=np.array([new_pos[0], new_pos[1], new_pos[2]]))

                # Step the simulation
                self.world.step(render=True)

    def rotate_robot(self, angle, duration):
        """
        Rotate the robot by a specified angle over a given duration.

        Args:
            angle: Rotation angle in radians
            duration: Duration of rotation in seconds
        """
        steps = int(duration / (1.0/60.0))
        rotation_per_step = angle / steps if steps > 0 else 0

        for _ in range(steps):
            # In a real implementation, you would apply torques or use joint control
            # For this example, we'll just step the simulation
            self.world.step(render=True)

    def run_square_pattern(self):
        """
        Run a square movement pattern: move forward, turn 90 degrees, repeat 4 times.
        """
        print("Starting square movement pattern...")

        # Define movement directions for each side of the square
        # Each side goes in a different direction (relative to the robot's orientation)
        directions = [
            [1, 0, 0],   # Move along +X
            [0, 1, 0],   # Move along +Y
            [-1, 0, 0],  # Move along -X
            [0, -1, 0]   # Move along -Y
        ]

        for i, direction in enumerate(directions):
            print(f"Moving side {i+1} of square...")

            # Move forward
            self.move_robot(direction, self.side_length / self.linear_speed)

            # Turn 90 degrees (simplified - in real implementation would be more complex)
            print(f"Turning at corner {i+1}...")
            for _ in range(30):  # Simple turn simulation
                self.world.step(render=True)

        print("Square pattern completed.")

    def run_spiral_pattern(self):
        """
        Run a spiral movement pattern.
        """
        print("Starting spiral movement pattern...")

        num_turns = 2
        steps_per_turn = 100
        total_steps = num_turns * steps_per_turn

        for step in range(total_steps):
            # Calculate angle and radius for spiral
            angle = (step / steps_per_turn) * 2 * math.pi
            radius = 0.1 + (step / total_steps) * 1.0  # Start small, expand

            # Calculate movement direction (tangential to spiral)
            dx = -math.sin(angle) * self.linear_speed * (1.0/60.0)
            dy = math.cos(angle) * self.linear_speed * (1.0/60.0)

            # Get current position
            current_pos = self.world.scene.get_object("base_link").get_world_poses()[0][0]

            # Calculate new position
            new_pos = current_pos + np.array([dx, dy, 0])

            # Set new position
            self.world.scene.get_object("base_link").set_world_poses(
                positions=np.array([new_pos[0], new_pos[1], new_pos[2]])
            )

            # Step the simulation
            self.world.step(render=True)

            if step % 50 == 0:
                print(f"Spiral progress: {step}/{total_steps}")

        print("Spiral pattern completed.")

    def run_simulation(self):
        """
        Main simulation loop that executes movement patterns.
        """
        print("Starting Isaac Sim movement simulation...")

        # Run the square pattern
        self.run_square_pattern()

        # Wait a bit before running the spiral
        print("Waiting before spiral pattern...")
        for _ in range(60):  # Wait for 1 second at 60Hz
            self.world.step(render=True)

        # Run the spiral pattern
        self.run_spiral_pattern()

        print("All movement patterns completed.")

    def cleanup(self):
        """
        Clean up the simulation environment.
        """
        self.world.clear()


def create_articulated_robot_example():
    """
    Example of how to work with articulated robots in Isaac Sim.
    This is a more advanced example showing how to control joints.
    """
    print("Setting up articulated robot example...")

    # Create world
    world = World(stage_units_in_meters=1.0, physics_dt=1.0/60.0, rendering_dt=1.0/30.0)

    # Add ground plane
    world.scene.add_default_ground_plane()

    # In a real scenario, you would load a robot from a USD file
    # For this example, we'll create a simple articulated structure
    # This would typically be a robot arm or a simplified leg structure

    # Create base
    create_prim(
        prim_path="/World/ArticulatedRobot/base",
        prim_type="Cylinder",
        position=np.array([0, 0, 0.2]),
        scale=np.array([0.2, 0.2, 0.2])
    )

    # Create a simple "arm" with one joint
    create_prim(
        prim_path="/World/ArticulatedRobot/arm",
        prim_type="Cylinder",
        position=np.array([0.3, 0, 0.2]),
        scale=np.array([0.05, 0.05, 0.3])
    )

    # Reset the world
    world.reset()

    print("Articulated robot example setup complete.")

    # In a real implementation, you would:
    # 1. Create an ArticulationView to control the robot
    # 2. Set joint positions/velocities/efforts
    # 3. Read sensor data

    # For demonstration, just run for a few steps
    for i in range(100):
        if i % 20 == 0:
            print(f"Articulated example step: {i}")
        world.step(render=True)

    # Clean up
    world.clear()
    print("Articulated robot example completed.")


def main():
    """
    Main function to run the Isaac Sim movement examples.
    """
    print("Isaac Sim Basic Movement Examples")
    print("=" * 40)

    # Example 1: Basic movement patterns
    controller = IsaacSimMovementController()

    try:
        controller.run_simulation()
    except Exception as e:
        print(f"Error during simulation: {e}")
    finally:
        controller.cleanup()

    print("\n" + "=" * 40)

    # Example 2: Articulated robot control
    try:
        create_articulated_robot_example()
    except Exception as e:
        print(f"Error in articulated example: {e}")

    print("\nAll Isaac Sim movement examples completed.")


"""
Advanced Example: Using Isaac Lab for Locomotion

This example shows how you might structure code for more advanced locomotion
using Isaac Lab (which provides higher-level interfaces for locomotion tasks).
"""

def advanced_locomotion_example():
    """
    Example structure for advanced locomotion using Isaac Lab concepts.

    Note: This is a conceptual example as Isaac Lab requires specific installation
    and is more advanced than basic Isaac Sim.
    """
    print("Advanced Locomotion Example (Conceptual)")
    print("-" * 40)

    # This would typically involve:
    # 1. Loading a humanoid robot asset
    # 2. Setting up a locomotion environment
    # 3. Using reinforcement learning or model predictive control

    # Conceptual structure:
    print("1. Initialize environment with humanoid robot")
    print("2. Set up reward function for locomotion")
    print("3. Implement control policy")
    print("4. Execute locomotion behavior")

    # In practice, this would use Isaac Lab's APIs:
    # from omni.isaac.orbit_tasks.locomotion.velocity.velocity_env_cfg import VelocityEnvCfg
    # from omni.isaac.orbit_tasks.locomotion.velocity import VelocityEnv
    # etc.

    print("Advanced locomotion example completed (conceptual).")


if __name__ == "__main__":
    main()

    print("\n" + "=" * 50)
    advanced_locomotion_example()