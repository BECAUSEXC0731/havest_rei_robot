#include <rei_robot_base/kinematics/diff_kinematics.h>

namespace reinovo_base {

Eigen::Vector3f DiffKin::ForwardKinematics(const Eigen::VectorXf &motor_speed) {
  Eigen::Vector3f velocity(0.0f, 0.0f, 0.0f);  // vx, vy, vth
  Eigen::Vector2f motor_speed_sequen(
      motor_speed[kin_data_.motors_index[0]] *
          kin_data_.signs[kin_data_.motors_index[0]],
      motor_speed[kin_data_.motors_index[1]] *
          kin_data_.signs[kin_data_.motors_index[1]]);
  Eigen::Matrix<float, 3, 2> mat;
  mat << 0.5, -0.5, 0.0, 0.0, passerby_var_, passerby_var_;
  velocity = mat * (rpm2vel_*motor_speed_sequen);
  return velocity;
}
Eigen::VectorXf DiffKin::InverseKinematics(const Eigen::Vector3f &vel) {
  Eigen::Vector2f motor_speed_sequen(0.0f, 0.0f);

  Eigen::Matrix<float, 2, 3> mat;
  mat << 1.0, 0.0, kin_data_.wheel_separation_y * 0.5, -1.0, 0.0,
      kin_data_.wheel_separation_y * 0.5;
  motor_speed_sequen = vel2rpm_ * (mat * vel);
  Eigen::Vector2f motor_speed;
  motor_speed(kin_data_.motors_index[0]) =
      motor_speed_sequen[0] *
      kin_data_.signs[kin_data_.motors_index[0]];
  motor_speed(kin_data_.motors_index[1]) =
      motor_speed_sequen[1]  *
      kin_data_.signs[kin_data_.motors_index[0]];
  return motor_speed;
}
}  // namespace reinovo_base
