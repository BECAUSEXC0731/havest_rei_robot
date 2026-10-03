/* 
 * Software License Agreement (BSD License)
 * Copyright (c) 2020, reinovo, Inc.
 * All rights reserved.
 * Author: LN  <825255961@qq.com>	   
 */

#include <string>
#include <vector>
#include <sstream>
#include <cmath>
#include <cstdlib>//string转化为double
#include <iomanip>//保留有效小数
#include "unistd.h"

#include <geometry_msgs/Twist.h>
#include <tf/transform_broadcaster.h>

#include <ros/ros.h>
#include <serial/serial.h>
#include <std_msgs/String.h>
#include <std_srvs/SetBool.h>
#include "arm_controller/move.h"
#include "arm_controller/control.h"
using namespace std;


class ARM_CONTROL
{
public:
    ARM_CONTROL();
//    virtual ~ARM_CONTROL();

    //获取位置
    bool get_pos();
    //移动到目标点
    bool goto_pos(float gx,float gy,float gz);
    //goto回调函数
    bool goto_position_deal(arm_controller::move::Request &req,
                            arm_controller::move::Response &res);
    //吸盘控制
    bool pump_callback(std_srvs::SetBool::Request &req,std_srvs::SetBool::Response &res);
    //解锁电机
    bool unlcok_callback(std_srvs::SetBool::Request &req,std_srvs::SetBool::Response &res);
	//手臂定向移动
    void cmd_callback(const geometry_msgs::Twist& msg);
private:
	ros::NodeHandle nh;
    std::string read_data;
    serial::Serial _serial;				// serial object
    arm_controller::control pos;
	ros::Subscriber sub;		
	ros::Publisher pub;
	ros::ServiceServer goto_position_server,pick_server,unlock_server;
    bool unlcok_aign;
    //tf广播器
    tf::TransformBroadcaster robot_broadcaster;

};

void ARM_CONTROL::cmd_callback(const geometry_msgs::Twist& msg)
{
	std::string Gcode = "";
	//float转字符
	char x[10];
	char y[10];
	char z[10];

	sprintf(x, "%.2f", msg.linear.x);
	sprintf(y, "%.2f", msg.linear.y);
	sprintf(z, "%.2f", msg.linear.z);
	Gcode = (std::string)"G2204 X" + x + " Y" + y + " Z" + z + " F1000" "\n";
	ROS_INFO("%s", Gcode.c_str());
	//将移动数据发送到串口
	_serial.write(Gcode.c_str());
}


//获取位姿
bool ARM_CONTROL::get_pos()
{
	// //向串口发送P2220获取位姿
	std::string Gcode = "",	data="";
	// Gcode = (std::string)"P2220" + "\r\n";
	// _serial.write(Gcode.c_str());
	//读取串口返回消息
	data = _serial.read(_serial.available());
	//std::cout << data << endl;

	//分割返回数据
    std::vector<std::string> v;
    std::string::size_type pos1, pos2, pos3;
    pos1 = data.find("X");
    pos2 = data.find("Y");
    pos3 = data.find("Z");

	v.push_back(data.substr(pos1+1,pos2-pos1));	//X
	v.push_back(data.substr(pos2+1,pos3-pos2));	//Y
	v.push_back(data.substr(pos3+1,data.length()-pos3-1));	//Z

	//赋值
	pos.position.x	=	std::atof(v[0].c_str());
	pos.position.y	=	std::atof(v[1].c_str());
	pos.position.z	=	std::atof(v[2].c_str());

	if (pos.position.x < 0.1 && pos.position.y < 0.1 && pos.position.z < 0.1)
		return false;
	else{
		//发布话题 arm_controller/position_info
		pub.publish(pos);
        geometry_msgs::Quaternion robot_quat = tf::createQuaternionMsgFromYaw(atan2(pos.position.y,pos.position.x));
        geometry_msgs::TransformStamped robot_trans;
        robot_trans.header.stamp = ros::Time::now();
        robot_trans.header.frame_id = "robot";
        robot_trans.child_frame_id = "end";

        robot_trans.transform.translation.x = pos.position.x/1000;
        robot_trans.transform.translation.y = pos.position.y/1000;
        robot_trans.transform.translation.z = pos.position.z/1000;
        robot_trans.transform.rotation = robot_quat;
        robot_broadcaster.sendTransform(robot_trans);
		return true;
	}
}

//goto pos
bool ARM_CONTROL::goto_pos(float gx,float gy,float gz)
{
	std::string Gcode = "";
	string result;
	ros::Rate loop_rate(20);

	_serial.read(_serial.available());

	//float转字符
	char x[10];
	char y[10];
	char z[10];

	sprintf(x, "%.2f", gx);
	sprintf(y, "%.2f", gy);
	sprintf(z, "%.2f", gz);
	Gcode = (std::string)"M2222 X" + x + " Y" + y + " Z" + z + " P0\n";
	ROS_INFO("发送数据 : %s", Gcode.c_str());
	//将移动数据发送到串口
	_serial.write(Gcode.c_str());
	//延时100ms
	usleep(50*1000);
	//读取返回
	result = _serial.read(_serial.available());

	cout << result << endl;

	if (result.find("V0") < 100){				//如果该点不在工作范围内
		return false;
	}else if (result.find("V1") < 100){			//如果该点在工作范围内
		Gcode = (std::string)"G0 X" + x + " Y" + y + " Z" + z + " F10000" + "\n";
		ROS_INFO("%s", Gcode.c_str());
		_serial.write(Gcode.c_str());
		usleep(100*1000);
		result = _serial.read(_serial.available());
		if (result.find("E26") < 100)			//如果目标点可以达到而直线插补不到
		{
			//先将其运动到中间点200,0,100
			char x1[10];
			char y1[10];
			char z1[10];
			sprintf(x1, "%.2f", 200.0);
			sprintf(y1, "%.2f", 0.0);
			sprintf(z1, "%.2f", 100.0);
			Gcode = (std::string)"G0 X" + x1 + " Y" + y1 + " Z" + z1 + " F10000" + "\r\n";
			ROS_INFO("%s", Gcode.c_str());
			_serial.write(Gcode.c_str());
			result = _serial.read(_serial.available());
			int i=0;
			while (!(abs(pos.position.x-200.0)<1&&abs(pos.position.y-0.0)<1&&abs(pos.position.z-100.0)<1))
			{
				get_pos();
				loop_rate.sleep();
				i++;
				if(i>200)return false;
			}
			//然后再运动到目标点
			Gcode = (std::string)"G0 X" + x + " Y" + y + " Z" + z + " F10000" + "\n";
			_serial.write(Gcode.c_str());
			result = _serial.read(_serial.available());
		}
		//等待移动完成
		int i=0;
		while (!(abs(pos.position.x-gx)<1&&abs(pos.position.y-gy)<1&&abs(pos.position.z-gz)<1))
		{
			/* code for loop body */
			get_pos();
			loop_rate.sleep();
			i++;
			// result = _serial.read(_serial.available());
			// if (result.find("@6") < 100&& result.find("V1")){
			// 	return true;
			// }
			if(i>200)
				return false;
		}
		return true;		
	}else{
		return false;
	}
}

//goto pos 回调函数
bool ARM_CONTROL::goto_position_deal(arm_controller::move::Request &req,
						arm_controller::move::Response &res)
{
	//调用goto 函数
    _serial.write("M2122\r\n");		//停止反馈
	res.success=goto_pos(req.pose.position.x,req.pose.position.y,req.pose.position.z);
    _serial.write("M2120 V0.1\r\n");		// report position per 0.05s
	return true;
}

//气泵回调函数
bool ARM_CONTROL::pump_callback(std_srvs::SetBool::Request &req,std_srvs::SetBool::Response &res)
{
    std::string Gcode = "";
    if (req.data == true)
    {
        //打开气泵指令M2231 V1
        Gcode = (std::string)"M2231 V1" + "\r\n";
    }else{
        //关闭气泵指令M2231 V1
        Gcode = (std::string)"M2231 V0" + "\r\n";
    }
    ROS_INFO("%s", Gcode.c_str());
    int i = _serial.write(Gcode.c_str());
    res.success=i;
    read_data = _serial.read(_serial.available());
    cout << read_data << endl;
	return true;
}
//解锁上锁电机
bool ARM_CONTROL::unlcok_callback(std_srvs::SetBool::Request &req,std_srvs::SetBool::Response &res)
{
    std::string Gcode = "";
    if (req.data == true)
    {
        //解锁所有电机 V1
        Gcode = (std::string)"M2019" + "\r\n";
    }else{
        //锁住所有电机 V1
        Gcode = (std::string)"M17" + "\r\n";
    }
    ROS_INFO("%s", Gcode.c_str());
    int i = _serial.write(Gcode.c_str());
    res.success=true;

	return true;
}

ARM_CONTROL::ARM_CONTROL()
{
	//服务器 pick
	pick_server = nh.advertiseService("pump",&ARM_CONTROL::pump_callback,this);
	//解锁电机
	unlock_server = nh.advertiseService("unlock",&ARM_CONTROL::unlcok_callback,this);

	//服务器 goto_position
	goto_position_server = nh.advertiseService("goto_position",&ARM_CONTROL::goto_position_deal,this);
	//发布者 arm_controller/position_info 发布机械臂位置信息
	pub = nh.advertise<arm_controller::control>("arm_controller/position_info", 1);

    //接收相对位移
    sub = nh.subscribe("/arm_controller/cmd_vel",2,&ARM_CONTROL::cmd_callback,this);

	//串口连接
	try
	{
		_serial.setPort("/dev/ttyACM0");
		_serial.setBaudrate(115200);
		serial::Timeout to = serial::Timeout::simpleTimeout(1000);
		_serial.setTimeout(to);
		_serial.open();
		ROS_INFO_STREAM("Port has been open successfully");
	}
	catch (serial::IOException& e)
	{
		ROS_ERROR_STREAM("Unable to open port");
		ros::shutdown();
		//return -1;
	}
	if (_serial.isOpen())
	{
		ros::Duration(3.5).sleep();				// wait 3.5s
		_serial.write("M2120 V0\r\n");			// stop report position
		ros::Duration(0.1).sleep();				// wait 0.1s
		_serial.write("M17\r\n");				// attach
		ros::Duration(0.1).sleep();				// wait 0.1s
		ROS_INFO_STREAM("Attach and wait for commands");
	}
    //返回笛卡尔坐标系
    _serial.write("M2120 V0.1\r\n");		// report position per 0.05s


	//10hz
	ros::Rate loop_rate(10);
	//读取初始化信息
	while (ros::ok())
	{
		string read_line;
		_serial.readline(read_line,65535,"\n");
		cout << read_line;
		if (read_line.find("@5 V1") < 1000) break;
		ros::Duration(0.05).sleep();				// wait 0.1s
	}



	//开始主循环
	while (ros::ok())
	{
		//获取机械臂位姿函数
		get_pos();
		//如果机械臂位姿未获取到则不发布消息
		if(abs(pos.position.x)<0.1&&abs(pos.position.y)<0.1&&abs(pos.position.z)<0.1)
		{
			ros::spinOnce();
			loop_rate.sleep();
			continue;
		}
		ros::spinOnce();
		loop_rate.sleep();
	}

}


int main(int argc, char** argv)
{
	ros::init(argc, argv, "arm_controller");
	ARM_CONTROL carm;
	ros::shutdown();

}
