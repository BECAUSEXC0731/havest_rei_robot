#pragma once
#include "kinematics.h"
namespace reinovo_base {
class ThreeWheeledOmniKin: public BaseKin{
public:
    ThreeWheeledOmniKin(KinematicData kin_data):BaseKin(kin_data){};
    Eigen::Vector3f ForwardKinematics(const Eigen::VectorXf &motor_speed);
    Eigen::VectorXf InverseKinematics(const Eigen::Vector3f &vel);
};
class ThreeOmniKinematicsReverse: public BaseKin{
public:
    ThreeOmniKinematicsReverse(KinematicData kin_data):BaseKin(kin_data){};
    Eigen::Vector3f ForwardKinematics(const Eigen::VectorXf &motor_speed);
    Eigen::VectorXf InverseKinematics(const Eigen::Vector3f &vel);
};
}  // namespace reinovo_base