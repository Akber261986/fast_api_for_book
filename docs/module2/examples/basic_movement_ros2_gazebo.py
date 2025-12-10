"""
Basic Movement Example for ROS 2/Gazebo

This script demonstrates how to control a robot in Gazebo simulation using ROS 2.
It sends velocity commands to make the robot move in a square pattern.
"""

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


"""
Additional Example: Waypoint Navigation

This is an alternative implementation that moves the robot to specific waypoints.
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, Point
from nav_msgs.msg import Odometry
import math


class WaypointNavigator(Node):
    """
    A controller that moves the robot to specified waypoints.
    """

    def __init__(self):
        super().__init__('waypoint_navigator')

        # Create publisher for velocity commands
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Create subscriber for odometry
        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        # Waypoints to visit (x, y coordinates)
        self.waypoints = [
            Point(x=1.0, y=0.0),
            Point(x=1.0, y=1.0),
            Point(x=0.0, y=1.0),
            Point(x=0.0, y=0.0)  # Return to start
        ]

        self.current_waypoint_index = 0
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_yaw = 0.0

        # Movement parameters
        self.linear_speed = 0.3
        self.angular_speed = 0.3
        self.arrival_threshold = 0.1  # Distance threshold for reaching waypoint

        # Create timer for control loop
        self.timer = self.create_timer(0.1, self.control_loop)

        self.get_logger().info('Waypoint Navigator initialized')

    def odom_callback(self, msg):
        """
        Update robot's current position and orientation.
        """
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
        Control loop for waypoint navigation.
        """
        if self.current_waypoint_index >= len(self.waypoints):
            # All waypoints reached, stop the robot
            stop_msg = Twist()
            self.cmd_vel_pub.publish(stop_msg)
            self.get_logger().info('All waypoints reached. Robot stopped.')
            self.timer.cancel()
            return

        # Get current waypoint
        target = self.waypoints[self.current_waypoint_index]

        # Calculate distance and angle to target
        dx = target.x - self.current_x
        dy = target.y - self.current_y
        distance_to_target = math.sqrt(dx*dx + dy*dy)
        target_angle = math.atan2(dy, dx)

        # Calculate angle difference
        angle_diff = target_angle - self.current_yaw
        # Normalize angle to [-pi, pi]
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi

        msg = Twist()

        if distance_to_target > self.arrival_threshold:
            # If far from target, rotate towards it first
            if abs(angle_diff) > 0.1:  # 0.1 rad = ~5.7 degrees
                msg.angular.z = self.angular_speed if angle_diff > 0 else -self.angular_speed
            else:
                # Move forward toward target
                msg.linear.x = min(self.linear_speed, distance_to_target)
        else:
            # Close enough to target, move to next waypoint
            self.current_waypoint_index += 1
            if self.current_waypoint_index < len(self.waypoints):
                self.get_logger().info(f'Reached waypoint {self.current_waypoint_index}. Moving to next.')
            else:
                self.get_logger().info('All waypoints reached.')
                msg.linear.x = 0.0
                msg.angular.z = 0.0

        # Publish command
        self.cmd_vel_pub.publish(msg)

        # Log information
        self.get_logger().info(
            f'Waypoint {self.current_waypoint_index + 1}/{len(self.waypoints)}, '
            f'Distance: {distance_to_target:.2f}m, '
            f'Position: ({self.current_x:.2f}, {self.current_y:.2f})'
        )


def run_waypoint_navigation(args=None):
    """
    Function to run the waypoint navigation example.
    """
    rclpy.init(args=args)

    navigator = WaypointNavigator()

    try:
        rclpy.spin(navigator)
    except KeyboardInterrupt:
        navigator.get_logger().info('Interrupted by user')
    finally:
        navigator.destroy_node()
        rclpy.shutdown()


"""
To run the waypoint navigation example, uncomment the following lines
and run this script with the command-line argument 'waypoint':

Example usage:
- For basic square movement: python basic_movement_ros2_gazebo.py
- For waypoint navigation: python basic_movement_ros2_gazebo.py waypoint
"""

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'waypoint':
        run_waypoint_navigation()
    else:
        main()