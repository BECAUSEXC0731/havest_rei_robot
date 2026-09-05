#include "ros/ros.h"
#include <tf/transform_listener.h>
#include <tf/transform_broadcaster.h>
#include "arm_controller/move.h"
#include "arm_controller/control.h"
#include "arm_controller/PickPlace.h"

#include <stdio.h>
#include <stdlib.h>
#include <string>
#include <math.h>       /* tan */

using namespace std;

#define CAMREA_X_MAX 200
#define CAMREA_Y_MAX 0
#define CAMREA_Z_MAX 170

class EYE_Cal
{
public:
    EYE_Cal();

    ros::NodeHandle n,nh;
	ros::Subscriber sub;		
    tf::TransformListener listener;
    tf::TransformBroadcaster robot_broadcaster;
    ros::ServiceClient client_goto;
    ros::Time current_time, last_time;
    void eye_calibration(void);
    void position_callback(const arm_controller::control& msg);

    float position[4];
private:
    /* data */
    boost::thread m_ikthread;

};

//pos_info回调函数
void EYE_Cal::position_callback(const arm_controller::control& msg)
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

float Target[3][3] = {270.0,0.0,5.0, 180.0,180.0,5.0, 180.0,-180.0,5.0 };
float actual[3][3] = {0};
void EYE_Cal::eye_calibration(void){
    for (size_t i = 0; i < 3; i++)
    {
        cout << "按任意键继续 !" <<endl;
        //ROS_INFO("按任意键继续!");
        getchar();

        arm_controller::move pos;
        //走到摄像头固定位置-盒子的上方
        pos.request.pose.position.x=Target[i][0] ;
        pos.request.pose.position.y=Target[i][1] ;
        pos.request.pose.position.z=Target[i][2] ;
        if (!client_goto.call(pos))
        {
            ROS_INFO("error !");
            break;
        }else{
            sleep(1);
            ROS_INFO("请将物块放置于机械臂下,放好后按任意键继续!");
            getchar();
        }

        //走到摄像头固定位置-盒子的上方
        pos.request.pose.position.x=CAMREA_X_MAX;
        pos.request.pose.position.y=CAMREA_Y_MAX;
        pos.request.pose.position.z=CAMREA_Z_MAX;
        if (!client_goto.call(pos))
        {
            ROS_INFO("error !");
            break;
        }
        sleep(1);

        //走到摄像头固定位置-盒子的上方
        pos.request.pose.position.x=CAMREA_X_MAX;
        pos.request.pose.position.y=CAMREA_Y_MAX;
        pos.request.pose.position.z=CAMREA_Z_MAX;
        if (!client_goto.call(pos))
        {
            ROS_INFO("error !");
            break;
        }
        sleep(3);

        //监听tf
        tf::StampedTransform transform;
        try
        {
            listener.waitForTransform("/robot","/ar_marker_4", ros::Time(0), ros::Duration(3.0));
            listener.lookupTransform("/robot","/ar_marker_4", ros::Time(0), transform);
        }
        catch (tf::TransformException &ex) 
        {
            ROS_ERROR("TF may have some problems.\n %s",ex.what());
            ros::Duration(1.0).sleep();
            ROS_INFO("error !");
            break;
        }
        actual[i][0] =transform.getOrigin().x()*1000.0;
        actual[i][1] =transform.getOrigin().y()*1000.0;
        actual[i][2] =transform.getOrigin().z()*1000.0;
    }
    for (size_t i = 0; i < 3; i++)
    {
        cout << Target[i][0] << "   " << Target[i][1] << "   " << Target[i][2] << endl;
        cout << actual[i][0] << "   " << actual[i][1] << " " << actual[i][2] << endl;
    }
}


EYE_Cal::EYE_Cal()
{
    client_goto=n.serviceClient<arm_controller::move>("goto_position");

    sub = n.subscribe("arm_controller/position_info",100,&EYE_Cal::position_callback,this);
    m_ikthread = boost::thread(boost::bind(&EYE_Cal::eye_calibration, this));
}

int main(int argc,char** argv)
{
    //节点初始化
    ros::init(argc,argv,"robot_pick");
    //实例化类EYE_Cal
    EYE_Cal eye_cal;
    //多线程接收
    ros::AsyncSpinner spinner(2); 
    spinner.start();
    ros::waitForShutdown();
    return 0;
}

