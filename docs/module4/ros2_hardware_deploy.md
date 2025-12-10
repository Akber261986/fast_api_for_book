# ROS 2 Deployment on Robot Hardware

## Overview

Deploying ROS 2-based robotic systems on physical hardware requires careful consideration of hardware constraints, real-time performance requirements, and safety considerations. This chapter provides a comprehensive guide to deploying ROS 2 systems on humanoid robots and other robotic platforms.

## Hardware Requirements Assessment

### Computing Platform Selection

When selecting a computing platform for ROS 2 deployment, consider:

**Performance Requirements:**
- CPU: Multi-core processor for handling multiple ROS 2 nodes
- GPU: For AI processing, computer vision, and simulation
- RAM: Typically 8GB+ for complex robotic systems
- Storage: SSD for fast I/O operations

**Environmental Considerations:**
- Power consumption for mobile robots
- Heat dissipation in enclosed spaces
- Vibration resistance for mobile platforms
- Operating temperature range

**Connectivity:**
- Multiple USB ports for sensors and peripherals
- Ethernet for high-bandwidth sensor data
- WiFi/Bluetooth for communication
- Serial interfaces for legacy devices

### Recommended Hardware Platforms

#### High-Performance Platforms
- **NVIDIA Jetson AGX Orin**: Excellent for AI workloads with 2048 CUDA cores
- **NVIDIA Jetson Orin NX**: Balance of performance and power efficiency
- **Custom PC with discrete GPU**: Maximum performance for stationary robots

#### Mid-Range Platforms
- **NVIDIA Jetson Orin Nano**: Good for moderate AI workloads
- **Intel NUC with integrated GPU**: x86 compatibility with reasonable performance
- **Raspberry Pi 4 (multiple units)**: Distributed processing approach

#### Specialized Platforms
- **Robot computers**: Pre-integrated with robotics I/O
- **Ruggedized systems**: For harsh environments
- **Safety-certified platforms**: For applications requiring safety certification

## ROS 2 Installation on Target Hardware

### System Preparation

Before installing ROS 2, prepare the target system:

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Set up locale
sudo locale-gen en_US.UTF-8
export LANG=en_US.UTF-8

# Set up sources.list
sudo apt install software-properties-common
sudo add-apt-repository universe

# Add ROS 2 GPG key
sudo apt update && sudo apt install curl gnupg lsb-release
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

# Add ROS 2 repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(source /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# Install ROS 2 packages
sudo apt update
sudo apt install ros-humble-desktop
sudo apt install python3-rosdep python3-rosinstall python3-rosinstall-generator python3-wstool build-essential
```

### Additional Dependencies

Install hardware-specific dependencies:

```bash
# Initialize rosdep
sudo rosdep init
rosdep update

# Install additional packages for robotics
sudo apt install ros-humble-ros2-control ros-humble-ros2-controllers
sudo apt install ros-humble-gazebo-ros2-control
sudo apt install ros-humble-moveit
sudo apt install ros-humble-navigation2 ros-humble-nav2-bringup
```

## Real-Time Considerations

### Real-Time Kernel

For time-critical applications, consider using a real-time kernel:

```bash
# Install real-time kernel
sudo apt install linux-image-rt-generic

# Configure GRUB to default to real-time kernel
sudo nano /etc/default/grub
# Add 'quiet splash' to GRUB_CMDLINE_LINUX_DEFAULT
sudo update-grub
```

### CPU Isolation

Isolate CPUs for real-time ROS 2 nodes:

```bash
# Add to kernel command line in /etc/default/grub
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash isolcpus=1,2,3"
sudo update-grub
```

### Real-Time Scheduling

Configure real-time scheduling for ROS 2 processes:

```bash
# Add user to real-time group
sudo usermod -a -G realtime $USER

# Configure RT limits in /etc/security/limits.conf
echo "$USER soft rtprio 99" | sudo tee -a /etc/security/limits.conf
echo "$USER hard rtprio 99" | sudo tee -a /etc/security/limits.conf
```

## Hardware Interface Development

### Sensor Integration

ROS 2 provides standard interfaces for various sensors:

**Camera Integration:**
```cpp
// Example camera driver node
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <cv_bridge/cv_bridge.h>
#include <opencv2/opencv.hpp>

class CameraDriver : public rclcpp::Node
{
public:
    CameraDriver() : Node("camera_driver")
    {
        publisher_ = this->create_publisher<sensor_msgs::msg::Image>("camera/image_raw", 10);
        timer_ = this->create_wall_timer(
            std::chrono::milliseconds(33), std::bind(&CameraDriver::capture_frame, this));

        // Initialize camera
        cap_.open(0); // Open default camera
    }

private:
    void capture_frame()
    {
        cv::Mat frame;
        cap_ >> frame;

        if (!frame.empty()) {
            auto msg = cv_bridge::CvImage(std_msgs::msg::Header(), "bgr8", frame).toImageMsg();
            publisher_->publish(*msg);
        }
    }

    rclcpp::Publisher<sensor_msgs::msg::Image>::SharedPtr publisher_;
    rclcpp::TimerBase::SharedPtr timer_;
    cv::VideoCapture cap_;
};
```

**LIDAR Integration:**
```xml
<!-- In package.xml -->
<depend>sensor_msgs</depend>
<depend>laser_geometry</depend>
```

```cpp
// LIDAR driver example
#include <sensor_msgs/msg/laser_scan.hpp>

class LIDARDriver : public rclcpp::Node
{
public:
    LIDARDriver() : Node("lidar_driver")
    {
        publisher_ = this->create_publisher<sensor_msgs::msg::LaserScan>("scan", 10);
    }

private:
    rclcpp::Publisher<sensor_msgs::msg::LaserScan>::SharedPtr publisher_;
};
```

### Actuator Control

ROS 2 Control framework for hardware interfaces:

**Control Configuration:**
```yaml
# controller_manager.yaml
controller_manager:
  ros__parameters:
    update_rate: 100  # Hz

    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster

    position_trajectory_controller:
      type: position_controllers/JointTrajectoryController

position_trajectory_controller:
  ros__parameters:
    joints:
      - joint1
      - joint2
      - joint3
    command_interfaces:
      - position
    state_interfaces:
      - position
      - velocity
```

## Safety Systems Integration

### Emergency Stop Implementation

Critical safety systems must be implemented both in software and hardware:

```cpp
// Emergency stop node
class EmergencyStop : public rclcpp::Node
{
public:
    EmergencyStop() : Node("emergency_stop")
    {
        // Subscribe to emergency stop topic
        estop_sub_ = this->create_subscription<std_msgs::msg::Bool>(
            "emergency_stop", 1,
            std::bind(&EmergencyStop::estop_callback, this, std::placeholders::_1));

        // Create service to reset emergency stop
        reset_service_ = this->create_service<std_srvs::srv::Trigger>(
            "reset_emergency_stop",
            std::bind(&EmergencyStop::reset_callback, this, std::placeholders::_1, std::placeholders::_2));
    }

private:
    void estop_callback(const std_msgs::msg::Bool::SharedPtr msg)
    {
        if (msg->data) {
            // Stop all robot motion
            stop_all_controllers();
        }
    }

    rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr estop_sub_;
    rclcpp::Service<std_srvs::srv::Trigger>::SharedPtr reset_service_;
};
```

### Safety Monitor

Implement a safety monitor node that watches system state:

```cpp
// Safety monitor node
class SafetyMonitor : public rclcpp::Node
{
public:
    SafetyMonitor() : Node("safety_monitor")
    {
        // Subscribe to relevant topics
        joint_state_sub_ = this->create_subscription<sensor_msgs::msg::JointState>(
            "joint_states", 10,
            std::bind(&SafetyMonitor::joint_state_callback, this, std::placeholders::_1));

        // Timer for periodic safety checks
        timer_ = this->create_wall_timer(
            std::chrono::milliseconds(100), std::bind(&SafetyMonitor::check_safety, this));
    }

private:
    void joint_state_callback(const sensor_msgs::msg::JointState::SharedPtr msg)
    {
        // Store joint states for safety checks
        current_joint_states_ = *msg;
    }

    void check_safety()
    {
        // Check for dangerous conditions
        for (size_t i = 0; i < current_joint_states_.position.size(); ++i) {
            if (std::abs(current_joint_states_.velocity[i]) > MAX_VELOCITY) {
                RCLCPP_WARN(this->get_logger(), "Joint %zu velocity exceeded limit", i);
                // Trigger safety action
            }
        }
    }

    rclcpp::Subscription<sensor_msgs::msg::JointState>::SharedPtr joint_state_sub_;
    rclcpp::TimerBase::SharedPtr timer_;
    sensor_msgs::msg::JointState current_joint_states_;
    static constexpr double MAX_VELOCITY = 5.0; // rad/s
};
```

## Deployment Configuration

### Launch Files

Create launch files for hardware-specific deployments:

```python
# hardware_launch.py
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # Declare launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')

    # Camera driver node
    camera_node = Node(
        package='v4l2_camera',
        executable='v4l2_camera_node',
        parameters=[{
            'video_device': '/dev/video0',
            'image_size': [640, 480],
            'camera_frame_id': 'camera_link'
        }],
        condition=LaunchConfigurationEquals('use_camera', 'true')
    )

    # Joint state publisher
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        parameters=[{
            'use_sim_time': use_sim_time
        }]
    )

    # Robot state publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_description': open(os.path.join(
                get_package_share_directory('my_robot_description'),
                'urdf', 'my_robot.urdf'
            )).read()
        }]
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument('use_camera', default_value='true'),
        camera_node,
        joint_state_publisher,
        robot_state_publisher
    ])
```

### Parameter Files

Use YAML parameter files for hardware-specific configurations:

```yaml
# config/hardware_params.yaml
/**:
  ros__parameters:
    # Hardware-specific parameters
    hardware:
      loop_rate: 100
      timeout: 0.1
      max_velocity: 1.0
      max_effort: 100.0

    # Sensor parameters
    sensors:
      camera:
        exposure: -6
        gain: 1.0
        white_balance: 4000
      imu:
        rate: 100

    # Control parameters
    controllers:
      position:
        kp: 10.0
        ki: 0.1
        kd: 0.05
```

## Network Configuration

### Real-time Network Setup

For distributed robotic systems, configure network for real-time performance:

```bash
# Optimize network settings in /etc/sysctl.conf
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.core.rmem_default = 65536
net.core.wmem_default = 65536
net.core.netdev_max_backlog = 5000
```

### DDS Configuration

Configure DDS for optimal performance:

```xml
<!-- ros2_dds_config.xml -->
<dds>
    <profiles xmlns="http://www.eprosima.com/XMLSchemas/fastRTPS_Profiles">
        <transport_descriptors>
            <transport_descriptor>
                <transport_id>CustomUdpTransport</transport_id>
                <type>UDPv4</type>
                <sendBufferSize>65536</sendBufferSize>
                <receiveBufferSize>65536</receiveBufferSize>
            </transport_descriptor>
        </transport_descriptors>

        <participant profile_name="custom_participant" is_default_profile="true">
            <rtps>
                <userTransports>
                    <transport_id>CustomUdpTransport</transport_id>
                </userTransports>
                <useBuiltinTransports>false</useBuiltinTransports>
            </rtps>
        </participant>
    </profiles>
</dds>
```

## Monitoring and Diagnostics

### System Monitoring

Implement monitoring for deployed systems:

```cpp
// System monitor node
class SystemMonitor : public rclcpp::Node
{
public:
    SystemMonitor() : Node("system_monitor")
    {
        // Publishers for system metrics
        cpu_pub_ = this->create_publisher<std_msgs::msg::Float32>("diagnostics/cpu_usage", 1);
        memory_pub_ = this->create_publisher<std_msgs::msg::Float32>("diagnostics/memory_usage", 1);

        // Timer for periodic monitoring
        monitor_timer_ = this->create_wall_timer(
            std::chrono::seconds(1), std::bind(&SystemMonitor::monitor_system, this));
    }

private:
    void monitor_system()
    {
        // Monitor CPU usage
        float cpu_usage = get_cpu_usage();
        auto cpu_msg = std_msgs::msg::Float32();
        cpu_msg.data = cpu_usage;
        cpu_pub_->publish(cpu_msg);

        // Monitor memory usage
        float memory_usage = get_memory_usage();
        auto memory_msg = std_msgs::msg::Float32();
        memory_msg.data = memory_usage;
        memory_pub_->publish(memory_msg);
    }

    rclcpp::Publisher<std_msgs::msg::Float32>::SharedPtr cpu_pub_;
    rclcpp::Publisher<std_msgs::msg::Float32>::SharedPtr memory_pub_;
    rclcpp::TimerBase::SharedPtr monitor_timer_;
};
```

### Logging Configuration

Configure logging for deployed systems:

```yaml
# config/logging_config.yaml
log_config:
  version: 1
  formatters:
    default:
      format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  handlers:
    file:
      class: logging.FileHandler
      filename: /var/log/robot/robot.log
      formatter: default
      level: INFO
    console:
      class: logging.StreamHandler
      formatter: default
      level: WARNING
  loggers:
    robot_system:
      level: INFO
      handlers: [file, console]
      propagate: false
```

## Deployment Best Practices

### Version Management

- Use Docker containers for consistent deployments
- Tag and version all software components
- Maintain separate configurations for different hardware platforms
- Implement rollback mechanisms

### Testing Before Deployment

1. **Simulation Testing**: Validate all functionality in simulation
2. **Hardware-in-the-Loop**: Test with actual hardware components
3. **Safety Testing**: Verify all safety systems function correctly
4. **Performance Testing**: Ensure real-time requirements are met

### Documentation

- Hardware setup procedures
- Calibration procedures
- Troubleshooting guides
- Maintenance schedules

## References

- [ROS 2 Hardware Integration Guide](https://docs.ros.org/en/rolling/Tutorials/Advanced/Integration.html)
- [ROS 2 Control Hardware Integration](https://control.ros.org/)
- [Real-time ROS 2 Deployment](https://docs.ros.org/en/rolling/How-To-Guides/Real-time-with-ROS2.html)
- [Robot Deployment Best Practices](https://navigation.ros.org/setup_guides/index.html)

---

**Previous**: [Deployment Architectures](./deployment_arch.md) | **Next**: [Module 4 Examples](../module4/examples/) | [Table of Contents](../README.md)