# NVIDIA Isaac Sim Setup Example

## Overview

This example demonstrates how to set up a basic simulation environment with NVIDIA Isaac Sim. This will serve as a foundation for more complex humanoid robot simulations using the Isaac Sim platform.

## Prerequisites

Before starting, ensure you have:
- NVIDIA GPU with Compute Capability 6.0 or higher
- CUDA 11.8 or later installed
- Python 3.10 (recommended for Isaac Sim compatibility)
- Isaac Sim installed (see Module 2 for installation instructions)

## Step 1: Verify Isaac Sim Installation

First, verify that Isaac Sim is properly installed:

```python
# Create a test script to verify installation
# test_isaac_sim.py
import omni
from omni.isaac.core import World
from omni.isaac.core.utils.stage import add_reference_to_stage
from omni.isaac.core.utils.nucleus import get_assets_root_path
from omni.isaac.core.utils.prims import get_prim_at_path
import numpy as np

def test_isaac_sim():
    print("Testing Isaac Sim installation...")

    # Create a simple world
    my_world = World(stage_units_in_meters=1.0)

    # Add a simple cube
    my_world.scene.add_default_ground_plane()

    print("Isaac Sim test completed successfully!")

    # Clean up
    my_world.clear()

if __name__ == "__main__":
    test_isaac_sim()
```

Run this script to verify your installation:

```bash
python test_isaac_sim.py
```

## Step 2: Create a Basic Simulation Script

Create a more comprehensive example script called `basic_humanoid_sim.py`:

```python
"""
Basic Humanoid Simulation in Isaac Sim

This script demonstrates how to create a simple simulation environment
with a basic humanoid robot in Isaac Sim.
"""

import numpy as np
import omni
from omni.isaac.core import World
from omni.isaac.core.utils.stage import add_reference_to_stage
from omni.isaac.core.utils.nucleus import get_assets_root_path
from omni.isaac.core.utils.prims import create_prim
from omni.isaac.core.utils.semantics import add_semantic_classification
from omni.isaac.core.objects import VisualCuboid
from omni.isaac.core.prims import RigidPrim, Articulation
from omni.isaac.core.materials import OmniPBR


def create_simple_humanoid():
    """
    Create a simple humanoid robot using basic primitives.
    In a real application, you would load a USD file with a detailed robot model.
    """
    # Create a simple humanoid using basic shapes
    # This is a simplified representation for demonstration purposes

    # Create torso
    create_prim(
        prim_path="/World/Humanoid/torso",
        prim_type="Cylinder",
        position=np.array([0, 0, 0.5]),
        orientation=np.array([0, 0, 0, 1]),
        scale=np.array([0.2, 0.2, 0.3])
    )

    # Create head
    create_prim(
        prim_path="/World/Humanoid/head",
        prim_type="Sphere",
        position=np.array([0, 0, 0.85]),
        orientation=np.array([0, 0, 0, 1]),
        scale=np.array([0.15, 0.15, 0.15])
    )

    # Create left arm
    create_prim(
        prim_path="/World/Humanoid/left_arm",
        prim_type="Cylinder",
        position=np.array([0.25, 0, 0.5]),
        orientation=np.array([0, 0, 0, 1]),
        scale=np.array([0.08, 0.08, 0.3])
    )

    # Create right arm
    create_prim(
        prim_path="/World/Humanoid/right_arm",
        prim_type="Cylinder",
        position=np.array([-0.25, 0, 0.5]),
        orientation=np.array([0, 0, 0, 1]),
        scale=np.array([0.08, 0.08, 0.3])
    )

    # Create left leg
    create_prim(
        prim_path="/World/Humanoid/left_leg",
        prim_type="Cylinder",
        position=np.array([0.1, 0, -0.1]),
        orientation=np.array([0, 0, 0, 1]),
        scale=np.array([0.08, 0.08, 0.4])
    )

    # Create right leg
    create_prim(
        prim_path="/World/Humanoid/right_leg",
        prim_type="Cylinder",
        position=np.array([-0.1, 0, -0.1]),
        orientation=np.array([0, 0, 0, 1]),
        scale=np.array([0.08, 0.08, 0.4])
    )


def main():
    # Create world with 60Hz physics update rate
    my_world = World(stage_units_in_meters=1.0, physics_dt=1.0/60.0, rendering_dt=1.0/30.0)

    print("Setting up Isaac Sim environment...")

    # Add ground plane
    my_world.scene.add_default_ground_plane()

    # Create a simple humanoid robot
    create_simple_humanoid()

    # Add some objects for interaction
    VisualCuboid(
        prim_path="/World/cube_1",
        name="cube_1",
        position=np.array([0.5, 0.5, 0.5]),
        size=0.2,
        color=np.array([0.5, 0.5, 0.5])
    )

    # Reset the world to apply changes
    my_world.reset()

    print("Environment setup complete. Starting simulation...")

    # Run simulation for a number of steps
    for i in range(1000):  # Run for about 16.7 seconds at 60Hz
        # Simple controller - just print progress
        if i % 100 == 0:
            print(f"Simulation step: {i}")

        # Step the world
        my_world.step(render=True)

    print("Simulation completed.")

    # Clean up
    my_world.clear()


if __name__ == "__main__":
    main()
```

## Step 3: Create a More Realistic Robot Example

For a more realistic humanoid robot, you would typically load a USD file. Here's an example using the built-in A1 robot from the NVIDIA assets (if available):

```python
"""
Advanced Humanoid Simulation with NVIDIA Assets

This script demonstrates how to load and control a more complex humanoid robot
using NVIDIA's asset library in Isaac Sim.
"""

import numpy as np
import omni
from omni.isaac.core import World
from omni.isaac.core.utils.stage import add_reference_to_stage
from omni.isaac.core.utils.nucleus import get_assets_root_path
from omni.isaac.core.articulations import ArticulationView
from omni.isaac.core.utils.types import ArticulationAction


def setup_advanced_humanoid_simulation():
    """
    Set up a simulation with a more advanced humanoid robot.
    This example uses NVIDIA's robot assets when available.
    """
    # Create world
    world = World(stage_units_in_meters=1.0, physics_dt=1.0/60.0, rendering_dt=1.0/30.0)

    # Add default ground plane
    world.scene.add_default_ground_plane()

    # Try to get assets root path
    assets_root_path = get_assets_root_path()
    if assets_root_path is None:
        print("Could not find NVIDIA Nucleus server. Using basic robot instead.")

        # Create a simple robot using basic shapes as fallback
        from omni.isaac.core.utils.prims import create_prim

        # Create a simple robot body
        create_prim(
            prim_path="/World/Robot/base_link",
            prim_type="Cylinder",
            position=np.array([0, 0, 0.2]),
            scale=np.array([0.2, 0.2, 0.3])
        )
    else:
        # Use NVIDIA's robot assets if available
        # This is a common quadruped robot, but can be adapted for humanoid
        jetbot_asset_path = assets_root_path + "/Isaac/Robots/Jetbot/jetbot.usd"
        add_reference_to_stage(
            usd_path=jetbot_asset_path,
            prim_path="/World/Robot"
        )

    # Reset the world
    world.reset()

    return world


def run_advanced_simulation():
    """Run the advanced simulation with basic control."""
    world = setup_advanced_humanoid_simulation()

    print("Advanced simulation setup complete.")

    # Run simulation
    for i in range(500):
        if i % 100 == 0:
            print(f"Advanced simulation step: {i}")

        # Step the world
        world.step(render=True)

    print("Advanced simulation completed.")

    # Clean up
    world.clear()


if __name__ == "__main__":
    run_advanced_simulation()
```

## Step 4: Create a Sensor Integration Example

Create an example showing how to integrate sensors in Isaac Sim:

```python
"""
Sensor Integration Example for Isaac Sim

This script demonstrates how to add and use various sensors in Isaac Sim.
"""

import numpy as np
import omni
from omni.isaac.core import World
from omni.isaac.core.utils.stage import add_reference_to_stage
from omni.isaac.core.utils.nucleus import get_assets_root_path
from omni.isaac.core.utils.prims import create_prim
from omni.isaac.sensor import Camera
from omni.isaac.core.objects import VisualCuboid
import carb


def setup_sensor_simulation():
    """Set up a simulation with various sensors."""
    # Create world
    world = World(stage_units_in_meters=1.0, physics_dt=1.0/60.0, rendering_dt=1.0/30.0)

    # Add ground plane
    ground_plane = world.scene.add_default_ground_plane()

    # Create a simple robot body with sensors
    create_prim(
        prim_path="/World/Robot/base_link",
        prim_type="Cylinder",
        position=np.array([0, 0, 0.5]),
        scale=np.array([0.3, 0.3, 0.4])
    )

    # Add a camera sensor
    camera = Camera(
        prim_path="/World/Robot/base_link/Camera",
        position=np.array([0.1, 0, 0.1]),
        orientation=np.array([0, 0, 0, 1])
    )

    # Add some objects for the camera to see
    VisualCuboid(
        prim_path="/World/box_1",
        name="box_1",
        position=np.array([1.0, 0, 0.2]),
        size=0.3,
        color=np.array([1.0, 0, 0])
    )

    # Reset the world
    world.reset()

    # Add camera to the scene
    world.scene.add(camera)

    return world, camera


def run_sensor_simulation():
    """Run the simulation and collect sensor data."""
    world, camera = setup_sensor_simulation()

    print("Sensor simulation setup complete. Collecting data...")

    # Enable camera
    camera.initialize()
    camera.add_render_product()

    # Run simulation and collect sensor data
    for i in range(200):
        if i % 50 == 0:
            print(f"Sensor simulation step: {i}")

        # Step the world
        world.step(render=True)

        # Get camera data every 10 steps
        if i % 10 == 0:
            try:
                # Get RGB image
                rgb_data = camera.get_rgb()
                print(f"Captured RGB image at step {i}, shape: {rgb_data.shape if rgb_data is not None else 'None'}")
            except Exception as e:
                print(f"Error getting camera data: {e}")

    print("Sensor simulation completed.")

    # Clean up
    world.clear()


if __name__ == "__main__":
    run_sensor_simulation()
```

## Step 5: Running the Examples

To run these examples:

1. **Save each script** to your working directory
2. **Activate your Isaac Sim environment**:
   ```bash
   # If using a virtual environment
   source /path/to/isaac_venv/bin/activate
   ```

3. **Run the basic simulation**:
   ```bash
   python basic_humanoid_sim.py
   ```

4. **Run the advanced simulation**:
   ```bash
   python advanced_humanoid_sim.py
   ```

5. **Run the sensor simulation**:
   ```bash
   python sensor_integration_example.py
   ```

## Step 6: Verification Steps

To verify that your Isaac Sim setup is working correctly:

1. **Check Isaac Sim installation**:
   ```bash
   python -c "import omni.isaac.core; print('Isaac Sim imported successfully')"
   ```

2. **Verify GPU acceleration**:
   ```bash
   nvidia-smi
   # Should show Isaac Sim using GPU resources when running
   ```

3. **Test basic functionality**:
   - Run the test script and ensure no errors occur
   - Verify that the simulation window opens
   - Check that physics simulation runs smoothly

4. **Validate sensor data** (if using sensor example):
   - Confirm that sensor data is being collected
   - Verify image shapes and data types match expectations

## Troubleshooting

### Common Issues:

1. **Import errors**:
   - Ensure Isaac Sim is properly installed in your Python environment
   - Check that you're using the correct Python version (3.10 recommended)

2. **GPU issues**:
   - Verify NVIDIA drivers are up to date
   - Check CUDA installation: `nvcc --version`
   - Ensure your GPU has sufficient VRAM

3. **Performance issues**:
   - Reduce rendering resolution
   - Lower physics update rate
   - Simplify scene geometry

4. **Asset loading issues**:
   - Check connection to NVIDIA Nucleus server
   - Verify network connectivity
   - Use local assets as fallback

## Next Steps

This basic setup provides a foundation for more complex humanoid robot simulations in Isaac Sim. You can extend this example by:

- Loading more complex humanoid robot models in USD format
- Implementing advanced control algorithms
- Adding more sophisticated sensors (LiDAR, IMU, etc.)
- Creating complex environments with multiple objects
- Implementing reinforcement learning training scenarios
- Integrating with ROS 2 for hybrid simulation workflows

## References

- [Isaac Sim Documentation](https://docs.omniverse.nvidia.com/isaacsim/latest/index.html)
- [Isaac Sim Python API](https://docs.omniverse.nvidia.com/py/isaacsim/source/extensions/omni.isaac.core/docs/index.html)
- [NVIDIA Omniverse](https://www.nvidia.com/en-us/omniverse/)

This example demonstrates the fundamental setup for Isaac Sim, which is essential for advanced humanoid robot simulation and development with NVIDIA's platform.