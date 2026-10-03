#pragma once
#include "diff_kinematics.h"
#include "mecanum_box_kinematics.h"
#include "three_omni_kinematics.h"
namespace reinovo_base {
/**
 * @brief 枚举 底盘运动模型
 * @param kNone 无 1
 * @param kDiff 两轮差动底盘 2
 * @param kThreeWheeledOmni 三轮全向轮底盘 3
 * @param kThreeWheeledOmniReverse 三轮全向轮反向底盘 4
 * @param kFourMecanumOmni 四轮麦克纳姆轮底盘(长方形) 5
 */
enum MotionModel {
  kNone = 1,
  kDiff,
  kThreeWheeledOmni,
  kThreeWheeledOmniReverse,
  kMecanumBox
  // kFourWheelSlip,
  // kAckermannSteering
};
class BaseKinematicsFactory {
 public:
  /**
   * @brief Create a Base Kinematics object
   *
   * @param kin_data
   * @return std::shared_ptr<BaseKin>
   */
  static std::shared_ptr<BaseKin> CreateBaseKinematics(KinematicData kin_data) {
    switch (kin_data.car_mode) {
      case MotionModel::kDiff:
        return std::make_shared<DiffKin>(kin_data);
        break;
      case MotionModel::kThreeWheeledOmni:
        return std::make_shared<ThreeWheeledOmniKin>(kin_data);
        break;
      case MotionModel::kThreeWheeledOmniReverse:
        return std::make_shared<ThreeOmniKinematicsReverse>(kin_data);
        break;
      case MotionModel::kMecanumBox:
        return std::make_shared<MecanumBoxOmniKin>(kin_data);
        break;
      default:
        return nullptr;
        break;
    }
  }
};
}  // namespace reinovo_base