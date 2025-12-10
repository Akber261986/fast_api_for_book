# Gazebo Simulation Environment

## Overview

Gazebo is a powerful open-source 3D robotics simulator that provides realistic physics simulation, high-quality graphics, and convenient interfaces for creating and testing robot designs. This module covers the setup and usage of Gazebo for humanoid robotics simulation.

## What is Gazebo?

Gazebo is a 3D dynamic simulator with the ability to:
- Accurately and efficiently simulate populations of robots in complex indoor and outdoor environments
- Provide realistic rendering of environments using OGRE (Object-Oriented Graphics Rendering Engine)
- Simulate various sensors including cameras, LiDAR, IMU, and more
- Integrate with ROS/ROS 2 for robot control and data exchange
- Support for multiple physics engines (ODE, Bullet, Simbody)

## Key Features

### Physics Simulation
- **Realistic physics**: Accurate simulation of rigid body dynamics
- **Contact simulation**: Realistic contact forces and friction
- **Multi-body dynamics**: Support for complex articulated robots
- **Fluid simulation**: Basic fluid dynamics for underwater robots

### Sensor Simulation
- **Camera sensors**: RGB, depth, and stereo cameras
- **Range sensors**: LiDAR, sonar, and infrared sensors
- **Inertial sensors**: IMU and accelerometer simulation
- **Force/torque sensors**: Joint force and torque measurements
- **GPS simulation**: Global positioning system simulation

### Rendering and Visualization
- **High-quality graphics**: Realistic rendering using OGRE
- **Multiple viewports**: Different camera angles and perspectives
- **Dynamic lighting**: Realistic lighting effects
- **Texture mapping**: Detailed surface textures

## Installing Gazebo

### System Requirements
- **Operating System**: Ubuntu 20.04 or 22.04 (recommended)
- **Graphics**: OpenGL 2.1+ compatible GPU
- **RAM**: Minimum 4GB, 8GB+ recommended
- **Disk Space**: At least 2GB for basic installation

### Installation Steps

#### 1. Update package list
```bash
sudo apt update
```

#### 2. Install Gazebo Garden (recommended version for ROS 2 Humble)
```bash
sudo apt install gazebo
```

#### 3. Install Gazebo ROS packages
```bash
sudo apt install ros-humble-gazebo-ros-pkgs ros-humble-gazebo-plugins ros-humble-gazebo-dev
```

#### 4. Install additional tools
```bash
sudo apt install ros-humble-joint-state-publisher-gui ros-humble-robot-state-publisher
```

### Verification
```bash
gazebo --version
# Should show Gazebo version information
```

## Gazebo World Format

### World Files
Gazebo uses SDF (Simulation Description Format) to define simulation environments:

```xml
<?xml version="1.0" ?>
<sdf version="1.7">
  <world name="default">
    <!-- Include a model from the model database -->
    <include>
      <uri>model://ground_plane</uri>
    </include>

    <!-- Lighting -->
    <include>
      <uri>model://sun</uri>
    </include>

    <!-- Custom robot -->
    <model name="my_robot">
      <pose>0 0 0.5 0 0 0</pose>
      <link name="chassis">
        <collision name="collision">
          <geometry>
            <box>
              <size>1.0 0.5 0.2</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>1.0 0.5 0.2</size>
            </box>
          </geometry>
        </visual>
      </link>
    </model>
  </world>
</sdf>
```

## Robot Description in URDF

For humanoid robots, Gazebo uses URDF (Unified Robot Description Format) with Gazebo-specific extensions:

```xml
<?xml version="1.0"?>
<robot name="humanoid_robot" xmlns:xacro="http://www.ros.org/wiki/xacro">
  <!-- Base link -->
  <link name="base_link">
    <visual>
      <geometry>
        <cylinder length="0.2" radius="0.1"/>
      </geometry>
    </visual>
    <collision>
      <geometry>
        <cylinder length="0.2" radius="0.1"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0.1" ixy="0.0" ixz="0.0" iyy="0.1" iyz="0.0" izz="0.1"/>
    </inertial>
  </link>

  <!-- Gazebo material -->
  <gazebo reference="base_link">
    <material>Gazebo/Blue</material>
  </gazebo>

  <!-- Joint between base and torso -->
  <joint name="base_to_torso" type="fixed">
    <parent link="base_link"/>
    <child link="torso"/>
    <origin xyz="0 0 0.1" rpy="0 0 0"/>
  </joint>

  <link name="torso">
    <visual>
      <geometry>
        <box size="0.3 0.2 0.5"/>
      </geometry>
    </visual>
    <collision>
      <geometry>
        <box size="0.3 0.2 0.5"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="2.0"/>
      <inertia ixx="0.2" ixy="0.0" ixz="0.0" iyy="0.2" iyz="0.0" izz="0.2"/>
    </inertial>
  </link>
</robot>
```

## Gazebo ROS Integration

### ROS 2 Control Interface
Gazebo integrates with ROS 2 through the ros_gz bridge:

```bash
# Launch a robot in Gazebo
ros2 launch my_robot_gazebo my_robot_world.launch.py

# Check available topics
ros2 topic list | grep -E "(joint|cmd|imu)"
```

### Common Topics
- `/joint_states`: Current joint positions, velocities, and efforts
- `/cmd_vel`: Velocity commands for mobile robots
- `/camera/image_raw`: Camera image data
- `/imu`: Inertial measurement unit data
- `/tf`: Transform data between coordinate frames

## Physics Configuration

### Physics Engines
Gazebo supports multiple physics engines:

- **ODE (Open Dynamics Engine)**: Default, good balance of speed and accuracy
- **Bullet**: Faster simulation, good for real-time applications
- **Simbody**: More accurate for complex articulated systems

### Quality of Service Settings
In simulation files, you can configure physics parameters:

```xml
<physics type="ode">
  <max_step_size>0.001</max_step_size>  <!-- Simulation time step -->
  <real_time_factor>1.0</real_time_factor>  <!-- Real-time vs simulation speed -->
  <real_time_update_rate>1000.0</real_time_update_rate>  <!-- Hz -->
  <gravity>0 0 -9.8</gravity>  <!-- Gravity vector -->
</physics>
```

## Simulation Best Practices

### 1. Model Complexity
- Start with simplified models for faster simulation
- Add detail gradually as needed
- Balance visual fidelity with simulation performance

### 2. Physics Parameters
- Tune damping and friction coefficients for realistic behavior
- Use appropriate mass and inertia values
- Consider the impact of time step on stability

### 3. Sensor Configuration
- Configure sensor noise parameters to match real sensors
- Set appropriate update rates for different sensors
- Consider field of view and range limitations

## Troubleshooting Common Issues

### Performance Issues
```bash
# Reduce visual complexity
gz sim -r --minimal_gui world_name.sdf

# Lower physics update rate in world file
<max_step_size>0.01</max_step_size>
```

### Physics Instability
- Increase solver iterations
- Reduce time step size
- Check mass and inertia values
- Verify joint limits and stiffness

### ROS Communication Issues
```bash
# Check bridge status
ros2 run ros_gz_bridge parameter_bridge --ros-args --log-level info

# Verify topic connections
ros2 topic info /joint_states
```

## Example: Launching a Humanoid Robot in Gazebo

Here's a complete example of launching a humanoid robot in Gazebo with ROS 2:

### 1. Create launch file (`launch/humanoid_gazebo.launch.py`)

```python
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    ld = LaunchDescription()

    # Launch Gazebo with a world file
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('gazebo_ros'),
                'launch',
                'gazebo.launch.py'
            ])
        ]),
        launch_arguments={
            'world': PathJoinSubstitution([
                FindPackageShare('my_humanoid_description'),
                'worlds',
                'simple_room.sdf'
            ])
        }.items()
    )

    ld.add_action(gazebo)

    # Spawn robot in Gazebo
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'humanoid_robot',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.5'
        ],
        output='screen'
    )

    ld.add_action(spawn_entity)

    return ld
```

### 2. Robot state publisher
```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            parameters=[
                {'use_sim_time': True},
                {'robot_description': open('path/to/robot.urdf').read()}
            ]
        )
    ])
```

## Practical Exercise: ROS 2 + Gazebo Movement Example

Let's look at a practical example that demonstrates robot movement in Gazebo using ROS 2. This example is available in the examples directory as `basic_movement_ros2_gazebo.py`:

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import math
import time


class BasicMovementController(Node):
    """
    A simple controller that makes a robot move in a square pattern in Gazebo.
    """

    def __init__(self):
        super().__init__('basic_movement_controller')

        # Create publisher for velocity commands
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Create subscriber for odometry (to track robot position)
        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        # Initialize variables to track robot state
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_yaw = 0.0  # Robot's orientation

        # Movement parameters
        self.linear_speed = 0.5  # m/s
        self.angular_speed = 0.5  # rad/s
        self.side_length = 1.0  # Length of each side of the square (meters)

        # Movement state
        self.movement_state = 0  # 0-7: 4 sides + 4 turns
        self.state_start_time = self.get_clock().now()
        self.state_duration = 0.0

        # Create a timer for the control loop
        self.timer = self.create_timer(0.1, self.control_loop)

        self.get_logger().info('Basic Movement Controller initialized')

    def odom_callback(self, msg):
        """
        Callback function to update robot's position and orientation.
        """
        # Extract position
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y

        # Extract orientation (convert quaternion to yaw)
        orientation = msg.pose.pose.orientation
        self.current_yaw = math.atan2(
            2.0 * (orientation.w * orientation.z + orientation.x * orientation.y),
            1.0 - 2.0 * (orientation.y * orientation.y + orientation.z * orientation.z)
        )

    def control_loop(self):
        """
        Main control loop that determines the robot's movement based on state.
        """
        msg = Twist()

        # Calculate elapsed time in current state
        current_time = self.get_clock().now()
        elapsed_time = (current_time - self.state_start_time).nanoseconds / 1e9

        if self.movement_state < 8:  # Only move for 8 states (square pattern)
            if self.movement_state % 2 == 0:  # Moving forward
                # Move forward for the length of a side
                msg.linear.x = self.linear_speed
                msg.angular.z = 0.0

                # Check if we've moved enough distance
                expected_duration = self.side_length / self.linear_speed
                if elapsed_time >= expected_duration:
                    self.movement_state += 1
                    self.state_start_time = current_time
                    self.get_logger().info(f'Turning: State {self.movement_state}')

            else:  # Turning
                # Turn 90 degrees
                msg.linear.x = 0.0
                msg.angular.z = self.angular_speed

                # Check if we've turned 90 degrees (pi/2 radians)
                expected_duration = (math.pi / 2) / self.angular_speed
                if elapsed_time >= expected_duration:
                    self.movement_state += 1
                    self.state_start_time = current_time
                    self.get_logger().info(f'Moving forward: State {self.movement_state}')

        else:  # Stop after completing the square
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            self.get_logger().info('Movement completed. Robot stopped.')
            self.timer.cancel()  # Stop the timer

        # Publish the velocity command
        self.cmd_vel_pub.publish(msg)

        # Log current state
        self.get_logger().info(
            f'State: {self.movement_state}, '
            f'Position: ({self.current_x:.2f}, {self.current_y:.2f}), '
            f'Yaw: {math.degrees(self.current_yaw):.2f}°'
        )


def main(args=None):
    """
    Main function to run the basic movement controller.
    """
    rclpy.init(args=args)

    # Create the controller node
    controller = BasicMovementController()

    try:
        # Spin the node to process callbacks
        rclpy.spin(controller)
    except KeyboardInterrupt:
        controller.get_logger().info('Interrupted by user')
    finally:
        # Clean up
        controller.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Verification Steps

To verify your Gazebo and ROS 2 integration:

1. **Installation Verification**:
   ```bash
   # Check Gazebo installation
   gazebo --version

   # Check ROS 2 installation
   ros2 topic list
   ```

2. **Basic Launch Test**:
   - Create a simple URDF robot model
   - Launch Gazebo with the robot
   - Verify the robot appears in the simulation

3. **Control Verification**:
   - Launch the movement example
   - Verify the robot moves as expected
   - Check that odometry data is published correctly

4. **Communication Check**:
   ```bash
   # Verify ROS 2 topics are active
   ros2 topic list | grep -E "(joint|cmd|odom)"
   ```

5. **Performance Verification**:
   - Monitor simulation real-time factor (should be close to 1.0)
   - Check CPU and memory usage
   - Verify sensor data rates match expectations

## Advanced Features

### Plugins
Gazebo supports various plugins for extended functionality:
- **Controller plugins**: For robot control
- **Sensor plugins**: For custom sensor simulation
- **Model plugins**: For custom model behavior
- **World plugins**: For world-specific behavior

### Integration with ROS 2 Control
For advanced control, integrate with ros2_control:

```xml
<gazebo>
  <plugin name="gazebo_ros2_control" filename="libgazebo_ros2_control.so">
    <parameters>$(find-pkg-share my_robot_control)/config/my_robot_controllers.yaml</parameters>
  </plugin>
</gazebo>
```

## References

- [Gazebo Documentation](http://gazebosim.org/) - Official Gazebo documentation
- [Gazebo Tutorials](http://gazebosim.org/tutorials) - Step-by-step tutorials
- [ROS 2 Gazebo Integration](https://github.com/gazebosim/ros_gz) - ROS 2 and Gazebo bridge
- [Gazebo GitHub](https://github.com/gazebosim/gazebo) - Source code repository

## References

- [Gazebo Documentation](http://gazebosim.org/) - Official Gazebo documentation (verified: official source)
- [Gazebo Tutorials](http://gazebosim.org/tutorials) - Step-by-step tutorials (verified: official source)
- [ROS 2 Gazebo Integration](https://github.com/gazebosim/ros_gz) - ROS 2 and Gazebo bridge (verified: official GitHub repository)
- [Open Robotics](https://www.openrobotics.org/) - Organization behind Gazebo (verified: official organization)

## Additional Resources

- [Gazebo Community](https://community.gazebosim.org/) - Community forum
- [Gazebo Q&A](https://answers.gazebosim.org/) - Question and answer site
- [Open Robotics](https://www.openrobotics.org/) - Organization behind Gazebo