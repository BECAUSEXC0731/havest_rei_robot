#include <rei_robot_base/rei_robot_base.h>

namespace reinovo_base {

ReiBaseRos::ReiBaseRos()
    : Node("rei_robot_base_ros2"), kinematics_ptr_(nullptr), soft_estop_(false) {
  max_vel_x_ = 0.0;
  max_vel_y_ = 0.0;
  max_vel_th_ = 0.0;

  odom_x_ = 0.0;
  odom_y_ = 0.0;
  odom_th_ = 0.0;

  publish_odom_ = false;
  publish_tf_ = false;

  robot_type_ = "unknown";

  // 声明参数
  this->declare_parameter("robot", "unknown");
  this->declare_parameter("port", "/dev/fox");
  this->declare_parameter("baudrate", 115200);
  this->declare_parameter("kinematics_mode", 2);
  this->declare_parameter("wheel_radius", 0.04);
  this->declare_parameter("wheel_separation_x", 0.0);
  this->declare_parameter("wheel_separation_y", 0.0);
  this->declare_parameter("motors_index", std::vector<int64_t>{0, 1, 2, 3});
  this->declare_parameter("motors_signs", std::vector<double>{-1.0, -1.0, -1.0, -1.0});
  this->declare_parameter("odom_frame", "odom");
  this->declare_parameter("base_frame", "base_footprint");
  this->declare_parameter("max_vel_x", 0.8);
  this->declare_parameter("max_vel_y", 0.8);
  this->declare_parameter("max_vel_th", 1.5);
  this->declare_parameter("publish_odom", true);
  this->declare_parameter("publish_odom_tf", true);
  this->declare_parameter("range_1_frame_id", "range_right_link");
  this->declare_parameter("range_2_frame_id", "range_left_link");

  RobotBaseCom::GetInstance();

  // 创建发布者
  odom_pub_ = this->create_publisher<nav_msgs::msg::Odometry>("odom", 50);
  car_data_pub_ = this->create_publisher<rei_robot_base::msg::CarData>("car_data", 50);
  range_pubs_.push_back(
      this->create_publisher<sensor_msgs::msg::Range>("range1", 5));
  range_pubs_.push_back(
      this->create_publisher<sensor_msgs::msg::Range>("range2", 5));

  // 创建订阅者
  motor_cmd_sub_ = this->create_subscription<rei_robot_base::msg::MotorCmd>(
      "motor_cmd", 1,
      std::bind(&ReiBaseRos::MotorCmdCallback, this, std::placeholders::_1));

  vel_sub_ = this->create_subscription<geometry_msgs::msg::Twist>(
      "cmd_vel", 1,
      std::bind(&ReiBaseRos::VelCallback, this, std::placeholders::_1));

  // 创建服务端 — 使用 lambda 替代 std::bind 避免 variant 类型推导问题
  set_io_server_ = this->create_service<rei_robot_base::srv::SetIO>(
      "set_io",
      [this](const std::shared_ptr<rei_robot_base::srv::SetIO::Request> req,
             std::shared_ptr<rei_robot_base::srv::SetIO::Response> res) {
        return this->SetIOCallback(req, res);
      });
  set_relay_server_ = this->create_service<std_srvs::srv::SetBool>(
      "set_relay",
      [this](const std::shared_ptr<std_srvs::srv::SetBool::Request> req,
             std::shared_ptr<std_srvs::srv::SetBool::Response> res) {
        return this->SetRelayCallback(req, res);
      });
  extra_motor_server_ = this->create_service<rei_robot_base::srv::Int8>(
      "set_extra_motor",
      [this](const std::shared_ptr<rei_robot_base::srv::Int8::Request> req,
             std::shared_ptr<rei_robot_base::srv::Int8::Response> res) {
        return this->ExtraMotorCallback(req, res);
      });
  set_buzzer_server_ = this->create_service<std_srvs::srv::SetBool>(
      "set_buzzer",
      [this](const std::shared_ptr<std_srvs::srv::SetBool::Request> req,
             std::shared_ptr<std_srvs::srv::SetBool::Response> res) {
        return this->SetBuzzerCallback(req, res);
      });
  reset_odom_server_ = this->create_service<std_srvs::srv::Empty>(
      "reset_odom",
      [this](const std::shared_ptr<std_srvs::srv::Empty::Request> req,
             std::shared_ptr<std_srvs::srv::Empty::Response> res) {
        return this->ResetOdomCallback(req, res);
      });
  base_connect_server_ = this->create_service<std_srvs::srv::SetBool>(
      "base_connect",
      [this](const std::shared_ptr<std_srvs::srv::SetBool::Request> req,
             std::shared_ptr<std_srvs::srv::SetBool::Response> res) {
        return this->BaseConnectCallback(req, res);
      });
}

bool ReiBaseRos::Init() {
  range_frame_.clear();

  // 读取机器人型号
  this->get_parameter("robot", robot_type_);
  std::vector<std::string> existed_robots = {"bobac2", "bobac3", "oryxbot", "fox"};
  bool found = false;
  for (const auto& r : existed_robots) {
    if (robot_type_ == r) {
      found = true;
      break;
    }
  }
  if (!found) {
    RCLCPP_ERROR(this->get_logger(), "未知机器人型号: %s", robot_type_.c_str());
    return false;
  }
  RCLCPP_INFO(this->get_logger(), "机器人型号: %s", robot_type_.c_str());

  // 读取串口参数
  this->get_parameter("port", communicate_params_.port);
  this->get_parameter("baudrate", communicate_params_.baud);
  communicate_params_.parity = 'N';
  communicate_params_.data_bit = 8;
  communicate_params_.stop_bit = 1;
  communicate_params_.slave = 1;

  RobotBaseCom::GetInstance().communicate_params_ = communicate_params_;

  if (ConnectBase() < 0) {
    RCLCPP_ERROR(this->get_logger(), "连接下位机失败");
    return false;
  }

  // 初始化 TF broadcaster
  odom_br_ = std::make_unique<tf2_ros::TransformBroadcaster>(*this);

  // 读取运动学参数
  int kin_mode;
  this->get_parameter("kinematics_mode", kin_mode);
  kin_data_.car_mode = kin_mode;
  RCLCPP_INFO(this->get_logger(), "kinematics_mode = %d", kin_data_.car_mode);

  this->get_parameter("wheel_radius", kin_data_.wheel_radius);
  RCLCPP_INFO(this->get_logger(), "wheel_radius = %g", kin_data_.wheel_radius);

  this->get_parameter("wheel_separation_x", kin_data_.wheel_separation_x);
  RCLCPP_INFO(this->get_logger(), "wheel_separation_x = %g", kin_data_.wheel_separation_x);

  this->get_parameter("wheel_separation_y", kin_data_.wheel_separation_y);
  RCLCPP_INFO(this->get_logger(), "wheel_separation_y = %g", kin_data_.wheel_separation_y);

  // 读取电机索引
  std::vector<int64_t> motors_index;
  this->get_parameter("motors_index", motors_index);
  kin_data_.motors_index.clear();
  for (auto& v : motors_index) {
    kin_data_.motors_index.push_back(static_cast<int>(v));
  }

  // 读取电机方向符号
  std::vector<double> motors_signs;
  this->get_parameter("motors_signs", motors_signs);
  kin_data_.signs.clear();
  for (auto& v : motors_signs) {
    kin_data_.signs.push_back(static_cast<float>(v));
  }

  // 安全打印（motors_index 长度可能 < 4，不能硬编码访问 [3] 会越界）
  std::string motors_index_str;
  for (size_t i = 0; i < kin_data_.motors_index.size(); ++i) {
    motors_index_str += std::to_string(kin_data_.motors_index[i]);
    if (i + 1 < kin_data_.motors_index.size()) motors_index_str += ", ";
  }
  RCLCPP_INFO(this->get_logger(), "motors_index = [%s]", motors_index_str.c_str());

  // 创建运动学实例
  if (kinematics_ptr_ != nullptr) kinematics_ptr_.reset();
  kinematics_ptr_ = BaseKinematicsFactory::CreateBaseKinematics(kin_data_);
  if (kinematics_ptr_ == nullptr) {
    RCLCPP_ERROR(this->get_logger(), "底盘运动模型(%d)不支持", kin_data_.car_mode);
    return false;
  }

  // 超声波传感器 frame_id (仅 bobac 系列)
  if (robot_type_ == "bobac2" || robot_type_ == "bobac3") {
    std::string range_frame_id;
    this->get_parameter("range_1_frame_id", range_frame_id);
    range_frame_.push_back(range_frame_id);
    this->get_parameter("range_2_frame_id", range_frame_id);
    range_frame_.push_back(range_frame_id);
  }

  // 读取里程计相关参数
  this->get_parameter("publish_odom", publish_odom_);
  this->get_parameter("publish_odom_tf", publish_tf_);
  this->get_parameter("odom_frame", odom_frame_);
  this->get_parameter("base_frame", base_frame_);
  this->get_parameter("max_vel_x", max_vel_x_);
  this->get_parameter("max_vel_y", max_vel_y_);
  this->get_parameter("max_vel_th", max_vel_th_);

  return true;
}

int8_t ReiBaseRos::ConnectBase() {
  RobotBaseCom::GetInstance().communicate_params_ = communicate_params_;
  return RobotBaseCom::GetInstance().Connect();
}

void ReiBaseRos::VelLimit(float &vx, float &vy, float &vth) {
  if (vx > max_vel_x_)
    vx = max_vel_x_;
  else if (vx < -max_vel_x_)
    vx = -max_vel_x_;
  if (vy > max_vel_y_)
    vy = max_vel_y_;
  else if (vy < -max_vel_y_)
    vy = -max_vel_y_;
  if (vth > max_vel_th_)
    vth = max_vel_th_;
  else if (vth < -max_vel_th_)
    vth = -max_vel_th_;
}

void ReiBaseRos::MotorCmdCallback(
    const rei_robot_base::msg::MotorCmd::SharedPtr msg) {
  if (soft_estop_) return;
  std::vector<double> motors_speed;
  for (size_t i = 0; i < msg->motor_expect_speed.size(); i++) {
    motors_speed.push_back(msg->motor_expect_speed[i]);
  }
  if (RobotBaseCom::GetInstance().SendSpeed(motors_speed) < 0) {
    RCLCPP_ERROR(this->get_logger(), "发送电机控制指令失败");
  }
}

void ReiBaseRos::VelCallback(const geometry_msgs::msg::Twist::SharedPtr msg) {
  if (soft_estop_) return;
  float vx = msg->linear.x;
  float vy = msg->linear.y;
  float vth = msg->angular.z;
  VelLimit(vx, vy, vth);
  Eigen::Vector3f vel;
  vel << vx, vy, vth;
  Eigen::VectorXf speed = kinematics_ptr_->InverseKinematics(vel);
  std::vector<double> motors_speed;
  for (int i = 0; i < speed.size(); i++) {
    motors_speed.push_back(speed[i]);
  }
  if (RobotBaseCom::GetInstance().SendSpeed(motors_speed) < 0) {
    RCLCPP_ERROR(this->get_logger(), "发送电机控制指令失败");
  }
}

bool ReiBaseRos::SetIOCallback(
    const std::shared_ptr<rei_robot_base::srv::SetIO::Request> req,
    std::shared_ptr<rei_robot_base::srv::SetIO::Response> res) {
  uint16_t data[7];
  if (robot_type_ != "bobac2" && robot_type_ != "fox") {
    if (output_io_.size() == 7) {
      for (size_t i = 0; i < 7; i++) {
        data[i] = output_io_[i];
      }

      if (req->all_on && req->all_off) {
        res->success = false;
        res->message = "could not set all_off and all_on both as true";
      } else {
        if (req->all_on) {
          for (size_t i = 0; i < 7; i++) data[i] = 1;
        } else if (req->all_off) {
          for (size_t i = 0; i < 7; i++) data[i] = 0;
        } else {
          for (size_t i = 0; i < req->io.size(); i++) {
            if (req->io[i] > 7 || req->io[i] < 0) continue;
            if (req->state)
              data[req->io[i]] = 1;
            else
              data[req->io[i]] = 0;
          }
        }
        if (RobotBaseCom::GetInstance().SetIO(data)) {
          res->success = true;
          res->message = "ok";
        } else {
          res->success = false;
          res->message = "get output err";
        }
      }
    } else {
      res->success = false;
      res->message = "set failed";
    }
  } else {
    res->success = false;
    res->message = robot_type_ + " is not support";
  }
  return true;
}

bool ReiBaseRos::SetRelayCallback(
    const std::shared_ptr<std_srvs::srv::SetBool::Request> req,
    std::shared_ptr<std_srvs::srv::SetBool::Response> res) {
  bool state = req->data;
  if (RobotBaseCom::GetInstance().SetRelay(state)) {
    res->success = true;
    res->message = "ok";
  } else {
    res->success = false;
    res->message = "get relay err";
  }
  return true;
}

bool ReiBaseRos::ExtraMotorCallback(
    const std::shared_ptr<rei_robot_base::srv::Int8::Request> req,
    std::shared_ptr<rei_robot_base::srv::Int8::Response> res) {
  int state = req->data;
  if (RobotBaseCom::GetInstance().SetExtraMotor(state)) {
    res->success = true;
    res->message = "ok";
  } else {
    res->success = false;
    res->message = "get extra motor err";
  }
  return true;
}

bool ReiBaseRos::SetBuzzerCallback(
    const std::shared_ptr<std_srvs::srv::SetBool::Request> req,
    std::shared_ptr<std_srvs::srv::SetBool::Response> res) {
  int time = req->data;
  if (RobotBaseCom::GetInstance().SetBuzzer(time)) {
    res->success = true;
    res->message = "ok";
  } else {
    res->success = false;
    res->message = "get buzzer err";
  }
  return true;
}

bool ReiBaseRos::ResetOdomCallback(
    const std::shared_ptr<std_srvs::srv::Empty::Request> req,
    std::shared_ptr<std_srvs::srv::Empty::Response> res) {
  (void)req;
  (void)res;
  odom_x_ = 0.0;
  odom_y_ = 0.0;
  odom_th_ = 0.0;
  last_odom_time_ = this->now();
  return true;
}

bool ReiBaseRos::BaseConnectCallback(
    const std::shared_ptr<std_srvs::srv::SetBool::Request> req,
    std::shared_ptr<std_srvs::srv::SetBool::Response> res) {
  if (req->data) {
    int ret = ConnectBase();
    if (ret < 0) {
      res->success = false;
      res->message = "connect failed";
    } else {
      res->success = true;
      res->message = "ok";
    }
  } else {
    RobotBaseCom::GetInstance().CloseConnect();
    res->success = true;
    res->message = "ok";
  }
  return true;
}

void ReiBaseRos::Run() {
  rclcpp::WallRate loop_rate(50);
  last_odom_time_ = this->now();

  std::vector<double> d_data_v;
  std::vector<float> f_data_v;
  std::vector<int> i_data_v;

  while (rclcpp::ok()) {
    if (RobotBaseCom::GetInstance().ReadData() < 0) {
      RCLCPP_ERROR(this->get_logger(), "读取下位机数据失败");
    } else {
      auto current_time = this->now();
      rei_robot_base::msg::CarData car_data;

      // 读取电机转速
      RobotBaseCom::GetInstance().GetMotorSpeed(d_data_v);
      car_data.motor_speed.assign(d_data_v.begin(), d_data_v.end());

      // 读取超声波
      if (range_frame_.size() > 0) {
        sensor_msgs::msg::Range range_msg;
        if (RobotBaseCom::GetInstance().GetUltraSound(f_data_v) == 0) {
          for (size_t i = 0; i < range_frame_.size(); i++) {
            range_msg.header.stamp = current_time;
            range_msg.header.frame_id = range_frame_[i];
            if (f_data_v[i] < 0)
              range_msg.range = 0;
            else
              range_msg.range = f_data_v[i] / 1000.0f;
            car_data.ultrasound.push_back(range_msg.range);
            range_pubs_[i]->publish(range_msg);
          }
        }
      }

      // 读取电池电压
      float f_data;
      if (RobotBaseCom::GetInstance().GetPower(f_data) == 0) {
        car_data.power_voltage = f_data;
      }

      // 读取充电状态
      int i_data;
      if (RobotBaseCom::GetInstance().GetCharge(i_data) == 0) {
        car_data.is_charge = i_data;
      }

      // 读取输入 IO
      if (RobotBaseCom::GetInstance().GetInputIO(i_data_v) == 0) {
        car_data.input_io[0] = i_data_v[0];
        car_data.input_io[1] = i_data_v[1];
        car_data.input_io[2] = i_data_v[2];
        car_data.input_io[3] = i_data_v[3];
      }

      // 读取烟雾传感器
      if (RobotBaseCom::GetInstance().GetSmoke(i_data) == 0) {
        car_data.smoke = i_data;
      }

      // 读取温度
      if (RobotBaseCom::GetInstance().GetTemperature(f_data) == 0) {
        car_data.tempareture = f_data;
      }

      // 读取湿度
      if (RobotBaseCom::GetInstance().GetRelativeHumidity(f_data) == 0) {
        car_data.relative_humidity = f_data;
      }

      // 读取碰撞/跌落传感器 (仅 bobac2)
      if (robot_type_ == "bobac2") {
        bool bc_flag = false;
        if (RobotBaseCom::GetInstance().GetBumper(i_data_v) == 0) {
          for (size_t i = 0; i < i_data_v.size(); i++) {
            car_data.crash.push_back(i_data_v[i]);
            if (i_data_v[i] == 1) bc_flag = true;
          }
        }
        if (RobotBaseCom::GetInstance().GetCliff(i_data_v) == 0) {
          for (size_t i = 0; i < i_data_v.size(); i++) {
            car_data.cliff.push_back(i_data_v[i]);
            if (i_data_v[i] == 1) bc_flag = true;
          }
        }
        if (bc_flag && (!soft_estop_))
          soft_estop_ = true;
        else if ((!bc_flag) && soft_estop_)
          soft_estop_ = false;
      }

      // 读取继电器
      bool b_data;
      if (RobotBaseCom::GetInstance().GetRelay(b_data) == 0)
        car_data.relay_status = b_data;

      // 读取输出 IO
      if (RobotBaseCom::GetInstance().GetOutputIO(i_data_v) == 0) {
        for (size_t i = 0; i < i_data_v.size(); i++) {
          car_data.output_io[i] = i_data_v[i];
        }
      }

      // ── 里程计计算 ──
      double dt = (current_time - last_odom_time_).seconds();
      last_odom_time_ = current_time;

      Eigen::Vector3f real_vel;
      Eigen::VectorXf motor_speed(car_data.motor_speed.size());
      for (size_t i = 0; i < car_data.motor_speed.size(); i++) {
        motor_speed[i] = car_data.motor_speed[i];
      }
      real_vel = kinematics_ptr_->ForwardKinematics(motor_speed);

      double delta_x =
          (real_vel[0] * cos(odom_th_) - real_vel[1] * sin(odom_th_)) * dt;
      double delta_y =
          (real_vel[0] * sin(odom_th_) + real_vel[1] * cos(odom_th_)) * dt;
      double delta_th = real_vel[2] * dt;

      odom_x_ += delta_x;
      odom_y_ += delta_y;
      odom_th_ += delta_th;

      if (publish_odom_) {
        nav_msgs::msg::Odometry odom;
        odom.header.stamp = current_time;
        odom.header.frame_id = odom_frame_;
        odom.child_frame_id = base_frame_;
        odom.pose.pose.position.x = odom_x_;
        odom.pose.pose.position.y = odom_y_;
        odom.pose.pose.position.z = 0.0;
        odom.pose.pose.orientation.z = sin(odom_th_ / 2);
        odom.pose.pose.orientation.w = cos(odom_th_ / 2);
        odom.twist.twist.linear.x = real_vel[0];
        odom.twist.twist.linear.y = real_vel[1];
        odom.twist.twist.angular.z = real_vel[2];
        odom_pub_->publish(odom);
      }

      if (publish_tf_) {
        geometry_msgs::msg::TransformStamped odom_tf;
        odom_tf.header.stamp = current_time;
        odom_tf.header.frame_id = odom_frame_;
        odom_tf.child_frame_id = base_frame_;
        odom_tf.transform.translation.x = odom_x_;
        odom_tf.transform.translation.y = odom_y_;
        odom_tf.transform.translation.z = 0.0;
        odom_tf.transform.rotation.z = sin(odom_th_ / 2);
        odom_tf.transform.rotation.w = cos(odom_th_ / 2);
        odom_br_->sendTransform(odom_tf);
      }

      car_data_pub_->publish(car_data);
    }

    rclcpp::spin_some(this->shared_from_this());
    loop_rate.sleep();
  }
}

}  // namespace reinovo_base
