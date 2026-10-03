#pragma once
#include "kinematics.h"
namespace reinovo_base {
class DiffKin : public BaseKin {
 public:
  DiffKin(KinematicData kin_data) : BaseKin(kin_data) {
    passerby_var_ = 1.0 / kin_data_.wheel_separation_y;
  };
  Eigen::Vector3f ForwardKinematics(const Eigen::VectorXf &motor_speed);
  Eigen::VectorXf InverseKinematics(const Eigen::Vector3f &vel);
};
}  // namespace reinovo_base