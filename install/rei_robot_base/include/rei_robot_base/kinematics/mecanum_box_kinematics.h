#pragma once
#include "kinematics.h"
namespace reinovo_base {
class MecanumBoxOmniKin: public BaseKin{
public:
    MecanumBoxOmniKin(KinematicData kin_data):BaseKin(kin_data){
        passerby_var_ = (kin_data.wheel_separation_x + kin_data.wheel_separation_y)*0.5f;
    };
    Eigen::Vector3f ForwardKinematics(const Eigen::VectorXf &motor_speed);
    Eigen::VectorXf InverseKinematics(const Eigen::Vector3f &vel);
};
}  // namespace reinovo_base