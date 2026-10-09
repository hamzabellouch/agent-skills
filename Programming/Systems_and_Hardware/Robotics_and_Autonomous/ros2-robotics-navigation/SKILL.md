---
name: ros2-robotics-navigation
metadata:
  category: Autonomous Systems and Robotics
description: Best practices for building autonomous robotics software using ROS 2 (Humble/Jazzy) and Nav2. Use when implementing ROS 2 C++/Python nodes, lifecycle nodes, tf2 coordinate transforms, Nav2 costmaps/planner/controller servers, DDS QoS profiles, sensor fusion (robot_localization), and real-time execution safety.
compatibility: ROS 2 Humble/Jazzy, Ubuntu 22.04/24.04, C++17, Python 3.10+, Nav2
---

# ROS 2 Robotics & Nav2 Autonomous Navigation Guidelines

This skill details node design, DDS Quality of Service (QoS) tuning, coordinate transformation frame trees (`tf2`), Nav2 architecture configuration, and real-time execution safety for ROS 2 autonomous mobile robots (AMR).

---

## 1. ROS 2 Architecture & Node Design

### 1.1 Lifecycle Node Management (C++)

Managed Lifecycle Nodes transition explicitly through states (`Unconfigured`, `Inactive`, `Active`, `Finalized`), ensuring hardware drivers and controllers initialize predictably:

```cpp
#include "rclcpp/rclcpp.hpp"
#include "rclcpp_lifecycle/lifecycle_node.hpp"
#include "sensor_msgs/msg/laser_scan.hpp"
#include "nav_msgs/msg/odometry.hpp"

using CallbackReturn = rclcpp_lifecycle::node_interfaces::LifecycleNodeInterface::CallbackReturn;

class AutonomousSafetyNode : public rclcpp_lifecycle::LifecycleNode {
public:
  explicit AutonomousSafetyNode(const rclcpp::NodeOptions & options)
  : rclcpp_lifecycle::LifecycleNode("safety_monitor_node", options) {}

  CallbackReturn on_configure(const rclcpp_lifecycle::State &) override {
    RCLCPP_INFO(get_logger(), "Configuring Safety Monitor Node...");
    
    // Configure QoS for High Frequency Sensor Data
    rclcpp::QoS sensor_qos(rclcpp::KeepLast(5));
    sensor_qos.reliability(RCLCPP_RELIABILITY_BEST_EFFORT);
    sensor_qos.durability(RCLCPP_DURABILITY_VOLATILE);

    scan_sub_ = create_subscription<sensor_msgs::msg::LaserScan>(
      "/scan", sensor_qos,
      std::bind(&AutonomousSafetyNode::scan_callback, this, std::placeholders::_1));

    cmd_vel_pub_ = create_publisher<geometry_msgs::msg::Twist>("/cmd_vel", rclcpp::SystemDefaultsQoS());

    return CallbackReturn::SUCCESS;
  }

  CallbackReturn on_activate(const rclcpp_lifecycle::State & state) override {
    LifecycleNode::on_activate(state);
    cmd_vel_pub_->on_activate();
    RCLCPP_INFO(get_logger(), "Safety Monitor Activated.");
    return CallbackReturn::SUCCESS;
  }

  CallbackReturn on_deactivate(const rclcpp_lifecycle::State & state) override {
    LifecycleNode::on_deactivate(state);
    cmd_vel_pub_->on_deactivate();
    RCLCPP_INFO(get_logger(), "Safety Monitor Deactivated.");
    return CallbackReturn::SUCCESS;
  }

private:
  void scan_callback(const sensor_msgs::msg::LaserScan::SharedPtr msg) {
    if (!get_current_state().label().compare("active")) {
      // Emergency Brake logic if obstacle closer than threshold
      for (const auto & range : msg->ranges) {
        if (range < 0.35f && range > msg->range_min) {
          RCLCPP_WARN(get_logger(), "EMERGENCY STOP TRIGGERED! Obstacle detected at %.2fm", range);
          auto stop_msg = std::make_unique<geometry_msgs::msg::Twist>();
          stop_msg->linear.x = 0.0;
          stop_msg->angular.z = 0.0;
          cmd_vel_pub_->publish(std::move(stop_msg));
          break;
        }
      }
    }
  }

  rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr scan_sub_;
  rclcpp_lifecycle::LifecyclePublisher<geometry_msgs::msg::Twist>::SharedPtr cmd_vel_pub_;
};
```

---

## 2. Coordinate Transforms & TF2 Tree Conventions

Robot spatial transforms MUST adhere to REP-105 standards:

```
    map  (Global Fixed Frame - SLAM / GPS)
     |
     v  (Provided by AMCL / SLAM Node)
    odom (Locally Continuous Frame - Wheel Encoders / Visual Odometry)
     |
     v  (Provided by EKF / Odometry Driver)
 base_link (Robot Center of Mass)
     |
     +--> sensor_laser (LiDAR Transform Offset)
     +--> camera_link   (Depth Camera Offset)
```

### 2.1 Publishing Static Sensor Transform (`tf2_ros`)
```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TransformStamped
from tf2_ros import StaticTransformBroadcaster

class StaticSensorPublisher(Node):
    def __init__(self):
        super().__init__('static_tf_publisher')
        self.tf_broadcaster = StaticTransformBroadcaster(self)
        self.publish_sensor_tf()

    def publish_sensor_tf(self):
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'base_link'
        t.child_frame_id = 'laser_frame'

        t.transform.translation.x = 0.20 # 20cm forward
        t.transform.translation.y = 0.0
        t.transform.translation.z = 0.15 # 15cm above base

        # Quaternion zero rotation
        t.transform.rotation.w = 1.0
        self.tf_broadcaster.sendTransform(t)
```

---

## 3. Nav2 Navigation Architecture & Configuration

Nav2 utilizes Behavior Trees (`BT Navigator`) to coordinate planning and recovery:

```
[ Nav2 Goal ] ---> [ Planner Server ] ---> Global Path (NavFn / Smac)
                         |
                         v
                  [ Controller Server ] ---> Velocity Command /cmd_vel (Regulated Pure Pursuit / DWB)
                         |
                   (Obstacle Hit?)
                         |
                         +---> [ Recovery Server ] (Spin / Backup / Wait)
```

### 3.1 Nav2 Controller Configuration Snippet (`nav2_params.yaml`)

```yaml
controller_server:
  ros__parameters:
    use_sim_time: True
    controller_frequency: 20.0
    min_x_velocity_threshold: 0.001
    min_y_velocity_threshold: 0.5
    min_theta_velocity_threshold: 0.001
    progress_checker_plugin: "progress_checker"
    goal_checker_plugins: ["general_goal_checker"]
    controller_plugins: ["FollowPath"]

    FollowPath:
      plugin: "nav2_regulated_pure_pursuit_controller::RegulatedPurePursuitController"
      desired_linear_vel: 0.5
      lookahead_dist: 0.6
      min_lookahead_dist: 0.3
      max_lookahead_dist: 0.9
      use_velocity_scaled_lookahead_dist: true
      transform_tolerance: 0.2
      use_collision_detection: true
      max_robot_pose_search_dist: 10.0
```

---

## 4. Anti-Patterns & Critical Pitfalls

| Anti-Pattern | Severity | Consequence | Correct Pattern |
|---|---|---|---|
| Incompatible DDS QoS (Reliable Publisher vs Best Effort Sub) | Critical | Silence on subscriber topic, missing data | Match QoS settings (e.g. `sensor_qos` for high-frequency LiDAR) |
| Missing TF extrapolation bounds handling | High | `LookupTransform` throws `tf2::ExtrapolationException` | Use `tf2::TimePointZero` or handle `LookupException` try/catch |
| Blocking ROS callback routines | Critical | Thread starvation, missed safety checks, heartbeat drop | Offload processing to MultiThreadedExecutor / Async callbacks |
| Dynamic allocation inside real-time control loop | High | Nondeterministic thread latency | Preallocate vectors, use static arrays in control loops |
| Non-REP-105 Frame hierarchy | High | AMCL localization jumps, Nav2 costmap distortion | Enforce strict `map -> odom -> base_link -> sensor` transform chain |

---

## 5. Real-Time Performance & DDS Tuning

1. **DDS Middleware Choice**: Use `rmw_cyclonedds_cpp` or `rmw_fastrtps_cpp` configured via environment variable:
   ```bash
   export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
   ```
2. **Multi-Threaded Executor**:
   ```cpp
   rclcpp::executors::MultiThreadedExecutor executor(rclcpp::ExecutorOptions(), 4);
   executor.add_node(node);
   executor.spin();
   ```

---

## 6. Verification Checklist

- [ ] **TF Tree Sanity**: Run `ros2 run tf2_tools view_frames` and confirm valid single-rooted transform tree.
- [ ] **Nav2 Lifecycle**: Verify all Nav2 servers report `active` via `ros2 lifecycle list`.
- [ ] **QoS Topic Alignment**: Run `ros2 topic echo --qos-profile /scan` to verify topic compatibility.
