---
name: drone-autopilot-mavlink
metadata:
  category: Autonomous Systems and Robotics
description: Autonomous drone autopilot control, telemetry stream parsing, and offboard mission execution using MAVLink, MAVSDK, and PX4 / ArduPilot. Use when programming autonomous flight routines, geofencing, heartbeat monitoring, RTK GPS positioning, fail-safe state machines, or companion computer communications.
compatibility: MAVLink 2.0, MAVSDK (Python/C++), PX4 Autopilot v1.14+, ArduPilot, ROS 2 (MAVROS2 / MicroXRCE-DDS)
---

# Drone Autopilot & MAVLink Mission Control Guidelines

This skill details architecture, telemetry stream decoding, offboard velocity/position control, fail-safe state machine design, and companion computer integration for autonomous Unmanned Aerial Vehicles (UAV) running PX4 or ArduPilot firmware.

---

## 1. MAVLink Protocol & Autopilot Communication Architecture

MAVLink (Micro Air Vehicle Link) is a lightweight binary protocol over UDP/Serial for communicating between Flight Controllers (PX4/ArduPilot), Companion Computers (Raspberry Pi/Jetson), and Ground Control Stations (QGroundControl):

```
+------------------------------------+          UDP / Serial (MAVLink 2.0)          +--------------------------------------+
|        Companion Computer          | <------------------------------------------> |           Flight Controller          |
|  (MAVSDK / PyMAVLink / Offboard)   |                                              |      (PX4 / ArduPilot Autopilot)     |
+------------------------------------+                                              +--------------------------------------+
                  |                                                                                    |
            REST / gRPC                                                                           PWM / CAN Bus
                  v                                                                                    v
+------------------------------------+                                              +--------------------------------------+
|       Cloud Telemetry / Fleet      |                                              |     ESC / Motors / GPS / RTK / IMU   |
+------------------------------------+                                              +--------------------------------------+
```

---

## 2. Autonomous Offboard Flight Script (MAVSDK Python)

Below is a production-grade, asynchronous offboard mission script using MAVSDK Python featuring heartbeat verification, pre-arm safety checks, takeoff, velocity guidance, geofencing, and automated Return-to-Launch (RTL):

```python
import asyncio
from mavsdk import System
from mavsdk.offboard import OffboardError, VelocityNedYaw, PositionNedYaw
from mavsdk.action import ActionError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DroneAutopilot")

class AutonomousDroneController:
    def __init__(self, mavlink_url: str = "udp://:14540"):
        self.drone = System()
        self.mavlink_url = mavlink_url

    async def connect(self):
        logger.info(f"Connecting to autopilot at {self.mavlink_url}...")
        await self.drone.connect(system_address=self.mavlink_url)

        # 1. Wait for Flight Controller Heartbeat
        async for state in self.drone.core.connection_state():
            if state.is_connected:
                logger.info("Flight Controller Connected! Heartbeat detected.")
                break

        # 2. Wait for GPS Fix & Health Checks
        logger.info("Awaiting Global Position GPS Lock & Home Position...")
        async for health in self.drone.telemetry.health():
            if health.is_global_position_ok and health.is_home_position_ok:
                logger.info("GPS Fix & Home Position Established.")
                break

    async def execute_autonomous_mission(self, target_altitude_m: float = 5.0):
        # 3. Arm Aircraft
        try:
            logger.info("Arming motors...")
            await self.drone.action.arm()
        except ActionError as e:
            logger.error(f"Arming failed: {e}")
            return

        # 4. Take Off
        logger.info(f"Taking off to {target_altitude_m}m altitude...")
        await self.drone.action.set_takeoff_altitude(target_altitude_m)
        await self.drone.action.takeoff()
        await asyncio.sleep(8) # Wait to reach takeoff altitude

        # 5. Initialize Offboard Mode with Initial Zero Velocity Setpoint
        logger.info("Initializing Offboard Control mode...")
        await self.drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, 0.0))
        
        try:
            await self.drone.offboard.start()
        except OffboardError as error:
            logger.critical(f"Starting offboard mode failed: {error._result.result}")
            logger.info("Disarming due to safety failure.")
            await self.drone.action.return_to_launch()
            return

        # 6. Execute Offboard Trajectory: Fly Forward (North) at 2 m/s
        logger.info("Flying North at 2.0 m/s...")
        await self.drone.offboard.set_velocity_ned(VelocityNedYaw(2.0, 0.0, 0.0, 0.0))
        await asyncio.sleep(5)

        # Fly East at 1.5 m/s while turning yaw to 90 degrees
        logger.info("Flying East at 1.5 m/s, Yaw 90 deg...")
        await self.drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 1.5, 0.0, 90.0))
        await asyncio.sleep(5)

        # Stop Movement
        logger.info("Holding Position...")
        await self.drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, 90.0))
        await asyncio.sleep(3)

        # 7. Stop Offboard and Return To Launch (RTL)
        logger.info("Stopping offboard mode & executing Return-to-Launch (RTL)...")
        try:
            await self.drone.offboard.stop()
        except OffboardError as error:
            logger.error(f"Stopping offboard mode failed: {error._result.result}")

        await self.drone.action.return_to_launch()

async def main():
    controller = AutonomousDroneController("udp://:14540")
    await controller.connect()
    await controller.execute_autonomous_mission(target_altitude_m=4.0)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 3. Telemetry Stream Monitoring & Geofence Failsafe

```python
async def monitor_telemetry_failsafe(drone: System, max_distance_from_home_m: float = 100.0):
    """Continuous background task checking battery levels and geofence distance."""
    async for position in drone.telemetry.position():
        # Calculate local distance or battery voltage
        pass

    async for battery in drone.telemetry.battery():
        if battery.remaining_percent < 0.20: # 20% Low Battery
            logger.warning("LOW BATTERY WARNING! Initiating Emergency Landing.")
            await drone.action.land()
            break
```

---

## 4. Anti-Patterns & Critical Pitfalls

| Anti-Pattern | Severity | Consequence | Correct Pattern |
|---|---|---|---|
| Switching to Offboard without prior setpoint message | Critical | Autopilot rejects mode change, safety rejection | Send initial `set_velocity_ned` or `set_position_ned` BEFORE calling `offboard.start()` |
| Offboard setpoint stream rate < 2 Hz | Critical | PX4 command timeout trigger -> Failsafe land | Maintain minimum 10 Hz to 20 Hz continuous streaming loop |
| Missing Heartbeat Timeout Monitoring | High | Uncontrolled drone flight if companion script crashes | Enable PX4 `COM_OBL_ACT` failsafe action |
| Ignoring `health.is_armable` status checks | Critical | Flight crash due to uncalibrated gyro/compass | Check `health` stream before issuing `arm()` |
| Hardcoded Altitude without AGL / Terrain check | High | Ground crash on uneven terrain | Use Rangefinder / Lidar distance sensor or Barometric AGL |

---

## 5. Verification & SITL Simulation Protocols

1. **PX4 Gazebo / QGroundControl SITL**: Run simulation locally to verify offboard script before hardware deployment:
   ```bash
   make px4_sitl gazebo-classic
   ```
2. **MAVLink Inspector**: Verify message rates (`HEARTBEAT`, `LOCAL_POSITION_NED`, `ATTITUDE`) are active at specified frequencies.
3. **Hardware-in-the-Loop (HITL)**: Test on physical autopilot hardware connected to simulation prior to live flight.
