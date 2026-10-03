#include <rei_robot_base/kinematics/mecanum_box_kinematics.h>

namespace reinovo_base {

Eigen::Vector3f MecanumBoxOmniKin::ForwardKinematics(
    const Eigen::VectorXf &motor_speed) {
  const float a = 0.5/passerby_var_;
  Eigen::Vector3f velocity(0.0f, 0.0f, 0.0f);  // vx, vy, vth
  Eigen::Vector4f motor_speed_sequen(
      motor_speed[kin_data_.motors_index[0]] *
          kin_data_.signs[kin_data_.motors_index[0]],
      motor_speed[kin_data_.motors_index[1]] *
          kin_data_.signs[kin_data_.motors_index[1]],
      motor_speed[kin_data_.motors_index[2]] *
          kin_data_.signs[kin_data_.motors_index[2]],
      motor_speed[kin_data_.motors_index[3]] *
          kin_data_.signs[kin_data_.motors_index[3]]);
  Eigen::Matrix<float, 3, 4> mat;
  mat << 0.5, -0.5, 0, 0,
         0, 0.5, -0.5, 0,
         a, 0, a, 0;
  velocity = mat * (rpm2vel_*motor_speed_sequen);
  return velocity;
}
Eigen::VectorXf MecanumBoxOmniKin::InverseKinematics(const Eigen::Vector3f &vel) {
  Eigen::Vector4f motor_speed_sequen(0.0f, 0.0f, 0.0f, 0.0f);
  Eigen::Matrix<float, 4, 3> mat;
  mat << 1.0, 1.0, passerby_var_,
         -1.0, 1.0, passerby_var_,
         -1.0, -1.0, passerby_var_,
         1.0, -1.0, passerby_var_;
  motor_speed_sequen = vel2rpm_ * (mat * vel);
  Eigen::Vector4f motor_speed;
  motor_speed(kin_data_.motors_index[0]) =
      motor_speed_sequen[0] *
      kin_data_.signs[kin_data_.motors_index[0]];
  motor_speed(kin_data_.motors_index[1]) =
      motor_speed_sequen[1] * 
      kin_data_.signs[kin_data_.motors_index[1]];
  motor_speed(kin_data_.motors_index[2]) =
      motor_speed_sequen[2]  *
      kin_data_.signs[kin_data_.motors_index[2]];
  motor_speed(kin_data_.motors_index[3]) =
      motor_speed_sequen[3]  *
      kin_data_.signs[kin_data_.motors_index[3]];
  return motor_speed;
}
}  // namespace reinovo_base
