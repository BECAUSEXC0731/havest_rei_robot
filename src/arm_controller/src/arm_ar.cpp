#include "ros/ros.h"
#include <tf/transform_listener.h>
#include "arm_controller/move.h"
#include "arm_controller/control.h"
#include "arm_controller/PickPlace.h"

#include <stdio.h>
#include <stdlib.h>
#include <string>
#include <math.h>       /* tan */

using namespace std;
class ARMAR
{
public:
    ARMAR();
    ros::NodeHandle nh;
    tf::TransformListener listener;
    ros::ServiceClient client_goto;
	ros::ServiceServer gotoar_server,getar_server;

    arm_controller::control get_ar(int data);

    bool getar_callback(arm_controller::PickPlace::Request &req,
                        arm_controller::PickPlace::Response &res);
    bool gotoar_callback(arm_controller::PickPlace::Request &req,
                         arm_controller::PickPlace::Response &res);

private:
    /* data */
};

ARMAR::ARMAR(){
    client_goto=nh.serviceClient<arm_controller::move>("goto_position");
    getar_server=nh.advertiseService("get_ar",&ARMAR::getar_callback,this);
    gotoar_server=nh.advertiseService("goto_ar",&ARMAR::gotoar_callback,this);

}

//get 出ar的位置
arm_controller::control ARMAR::get_ar(int data)
{
    stringstream ss;
    string stra="";
    ss<<"/ar_marker_";
    ss<<data;
    ss>>stra;
    const string &strb=stra;
    arm_controller::control pos;
    tf::StampedTransform transform;
    try
    {
        listener.waitForTransform("/robot",strb, ros::Time(0), ros::Duration(3.0));
        listener.lookupTransform("/robot",strb, ros::Time(0), transform);
    }
    catch (tf::TransformException &ex) 
    {
        ROS_ERROR("TF may have some problems.\n %s",ex.what());
        ros::Duration(1.0).sleep();
        return pos;
    }
    pos.position.x = transform.getOrigin().x()*1000.0;
    pos.position.y = transform.getOrigin().y()*1000.0;
    pos.position.z = transform.getOrigin().z()*1000.0;

    return pos;
}


bool ARMAR::getar_callback(arm_controller::PickPlace::Request &req,
                        arm_controller::PickPlace::Response &res)
{
    res.pose = get_ar(req.number);
    res.success = true;
    return true;
}

bool ARMAR::gotoar_callback(arm_controller::PickPlace::Request &req,
                            arm_controller::PickPlace::Response &res)
{
    arm_controller::move srv;
    res.pose = srv.request.pose = get_ar(req.number);
    srv.request.pose.position.z += 20;
    //走到ar码上方
    if (client_goto.call(srv))
    {
        if (srv.response.success)
        {
            res.success = true;
        }else{
            res.success = false;
        }
    }else{
        res.success = false;
    }
    srv.request.pose = res.pose;
    //ar码
    if (client_goto.call(srv))
    {
        if (srv.response.success)
        {
            res.success = true;
        }else{
            res.success = false;
        }
    }else{
        res.success = false;
    }
    return true;
}


int main(int argc,char** argv)
{
    //节点初始化
    ros::init(argc,argv,"arm_ar");
    //实例化类PickAr
    ARMAR arm_ar;
    //多线程接收
    ros::AsyncSpinner spinner(2); 
    spinner.start();
    ros::waitForShutdown();
    return 0;
}

