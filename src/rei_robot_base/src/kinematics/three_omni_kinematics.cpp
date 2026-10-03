#include <rei_robot_base/kinematics/three_omni_kinematics.h>

namespace reinovo_base {
Eigen::Vector3f ThreeWheeledOmniKin::ForwardKinematics(
    const Eigen::VectorXf &motor_speed) {
  const float a = 1.0f / 3.0f;
  const float b = 1.0f / std::sqrt(3.0f);
  const float c = 1.0f / kin_data_.wheel_separation_x / 3.0f;

  Eigen::Vector3f velocity(0.0f, 0.0f, 0.0f);  // vx, vy, vth
  Eigen::Vector3f motor_speed_sequen(
      motor_speed[kin_data_.motors_index[0]] *
          kin_data_.signs[kin_data_.motors_index[0]],
      motor_speed[kin_data_.motors_index[1]] *
          kin_data_.signs[kin_data_.motors_index[1]],
      motor_speed[kin_data_.motors_index[2]] *
          kin_data_.signs[kin_data_.motors_index[2]]);
  Eigen::Matrix3f mat;
  // 2026-08-26: 与 Inverse 同步反 vy 系数，保持正逆互逆（修复左右平移反）
  mat << b, -b, 0, 
        -a, -a, a * 2.0, 
        c, c, c;
  velocity = mat * (rpm2vel_ * motor_speed_sequen);
  return velocity;
}
Eigen::VectorXf ThreeWheeledOmniKin::InverseKinematics(
    const Eigen::Vector3f &vel) {
  const float a = std::sqrt(3.0f) * 0.5f;
  Eigen::Vector3f motor_speed_sequen(0.0f, 0.0f, 0.0f);
  Eigen::Matrix3f mat;
  // 2026-08-26: 物理左右平移反 → 反 vy 系数（vx/vth 不变，与 Forward 同步保持互逆）
  mat << a, -0.5, kin_data_.wheel_separation_x, 
        -a, -0.5, kin_data_.wheel_separation_x, 
        0.0, 1.0, kin_data_.wheel_separation_x;
  motor_speed_sequen = vel2rpm_ * (mat * vel);
  Eigen::Vector3f motor_speed;
  motor_speed(kin_data_.motors_index[0]) =
      motor_speed_sequen[0] * kin_data_.signs[kin_data_.motors_index[0]];
  motor_speed(kin_data_.motors_index[1]) =
      motor_speed_sequen[1] * kin_data_.signs[kin_data_.motors_index[1]];
  motor_speed(kin_data_.motors_index[2]) =
      motor_speed_sequen[2] * kin_data_.signs[kin_data_.motors_index[2]];
  return motor_speed;
}

Eigen::Vector3f ThreeOmniKinematicsReverse::ForwardKinematics(
    const Eigen::VectorXf &motor_speed) {
  const float a = 1.0f / 3.0f;
  const float b = 1.0f / std::sqrt(3.0f);
  const float c = 1.0f / kin_data_.wheel_separation_x / 3.0f;

  Eigen::Vector3f velocity(0.0f, 0.0f, 0.0f);  // vx, vy, vth
  Eigen::Vector3f motor_speed_sequen(
      motor_speed[kin_data_.motors_index[0]] *
          kin_data_.signs[kin_data_.motors_index[0]],
      motor_speed[kin_data_.motors_index[1]] *
          kin_data_.signs[kin_data_.motors_index[1]],
      motor_speed[kin_data_.motors_index[2]] *
          kin_data_.signs[kin_data_.motors_index[2]]);
  Eigen::Matrix3f mat;
  mat << b, 0, -b,
        -a, a * 2.0, -a, 
        c, c, c;
  velocity = mat * (rpm2vel_ * motor_speed_sequen);
  return velocity;
}
Eigen::VectorXf ThreeOmniKinematicsReverse::InverseKinematics(
    const Eigen::Vector3f &vel) {
  const float a = std::sqrt(3.0f) * 0.5f;
  Eigen::Vector3f motor_speed_sequen(0.0f, 0.0f, 0.0f);
  Eigen::Matrix3f mat;
  mat << a, -0.5, kin_data_.wheel_separation_x,
  	    0.0, 1.0, kin_data_.wheel_separation_x, 
        -a, -0.5, kin_data_.wheel_separation_x;
  motor_speed_sequen = vel2rpm_ * (mat * vel);
  Eigen::Vector3f motor_speed;
  motor_speed(kin_data_.motors_index[0]) =
      motor_speed_sequen[0] * kin_data_.signs[kin_data_.motors_index[0]];
  motor_speed(kin_data_.motors_index[1]) =
      motor_speed_sequen[1] * kin_data_.signs[kin_data_.motors_index[1]];
  motor_speed(kin_data_.motors_index[2]) =
      motor_speed_sequen[2] * kin_data_.signs[kin_data_.motors_index[2]];
  return motor_speed;
}

}  // namespace reinovo_base
