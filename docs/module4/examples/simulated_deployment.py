"""
Example: Simulated Deployment of Robotic System

This example demonstrates key concepts for deploying robotic systems,
including hardware simulation, system monitoring, and safety checks.
This represents a simulated version of what would be implemented
on actual robotic hardware.

Note: This is a conceptual example showing deployment concepts.
Actual deployment would require real hardware interfaces.
"""

import time
import threading
import signal
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable
import json
import logging
from enum import Enum


class RobotState(Enum):
    """Enumeration of possible robot states during deployment."""
    IDLE = "idle"
    INITIALIZING = "initializing"
    OPERATIONAL = "operational"
    EMERGENCY_STOP = "emergency_stop"
    FAULT = "fault"
    SHUTTING_DOWN = "shutting_down"


@dataclass
class HardwareComponent:
    """Represents a hardware component in the robotic system."""
    name: str
    type: str
    status: str
    health: float  # 0.0 to 1.0
    last_update: float


class SafetySystem:
    """Implements safety monitoring for the robotic system."""

    def __init__(self):
        self.emergency_stop_active = False
        self.safety_limits = {
            "max_velocity": 1.0,  # rad/s for joints
            "max_current": 10.0,  # amps for motors
            "max_temperature": 75.0,  # Celsius
            "collision_threshold": 0.1  # meters for proximity
        }
        self.safety_violations = []

    def check_safety(self, sensor_data: Dict) -> bool:
        """Check if current sensor data violates safety limits."""
        violations = []

        # Check joint velocities
        if "joint_velocities" in sensor_data:
            for i, vel in enumerate(sensor_data["joint_velocities"]):
                if abs(vel) > self.safety_limits["max_velocity"]:
                    violations.append(f"Joint {i} velocity exceeded: {vel} > {self.safety_limits['max_velocity']}")

        # Check temperatures
        if "motor_temperatures" in sensor_data:
            for i, temp in enumerate(sensor_data["motor_temperatures"]):
                if temp > self.safety_limits["max_temperature"]:
                    violations.append(f"Motor {i} temperature exceeded: {temp} > {self.safety_limits['max_temperature']}")

        # Check for proximity alerts
        if "proximity_sensors" in sensor_data:
            for i, dist in enumerate(sensor_data["proximity_sensors"]):
                if dist < self.safety_limits["collision_threshold"]:
                    violations.append(f"Proximity sensor {i} detected obstacle: {dist} < {self.safety_limits['collision_threshold']}")

        self.safety_violations = violations

        # Activate emergency stop if violations exist
        if violations:
            self.emergency_stop_active = True
            return False

        return True

    def trigger_emergency_stop(self):
        """Manually trigger emergency stop."""
        self.emergency_stop_active = True
        print("🚨 EMERGENCY STOP ACTIVATED")

    def reset_safety_system(self):
        """Reset safety system after emergency stop."""
        self.emergency_stop_active = False
        self.safety_violations = []
        print("✅ Safety system reset")


class RobotHardwareSimulator:
    """Simulates hardware components for deployment testing."""

    def __init__(self):
        self.components = {
            "camera": HardwareComponent("camera", "sensor", "ready", 1.0, time.time()),
            "lidar": HardwareComponent("lidar", "sensor", "ready", 1.0, time.time()),
            "imu": HardwareComponent("imu", "sensor", "ready", 1.0, time.time()),
            "motor_1": HardwareComponent("motor_1", "actuator", "ready", 1.0, time.time()),
            "motor_2": HardwareComponent("motor_2", "actuator", "ready", 1.0, time.time()),
            "motor_3": HardwareComponent("motor_3", "actuator", "ready", 1.0, time.time()),
        }

        self.joint_positions = [0.0, 0.0, 0.0]
        self.joint_velocities = [0.0, 0.0, 0.0]
        self.motor_temperatures = [25.0, 25.0, 25.0]
        self.proximity_sensors = [1.0, 1.0, 1.0, 1.0]  # meters
        self.battery_level = 100.0  # percentage

    def update_hardware_status(self):
        """Simulate hardware status updates."""
        current_time = time.time()

        for name, component in self.components.items():
            # Simulate occasional hardware issues
            if name.startswith("motor_") and component.health > 0.95:
                # Small chance of health degradation
                import random
                if random.random() < 0.01:  # 1% chance per update
                    component.health -= 0.05
                    component.status = "degraded"

            component.last_update = current_time

    def get_sensor_data(self) -> Dict:
        """Get simulated sensor data."""
        # Simulate sensor readings with some noise
        import random

        return {
            "joint_positions": self.joint_positions.copy(),
            "joint_velocities": [v + random.uniform(-0.01, 0.01) for v in self.joint_velocities],
            "motor_temperatures": [t + random.uniform(-1.0, 1.0) for t in self.motor_temperatures],
            "proximity_sensors": [d + random.uniform(-0.01, 0.01) for d in self.proximity_sensors],
            "battery_level": self.battery_level,
            "timestamp": time.time()
        }

    def execute_command(self, command: Dict) -> bool:
        """Simulate executing a robot command."""
        if command["type"] == "move_joints":
            target_positions = command["positions"]
            duration = command.get("duration", 1.0)

            # Simulate movement
            for i in range(len(self.joint_positions)):
                if i < len(target_positions):
                    self.joint_positions[i] = target_positions[i]

            # Update velocities based on movement
            for i in range(len(self.joint_velocities)):
                if i < len(target_positions):
                    self.joint_velocities[i] = (target_positions[i] - self.joint_positions[i]) / duration

            return True

        elif command["type"] == "navigate":
            # Simulate navigation command
            target = command["target"]
            print(f" navigating to {target}")
            return True

        return False


class SystemMonitor:
    """Monitors system health and performance."""

    def __init__(self):
        self.cpu_usage = 0.0
        self.memory_usage = 0.0
        self.disk_usage = 0.0
        self.network_status = "connected"
        self.uptime = 0.0
        self.start_time = time.time()

    def update_metrics(self):
        """Update system metrics (simulated)."""
        import random
        self.cpu_usage = random.uniform(10.0, 80.0)
        self.memory_usage = random.uniform(20.0, 70.0)
        self.disk_usage = random.uniform(30.0, 60.0)
        self.uptime = time.time() - self.start_time

    def get_system_status(self) -> Dict:
        """Get current system status."""
        return {
            "cpu_usage": self.cpu_usage,
            "memory_usage": self.memory_usage,
            "disk_usage": self.disk_usage,
            "network_status": self.network_status,
            "uptime": self.uptime,
            "timestamp": time.time()
        }


class DeploymentManager:
    """Manages the deployment of the robotic system."""

    def __init__(self):
        self.state = RobotState.IDLE
        self.hardware = RobotHardwareSimulator()
        self.safety_system = SafetySystem()
        self.monitor = SystemMonitor()
        self.running = False
        self.deployment_thread = None

        # Set up signal handling for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"\nReceived signal {signum}, initiating shutdown...")
        self.shutdown()
        sys.exit(0)

    def initialize_system(self):
        """Initialize the robotic system for deployment."""
        print("🚀 Initializing robotic system...")

        self.state = RobotState.INITIALIZING

        # Initialize hardware components
        for name, component in self.hardware.components.items():
            print(f"  Initializing {name}...")
            time.sleep(0.1)  # Simulate initialization time
            component.status = "initialized"

        # Initialize safety system
        print("  Initializing safety system...")
        time.sleep(0.2)

        # Initialize monitoring
        print("  Initializing system monitoring...")
        time.sleep(0.1)

        print("✅ System initialization complete")
        self.state = RobotState.OPERATIONAL

    def run_deployment_loop(self):
        """Main deployment loop that runs in a separate thread."""
        while self.running:
            try:
                # Update system metrics
                self.monitor.update_metrics()

                # Update hardware status
                self.hardware.update_hardware_status()

                # Get sensor data
                sensor_data = self.hardware.get_sensor_data()

                # Check safety
                is_safe = self.safety_system.check_safety(sensor_data)

                if not is_safe and self.safety_system.safety_violations:
                    print(f"⚠️  Safety violations detected: {self.safety_system.safety_violations}")
                    self.state = RobotState.EMERGENCY_STOP
                    break

                # Simulate periodic tasks
                time.sleep(0.1)  # 100Hz update rate

            except Exception as e:
                print(f"❌ Error in deployment loop: {e}")
                self.state = RobotState.FAULT
                break

    def start_deployment(self):
        """Start the robotic system deployment."""
        if self.state != RobotState.OPERATIONAL:
            self.initialize_system()

        print("🔧 Starting robotic system deployment...")
        self.running = True
        self.deployment_thread = threading.Thread(target=self.run_deployment_loop)
        self.deployment_thread.start()

        print("✅ Deployment started successfully")
        self.state = RobotState.OPERATIONAL

    def execute_robot_command(self, command: Dict) -> bool:
        """Execute a command on the robot."""
        if self.state != RobotState.OPERATIONAL:
            print(f"❌ Cannot execute command, robot is in {self.state.value} state")
            return False

        if self.safety_system.emergency_stop_active:
            print("❌ Cannot execute command, emergency stop is active")
            return False

        print(f"🤖 Executing command: {command}")
        success = self.hardware.execute_command(command)

        if success:
            print("✅ Command executed successfully")
        else:
            print("❌ Command execution failed")

        return success

    def get_system_status(self) -> Dict:
        """Get comprehensive system status."""
        return {
            "state": self.state.value,
            "safety_status": {
                "emergency_stop": self.safety_system.emergency_stop_active,
                "violations": self.safety_system.safety_violations
            },
            "hardware_status": {
                name: {
                    "status": comp.status,
                    "health": comp.health,
                    "last_update": comp.last_update
                }
                for name, comp in self.hardware.components.items()
            },
            "system_metrics": self.monitor.get_system_status(),
            "sensor_data": self.hardware.get_sensor_data()
        }

    def shutdown(self):
        """Gracefully shut down the robotic system."""
        print("🛑 Initiating system shutdown...")
        self.running = False

        if self.deployment_thread and self.deployment_thread.is_alive():
            self.deployment_thread.join(timeout=2.0)

        print("✅ System shutdown complete")
        self.state = RobotState.SHUTTING_DOWN


def main():
    """Main function demonstrating simulated deployment."""
    print("=== Simulated Robotic System Deployment ===\n")

    # Create deployment manager
    deployment = DeploymentManager()

    try:
        # Initialize and start deployment
        deployment.initialize_system()
        deployment.start_deployment()

        # Wait a moment for systems to stabilize
        time.sleep(1)

        # Display initial system status
        print("\n📋 Initial System Status:")
        status = deployment.get_system_status()
        print(json.dumps(status, indent=2, default=str))

        # Execute some sample commands
        print("\n🤖 Executing sample commands...")

        commands = [
            {
                "type": "move_joints",
                "positions": [0.5, 0.3, -0.2],
                "duration": 2.0
            },
            {
                "type": "navigate",
                "target": [1.0, 2.0, 0.0]
            },
            {
                "type": "move_joints",
                "positions": [0.0, 0.0, 0.0],
                "duration": 1.5
            }
        ]

        for i, command in enumerate(commands):
            print(f"\n--- Command {i+1} ---")
            success = deployment.execute_robot_command(command)

            # Wait between commands
            time.sleep(0.5)

            # Display status after command
            print("Current status:")
            status = deployment.get_system_status()
            print(f"  State: {status['state']}")
            print(f"  Safety: {'✅ OK' if not status['safety_status']['emergency_stop'] else '🚨 EMERGENCY'}")
            print(f"  CPU: {status['system_metrics']['cpu_usage']:.1f}%")
            print(f"  Battery: {status['sensor_data']['battery_level']:.1f}%")

        # Simulate a safety event
        print("\n⚠️  Simulating safety event...")
        deployment.safety_system.safety_violations = ["Proximity sensor detected obstacle"]
        deployment.safety_system.emergency_stop_active = True
        deployment.state = RobotState.EMERGENCY_STOP

        print(f"State after safety event: {deployment.state.value}")
        print(f"Emergency stop active: {deployment.safety_system.emergency_stop_active}")

        # Reset safety system
        print("\n🔧 Resetting safety system...")
        deployment.safety_system.reset_safety_system()
        deployment.state = RobotState.OPERATIONAL

        print(f"State after reset: {deployment.state.value}")

        # Display final status
        print("\n📋 Final System Status:")
        final_status = deployment.get_system_status()
        print(json.dumps(final_status, indent=2, default=str))

        print(f"\n📊 Deployment Statistics:")
        metrics = final_status["system_metrics"]
        print(f"  Uptime: {metrics['uptime']:.2f} seconds")
        print(f"  Peak CPU: {metrics['cpu_usage']:.1f}%")
        print(f"  Memory Usage: {metrics['memory_usage']:.1f}%")

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    finally:
        # Always shut down properly
        deployment.shutdown()

    print("\n✅ Simulated deployment completed successfully")


if __name__ == "__main__":
    main()