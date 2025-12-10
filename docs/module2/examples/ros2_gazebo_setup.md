# ROS 2 + Gazebo Setup Example

## Overview

This example demonstrates how to set up a basic simulation environment with ROS 2 and Gazebo for a simple robot. This will serve as a foundation for more complex humanoid robot simulations.

## Prerequisites

Before starting, ensure you have:
- ROS 2 Humble Hawksbill installed
- Gazebo Garden installed
- Basic understanding of ROS 2 concepts (nodes, topics, packages)

## Step 1: Create a ROS 2 Package

First, let's create a ROS 2 package for our simulation:

```bash
# Navigate to your ROS 2 workspace
cd ~/ros2_ws/src

# Create the package
ros2 pkg create --build-type ament_python my_robot_simulation --dependencies rclpy std_msgs sensor_msgs geometry_msgs

# Create necessary directories
mkdir -p ~/ros2_ws/src/my_robot_simulation/launch
mkdir -p ~/ros2_ws/src/my_robot_simulation/config
mkdir -p ~/ros2_ws/src/my_robot_simulation/worlds
```

## Step 2: Create Robot URDF

Create a simple robot description in URDF format. Create the file `~/ros2_ws/src/my_robot_simulation/urdf/my_robot.urdf`:

```xml
<?xml version="1.0"?>
<robot name="my_robot" xmlns:xacro="http://www.ros.org/wiki/xacro">
  <!-- Base Link -->
  <link name="base_link">
    <visual>
      <geometry>
        <cylinder length="0.2" radius="0.2"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 1 0.8"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder length="0.2" radius="0.2"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0.1" ixy="0.0" ixz="0.0" iyy="0.1" iyz="0.0" izz="0.1"/>
    </inertial>
  </link>

  <!-- Gazebo Material -->
  <gazebo reference="base_link">
    <material>Gazebo/Blue</material>
  </gazebo>

  <!-- Wheel Links -->
  <link name="wheel_left">
    <visual>
      <geometry>
        <cylinder length="0.05" radius="0.1"/>
      </geometry>
      <material name="black">
        <color rgba="0 0 0 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder length="0.05" radius="0.1"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.2"/>
      <inertia ixx="0.001" ixy="0.0" ixz="0.0" iyy="0.001" iyz="0.0" izz="0.001"/>
    </inertial>
  </link>

  <link name="wheel_right">
    <visual>
      <geometry>
        <cylinder length="0.05" radius="0.1"/>
      </geometry>
      <material name="black">
        <color rgba="0 0 0 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder length="0.05" radius="0.1"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.2"/>
      <inertia ixx="0.001" ixy="0.0" ixz="0.0" iyy="0.001" iyz="0.0" izz="0.001"/>
    </inertial>
  </link>

  <!-- Joints -->
  <joint name="wheel_left_joint" type="continuous">
    <parent link="base_link"/>
    <child link="wheel_left"/>
    <origin xyz="0 0.15 -0.05" rpy="1.57075 0 0"/>
    <axis xyz="0 0 1"/>
  </joint>

  <joint name="wheel_right_joint" type="continuous">
    <parent link="base_link"/>
    <child link="wheel_right"/>
    <origin xyz="0 -0.15 -0.05" rpy="1.57075 0 0"/>
    <axis xyz="0 0 1"/>
  </joint>

  <!-- Gazebo Plugins -->
  <gazebo>
    <plugin name="diff_drive" filename="libgazebo_ros_diff_drive.so">
      <left_joint>wheel_left_joint</left_joint>
      <right_joint>wheel_right_joint</right_joint>
      <wheel_separation>0.3</wheel_separation>
      <wheel_diameter>0.2</wheel_diameter>
      <max_wheel_torque>20</max_wheel_torque>
      <max_wheel_acceleration>1.0</max_wheel_acceleration>
      <command_topic>cmd_vel</command_topic>
      <publish_odom>true</publish_odom>
      <publish_odom_tf>true</publish_odom_tf>
      <publish_wheel_tf>true</publish_wheel_tf>
      <odometry_frame>odom</odometry_frame>
      <robot_base_frame>base_link</robot_base_frame>
    </plugin>
  </gazebo>
</robot>
```

## Step 3: Create a Simple World File

Create a basic world file at `~/ros2_ws/src/my_robot_simulation/worlds/simple_room.sdf`:

```xml
<?xml version="1.0" ?>
<sdf version="1.7">
  <world name="simple_room">
    <!-- Include ground plane -->
    <include>
      <uri>model://ground_plane</uri>
    </include>

    <!-- Include sun -->
    <include>
      <uri>model://sun</uri>
    </include>

    <!-- Add a simple room -->
    <model name="room">
      <static>true</static>
      <!-- Walls will be added as links -->
      <link name="wall_1">
        <pose>0 5 1 0 0 0</pose>
        <visual name="visual">
          <geometry>
            <box>
              <size>10 0.2 2</size>
            </box>
          </geometry>
          <material>
            <ambient>0.8 0.8 0.8 1</ambient>
            <diffuse>0.8 0.8 0.8 1</diffuse>
          </material>
        </visual>
        <collision name="collision">
          <geometry>
            <box>
              <size>10 0.2 2</size>
            </box>
          </geometry>
        </collision>
      </link>

      <link name="wall_2">
        <pose>5 0 1 0 0 1.5707</pose>
        <visual name="visual">
          <geometry>
            <box>
              <size>10 0.2 2</size>
            </box>
          </geometry>
          <material>
            <ambient>0.8 0.8 0.8 1</ambient>
            <diffuse>0.8 0.8 0.8 1</diffuse>
          </material>
        </visual>
        <collision name="collision">
          <geometry>
            <box>
              <size>10 0.2 2</size>
            </box>
          </geometry>
        </collision>
      </link>
    </model>
  </world>
</sdf>
```

## Step 4: Create Launch File

Create a launch file at `~/ros2_ws/src/my_robot_simulation/launch/robot_simulation.launch.py`:

```python
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution, TextSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # Arguments
    use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )

    # Launch Gazebo
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
                FindPackageShare('my_robot_simulation'),
                'worlds',
                'simple_room.sdf'
            ]),
            'verbose': 'false'
        }.items()
    )

    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'robot_description': open(
                PathJoinSubstitution([
                    FindPackageShare('my_robot_simulation'),
                    'urdf',
                    'my_robot.urdf'
                ]).perform(None)
            ).read()
        }]
    )

    # Spawn robot in Gazebo
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'my_robot',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.1'
        ],
        output='screen'
    )

    # RViz2 for visualization (optional)
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', PathJoinSubstitution([
            FindPackageShare('my_robot_simulation'),
            'config',
            'robot_view.rviz'
        ])],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    return LaunchDescription([
        use_sim_time,
        gazebo,
        robot_state_publisher,
        spawn_entity,
        # rviz  # Uncomment if you have RViz config
    ])
```

## Step 5: Build and Run

Now build your package and run the simulation:

```bash
# Navigate to your workspace
cd ~/ros2_ws

# Build the package
colcon build --packages-select my_robot_simulation

# Source the workspace
source install/setup.bash

# Run the simulation
ros2 launch my_robot_simulation robot_simulation.launch.py
```

## Step 6: Control the Robot

In another terminal, you can send commands to control the robot:

```bash
# Make sure you source the workspace
source ~/ros2_ws/install/setup.bash

# Send velocity commands
ros2 topic pub /cmd_vel geometry_msgs/Twist "linear:
  x: 0.5
  y: 0.0
  z: 0.0
angular:
  x: 0.0
  y: 0.0
  z: 0.2"
```

## Verification Steps

To verify that the setup is working correctly:

1. **Check that Gazebo launched successfully**:
   ```bash
   ros2 node list | grep gazebo
   ```

2. **Check that the robot model is loaded**:
   ```bash
   ros2 topic echo /joint_states --field name
   ```

3. **Verify the robot can move**:
   - Observe the robot moving in the Gazebo simulation
   - Check that the robot's odometry is being published:
     ```bash
     ros2 topic echo /odom --field pose.pose
     ```

4. **Test the command interface**:
   - Send different velocity commands and observe the robot's response

## Troubleshooting

### Common Issues:

1. **Robot not spawning in Gazebo**:
   - Check that the URDF file is valid
   - Verify the robot description is being published: `ros2 topic echo /robot_description`

2. **No movement when sending commands**:
   - Check topic names match between the diff_drive plugin and your commands
   - Verify the joints are properly defined in the URDF

3. **Performance issues**:
   - Reduce physics update rate in the world file
   - Simplify collision meshes in the URDF

## Next Steps

This basic setup provides a foundation for more complex humanoid robot simulations. You can extend this example by:

- Adding more complex robot models with multiple joints and sensors
- Implementing custom controllers for more sophisticated behaviors
- Adding perception sensors like cameras or LiDAR
- Creating more complex environments with obstacles and goals
- Implementing navigation and path planning algorithms

## References

- [ROS 2 Gazebo Documentation](https://gazebosim.org/docs/harmonic/ros_integration/)
- [Robot State Publisher](https://github.com/ros/robot_state_publisher)
- [Gazebo ROS Packages](https://github.com/ros-simulation/gazebo_ros_pkgs)

This example demonstrates the fundamental setup for ROS 2 and Gazebo integration, which is essential for humanoid robot simulation and development.