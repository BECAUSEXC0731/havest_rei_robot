/*
 * @Author: Zhaoq 1327153842@qq.com
 * @Date: 2022-09-08 11:30:39
 * @LastEditors: Zhaoq 1327153842@qq.com
 * @LastEditTime: 2023-04-26 09:39:19
 * @Gitee: https://gitee.com/REINOVO
 * Copyright (c) 2022 by 深圳市元创兴科技, All Rights Reserved. 
 * @Description: 机器人运动学解算
 */
#ifndef _REINOVO_KINEMATICS_BASE_H
#define _REINOVO_KINEMATICS_BASE_H

#include <iostream>
#include <string>
#include <vector>
#include <complex>
#include <eigen3/Eigen/Dense>
#include <memory>
const float PI = 3.1415926f;



namespace reinovo_base
{
/**
 * @brief 结构体 底盘运动参数
 * @param car_mode 底盘运动模型 
 * @param wheel_separation_x x方向轮间距 
 * @param wheel_separation_y y方向轮间距
 * @param wheel_radius 主动轮半径
 * @param motors_index 电机索引(数组第一位底盘右上电机序号，逆时针填入)
 * @param sign 左转时电机转向正负号(按电机序号顺序填入))
 * 
 */

struct KinematicData
{
    int car_mode = 0;
    float wheel_separation_x = 0.5f;//x方向轮间距
    float wheel_separation_y = 0.5f;//y方向轮间距
    float wheel_radius = 0.25f;
    std::vector<int> motors_index= {0, 1, 2, 3};
    std::vector<float> signs = {-1.0, -1.0, -1.0, -1.0};
};
class BaseKin{
public:
    BaseKin(KinematicData kin_data):kin_data_(kin_data), passerby_var_(0.0f){
        vel2rpm_ = 60.0f*0.5f*M_1_PI/kin_data_.wheel_radius;
        rpm2vel_ = 2.0f*PI/60.0f*kin_data_.wheel_radius;
    };
    virtual Eigen::Vector3f ForwardKinematics(const Eigen::VectorXf &motor_speed)=0;
    virtual Eigen::VectorXf InverseKinematics(const Eigen::Vector3f &vel)=0;
protected:
    KinematicData kin_data_;
    float vel2rpm_, rpm2vel_, passerby_var_;
};
}

#endif