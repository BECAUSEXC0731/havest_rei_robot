#include "ros/ros.h"
#include <tf/transform_listener.h>
#include <tf/transform_broadcaster.h>
#include "arm_controller/move.h"
#include "arm_controller/control.h"
#include "arm_controller/PickPlace.h"
#include "arm_controller/number.h"

#include <stdio.h>
#include <stdlib.h>
#include <string>
#include <math.h>       /* tan */

using namespace std;

#define CAMREA_X_MAX 160
#define CAMREA_Y_MAX 0
#define CAMREA_Z_MAX 150

class PickAr
{
public:
    PickAr();

    ros::NodeHandle n;
	ros::ServiceServer pick_server,place_server;
    ros::ServiceClient client_pick,client_goto,client_place,client_number;
	ros::Subscriber sub;		
    tf::TransformListener listener;
    tf::TransformBroadcaster robot_broadcaster;
    ros::Time current_time, last_time;

    float position[4];

    void position_callback(const arm_controller::control& msg);
    bool pick_callback( arm_controller::PickPlace::Request &req,
                        arm_controller::PickPlace::Response &res);
    bool place_callback( arm_controller::move::Request &req,
                        arm_controller::move::Response &res);

private:
    /* data */
};

//pos_info回调函数
void PickAr::position_callback(const arm_controller::control& msg)
{
    //info当前位置
	position[0] = msg.position.x;
	position[1] = msg.position.y;
	position[2] = msg.position.z;
    //ROS_INFO("pos X:  %.3f  Y:  %.3f Z:  %.3f",position[0],position[1],position[2]);

    //发布tf  robot-end
    geometry_msgs::Quaternion robot_quat = tf::createQuaternionMsgFromYaw(atan2(position[1],position[0]));
    current_time = ros::Time::now();
    geometry_msgs::TransformStamped robot_trans;
    robot_trans.header.stamp = current_time;
    robot_trans.header.frame_id = "robot";
    robot_trans.child_frame_id = "end";

    robot_trans.transform.translation.x = position[0]/1000;
    robot_trans.transform.translation.y = position[1]/1000;
    robot_trans.transform.translation.z = position[2]/1000;
    robot_trans.transform.rotation = robot_quat;
    robot_broadcaster.sendTransform(robot_trans);
    //ROS_INFO("X: %.1f  Y: %.1f Z: %.1f",position[0],position[1],position[2]);
}

//pick_ar回调函数
bool PickAr::pick_callback(arm_controller::PickPlace::Request &req,
                        arm_controller::PickPlace::Response &res)
{
    for(int w=0;w<100;w++)
    {
        arm_controller::move pos;

        //走到摄像头固定位置-盒子的上方
        pos.request.pose.position.x=CAMREA_X_MAX;
        pos.request.pose.position.y=CAMREA_Y_MAX;
        pos.request.pose.position.z=CAMREA_Z_MAX;
        if (!client_goto.call(pos))
        {
            res.message=" error !";
            res.success=false;
            return true;
        }
        arm_controller::number number;
        number.request.data = 0;
        if(client_number.call(number))
        {
            if(number.response.success==true){
                pos.request.pose.position.x=number.response.pose[0].position.x;
                pos.request.pose.position.y=number.response.pose[0].position.y;
                pos.request.pose.position.z=number.response.pose[0].position.z+30;
                client_goto.call(pos);
            }
            else
            {
                break;
                res.success=true;
            }
        }
        else
        {
                break;
                res.success=true;
        }

        // 抓取
        arm_controller::move pick;
        pick.request.pose.position.x=number.response.pose[0].position.x;
        pick.request.pose.position.y=number.response.pose[0].position.y;
        pick.request.pose.position.z=number.response.pose[0].position.z;
        if(client_pick.call(pick))
        {
            if(pick.response.success==true)
                res.success=true;
            else
            {
                res.message=" Manipulator unattainable !";
                res.success=false;
            }
        }
        else
        {
            res.success=false;
        }
        sleep(0.4);//延时一段时间不能频繁call/goto服务
        //回到ar码上方
        pos.request.pose.position.x=number.response.pose[0].position.x;
        pos.request.pose.position.y=number.response.pose[0].position.y;
        pos.request.pose.position.z=number.response.pose[0].position.z+50;
        client_goto.call(pos);

        pos.request.pose.position.x=5;
        pos.request.pose.position.y=-180;
        pos.request.pose.position.z=10*w+30;
        client_goto.call(pos);
        //ROS_INFO("gooto end");
        
        //下去放下
        arm_controller::move place;
        place.request.pose.position.x=5;
        place.request.pose.position.y=-180;
        place.request.pose.position.z=10*w+10;
        client_place.call(place);
    }

    return true;	
}

PickAr::PickAr()
{
    pick_server=n.advertiseService("pick_number",&PickAr::pick_callback,this);

    client_pick=n.serviceClient<arm_controller::move>("pick");
    client_place=n.serviceClient<arm_controller::move>("place");
    client_goto=n.serviceClient<arm_controller::move>("goto_position");
    client_number=n.serviceClient<arm_controller::number>("number");

    sub = n.subscribe("arm_controller/position_info",100,&PickAr::position_callback,this);
    current_time = ros::Time::now();
    ROS_INFO("INIT OK");
}

int main(int argc,char** argv)
{
    ros::init(argc,argv,"robot_pick");
    PickAr PickAr;
    ros::AsyncSpinner spinner(2); 
    spinner.start();
    ros::waitForShutdown();
    return 0;
}

