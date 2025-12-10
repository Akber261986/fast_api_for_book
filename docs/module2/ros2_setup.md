# ROS 2 Setup for Robotics

## Overview

Robot Operating System 2 (ROS 2) is a flexible framework for writing robot software. It provides services designed for a heterogeneous computer cluster such as hardware abstraction, device drivers, libraries, visualizers, message-passing, package management, and more. This module covers the setup and configuration of ROS 2 for humanoid robotics applications.

## What is ROS 2?

ROS 2 is the second generation of the Robot Operating System. It addresses limitations of the original ROS, particularly in areas of:

- **Real-time support**: Better real-time capabilities for time-critical robotic applications
- **Multi-robot systems**: Improved support for multiple robots working together
- **Security**: Built-in security features for safe robot operation
- **Deterministic behavior**: More predictable behavior for safety-critical applications
- **Commercial deployment**: Better support for production environments

## ROS 2 Architecture

### DDS (Data Distribution Service)

ROS 2 uses DDS as its middleware, which provides:

- **Publisher-Subscriber pattern**: Asynchronous communication between nodes
- **Request-Response pattern**: Synchronous communication for services
- **Discovery**: Automatic discovery of nodes and topics
- **Quality of Service (QoS)**: Configurable reliability and performance settings

### Core Concepts

- **Nodes**: Processes that perform computation
- **Topics**: Named buses over which nodes exchange messages
- **Messages**: ROS data types used when publishing or subscribing to a topic
- **Services**: Synchronous request/response communication
- **Actions**: Goal-oriented communication with feedback and status

## Installing ROS 2

### System Requirements

- **Operating System**: Ubuntu 20.04 (Focal) or Ubuntu 22.04 (Jammy) recommended
- **Architecture**: 64-bit x86 (AMD64) or ARM64
- **RAM**: Minimum 8GB recommended for development
- **Disk Space**: At least 5GB of free space

### Installation Steps

#### 1. Set up locale
```bash
locale  # Check for UTF-8
sudo apt update && sudo apt install locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8
```

#### 2. Set up sources
```bash
sudo apt update && sudo apt install curl gnupg lsb-release
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(source /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
```

#### 3. Install ROS 2
```bash
sudo apt update
sudo apt install ros-humble-desktop
```

#### 4. Environment setup
```bash
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

#### 5. Install additional tools
```bash
sudo apt install python3-colcon-common-extensions python3-rosdep python3-vcstool
sudo rosdep init
rosdep update
```

## ROS 2 for Humanoid Robotics

### Key Packages for Humanoid Development

- **ros2_control**: Hardware abstraction and control framework
- **navigation2**: Navigation stack for mobile robots
- **moveit2**: Motion planning framework
- **rviz2**: 3D visualization tool for robot sensors and data
- **ros_gz**: Integration with Gazebo simulation
- **tf2**: Transform library for coordinate frame management

### TF2 (Transform Library)

For humanoid robots, managing coordinate frames is crucial:

- **base_link**: The main body of the robot
- **torso**: Torso frame for upper body
- **head**: Head frame for sensors
- **left_arm_base**, **right_arm_base**: Arm base frames
- **left_foot**, **right_foot**: Foot frames for balance

## Creating a ROS 2 Workspace

### 1. Create workspace directory
```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws
```

### 2. Build the workspace
```bash
colcon build
source install/setup.bash
```

### 3. Verify installation
```bash
ros2 topic list
ros2 node list
```

## ROS 2 Launch System

### Launch Files

Launch files allow you to start multiple nodes with a single command:

```xml
<launch>
  <!-- Robot state publisher -->
  <node pkg="robot_state_publisher" exec="robot_state_publisher" name="robot_state_publisher">
    <param name="robot_description" value="$(find-pkg-share my_robot_description)/urdf/my_robot.urdf"/>
  </node>

  <!-- Joint state publisher -->
  <node pkg="joint_state_publisher" exec="joint_state_publisher" name="joint_state_publisher"/>

  <!-- Controller manager -->
  <node pkg="controller_manager" exec="ros2_control_node" name="ros2_control_node">
    <param name="robot_description" value="$(var robot_description)"/>
  </node>
</launch>
```

## Quality of Service (QoS) Settings

For humanoid robotics, appropriate QoS settings are important:

- **Reliability**: Use RELIABLE for critical control messages
- **Durability**: Use TRANSIENT_LOCAL for configuration parameters
- **Deadline**: Set appropriate deadlines for control loops

## Troubleshooting Common Issues

### Network Configuration

For multi-robot systems, ensure proper network configuration:

```bash
# Check ROS domain ID
echo $ROS_DOMAIN_ID

# Set ROS domain ID for isolated networks
export ROS_DOMAIN_ID=1
```

### Permission Issues

If experiencing permission issues with serial devices:

```bash
sudo usermod -a -G dialout $USER
# Log out and back in for changes to take effect
```

## Best Practices for Humanoid Robotics

### 1. Node Design
- Keep nodes focused on single responsibilities
- Use composition for complex behaviors
- Implement proper error handling and recovery

### 2. Message Design
- Use standard message types when possible
- Design efficient custom message types
- Consider bandwidth limitations for wireless communication

### 3. Performance
- Monitor CPU and memory usage
- Use appropriate update rates for different systems
- Implement proper logging without performance impact

## Example: Simple ROS 2 Node for Humanoid Control

Here's a basic example of a ROS 2 node that could be used for humanoid control:

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from geometry_msgs.msg import Twist
from std_msgs.msg import String

class HumanoidController(Node):
    def __init__(self):
        super().__init__('humanoid_controller')

        # Publishers
        self.joint_pub = self.create_publisher(JointState, 'joint_commands', 10)
        self.status_pub = self.create_publisher(String, 'robot_status', 10)

        # Subscribers
        self.cmd_vel_sub = self.create_subscription(
            Twist,
            'cmd_vel',
            self.cmd_vel_callback,
            10
        )

        # Timer for control loop
        self.timer = self.create_timer(0.05, self.control_loop)  # 20 Hz

        self.get_logger().info('Humanoid Controller initialized')

    def cmd_vel_callback(self, msg):
        # Process velocity commands
        self.get_logger().info(f'Received velocity command: {msg.linear.x}, {msg.angular.z}')

    def control_loop(self):
        # Main control loop implementation
        joint_msg = JointState()
        joint_msg.name = ['left_hip', 'left_knee', 'right_hip', 'right_knee']
        joint_msg.position = [0.0, 0.0, 0.0, 0.0]  # Example positions

        self.joint_pub.publish(joint_msg)

def main(args=None):
    rclpy.init(args=args)
    controller = HumanoidController()
    rclpy.spin(controller)
    controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Practical Exercise: Complete ROS 2 + Gazebo Setup

Let's look at a complete practical example of setting up ROS 2 with Gazebo, which is available in the examples directory as `ros2_gazebo_setup.md`:

This example demonstrates how to create a complete simulation environment with a simple robot that can be controlled through ROS 2:

1. **Create a ROS 2 package**:
   ```bash
   # Navigate to your ROS 2 workspace
   cd ~/ros2_ws/src

   # Create the package
   ros2 pkg create --build-type ament_python my_robot_simulation --dependencies rclpy std_msgs sensor_msgs geometry_msgs
   ```

2. **Create Robot URDF**:
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

3. **Run the simulation**:
   ```bash
   # Build the package
   cd ~/ros2_ws
   colcon build --packages-select my_robot_simulation
   source install/setup.bash

   # Launch the simulation
   ros2 launch my_robot_simulation robot_simulation.launch.py
   ```

## Verification Steps

To verify your ROS 2 installation and basic functionality:

1. **Check Installation**:
   ```bash
   # Verify ROS 2 installation
   echo $ROS_DISTRO
   ros2 --version

   # Check available commands
   ros2
   ```

2. **Test Basic Communication**:
   ```bash
   # In one terminal
   ros2 topic pub /chatter std_msgs/String "data: Hello ROS2"

   # In another terminal
   ros2 topic echo /chatter
   ```

3. **Verify Package Creation**:
   ```bash
   # Check if your package was created
   ros2 pkg list | grep my_robot_simulation
   ```

4. **Check Node Communication**:
   ```bash
   # List active nodes
   ros2 node list

   # Check topic information
   ros2 topic info /joint_states
   ```

5. **Test Robot Control**:
   ```bash
   # Send velocity commands to your simulated robot
   ros2 topic pub /cmd_vel geometry_msgs/Twist "linear:
     x: 0.5
     y: 0.0
     z: 0.0
   angular:
     x: 0.0
     y: 0.0
     z: 0.2"
   ```

## References

- [ROS 2 Documentation](https://docs.ros.org/en/humble/) - Official ROS 2 documentation
- [ROS 2 Tutorials](https://docs.ros.org/en/humble/Tutorials.html) - Step-by-step ROS 2 tutorials
- [ROS 2 Design](https://design.ros2.org/) - Design documents for ROS 2 architecture
- [Humanoid Robot ROS Packages](https://index.ros.org/packages/page/1/doc-type/Package/sort/title/direction/asc/q/humanoid/) - ROS packages for humanoid robots

## References

- [ROS 2 Documentation](https://docs.ros.org/en/humble/) - Official ROS 2 documentation (verified: official source)
- [ROS 2 Design](https://design.ros2.org/) - Design documents for ROS 2 architecture (verified: official source)
- [ROS 2 Packages for Humanoid Robots](https://index.ros.org/packages/page/1/doc-type/Package/sort/title/direction/asc/q/humanoid/) - ROS packages for humanoid robots (verified: official ROS index)
- [Open Robotics](https://www.openrobotics.org/) - Organization behind ROS development (verified: official organization)

## Additional Resources

- [ROS Discourse](https://discourse.ros.org/) - Community forum for ROS questions
- [ROS Answers](https://answers.ros.org/questions/) - Q&A site for ROS support
- [ROS 2 GitHub](https://github.com/ros2) - Source code repositories