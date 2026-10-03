#include <rclcpp/rclcpp.hpp>
#include <tf2_ros/transform_listener.h>
#include <tf2_ros/transform_broadcaster.h>
#include <tf2_ros/buffer.h>
#include <tf2_geometry_msgs/tf2_geometry_msgs.hpp>
#include <geometry_msgs/msg/transform_stamped.hpp>

#include "arm_controller/msg/control.hpp"
#include "arm_controller/srv/move.hpp"
#include "arm_controller/srv/pick_place.hpp"

#include <string>
#include <memory>
#include <chrono>
#include <cmath>
#include <sstream>

using namespace std;
using namespace std::chrono_literals;

#define CAMREA_X_MAX 200
#define CAMREA_Y_MAX 0
#define CAMREA_Z_MAX 170

class PickAr : public rclcpp::Node
{
public:
    PickAr();

private:
    rclcpp::Service<arm_controller::srv::PickPlace>::SharedPtr pick_server_;
    rclcpp::Service<arm_controller::srv::Move>::SharedPtr place_server_;
    rclcpp::Client<arm_controller::srv::Move>::SharedPtr client_pick_;
    rclcpp::Client<arm_controller::srv::Move>::SharedPtr client_goto_;
    rclcpp::Client<arm_controller::srv::Move>::SharedPtr client_place_;
    rclcpp::Subscription<arm_controller::msg::Control>::SharedPtr sub_;

    std::shared_ptr<tf2_ros::Buffer> tf_buffer_;
    std::shared_ptr<tf2_ros::TransformListener> tf_listener_;
    std::shared_ptr<tf2_ros::TransformBroadcaster> tf_broadcaster_;

    float position_[4];

    void position_callback(const arm_controller::msg::Control::SharedPtr msg);
    void pick_callback(const std::shared_ptr<arm_controller::srv::PickPlace::Request> req,
                       std::shared_ptr<arm_controller::srv::PickPlace::Response> res);
    void place_callback(const std::shared_ptr<arm_controller::srv::Move::Request> req,
                        std::shared_ptr<arm_controller::srv::Move::Response> res);

    bool call_goto(float x, float y, float z);
    bool call_pick(float x, float y, float z);
    bool call_place(float x, float y, float z);
};

PickAr::PickAr() : Node("robot_pick")
{
    pick_server_ = this->create_service<arm_controller::srv::PickPlace>("pick_ar",
        [this](const std::shared_ptr<arm_controller::srv::PickPlace::Request> req,
               std::shared_ptr<arm_controller::srv::PickPlace::Response> res) {
            this->pick_callback(req, res);
        });
    place_server_ = this->create_service<arm_controller::srv::Move>("place_ar",
        [this](const std::shared_ptr<arm_controller::srv::Move::Request> req,
               std::shared_ptr<arm_controller::srv::Move::Response> res) {
            this->place_callback(req, res);
        });

    client_pick_ = this->create_client<arm_controller::srv::Move>("pick");
    client_place_ = this->create_client<arm_controller::srv::Move>("place");
    client_goto_ = this->create_client<arm_controller::srv::Move>("goto_position");

    sub_ = this->create_subscription<arm_controller::msg::Control>(
        "arm_controller/position_info", 100,
        [this](const arm_controller::msg::Control::SharedPtr msg) {
            this->position_callback(msg);
        });

    tf_buffer_ = std::make_shared<tf2_ros::Buffer>(this->get_clock());
    tf_listener_ = std::make_shared<tf2_ros::TransformListener>(*tf_buffer_);
    tf_broadcaster_ = std::make_shared<tf2_ros::TransformBroadcaster>(this);

    RCLCPP_INFO(this->get_logger(), "INIT OK");
}

bool PickAr::call_goto(float x, float y, float z)
{
    auto req = std::make_shared<arm_controller::srv::Move::Request>();
    req->pose.position.x = x;
    req->pose.position.y = y;
    req->pose.position.z = z;
    auto future = client_goto_->async_send_request(req);
    if (rclcpp::spin_until_future_complete(shared_from_this(), future, 10s) == rclcpp::FutureReturnCode::SUCCESS) {
        return future.get()->success;
    }
    return false;
}

bool PickAr::call_pick(float x, float y, float z)
{
    auto req = std::make_shared<arm_controller::srv::Move::Request>();
    req->pose.position.x = x;
    req->pose.position.y = y;
    req->pose.position.z = z;
    auto future = client_pick_->async_send_request(req);
    if (rclcpp::spin_until_future_complete(shared_from_this(), future, 10s) == rclcpp::FutureReturnCode::SUCCESS) {
        return future.get()->success;
    }
    return false;
}

bool PickAr::call_place(float x, float y, float z)
{
    auto req = std::make_shared<arm_controller::srv::Move::Request>();
    req->pose.position.x = x;
    req->pose.position.y = y;
    req->pose.position.z = z;
    auto future = client_place_->async_send_request(req);
    if (rclcpp::spin_until_future_complete(shared_from_this(), future, 10s) == rclcpp::FutureReturnCode::SUCCESS) {
        return future.get()->success;
    }
    return false;
}

void PickAr::position_callback(const arm_controller::msg::Control::SharedPtr msg)
{
    position_[0] = msg->position.x;
    position_[1] = msg->position.y;
    position_[2] = msg->position.z;

    geometry_msgs::msg::TransformStamped robot_trans;
    robot_trans.header.stamp = this->now();
    robot_trans.header.frame_id = "robot";
    robot_trans.child_frame_id = "end";

    robot_trans.transform.translation.x = position_[0] / 1000.0;
    robot_trans.transform.translation.y = position_[1] / 1000.0;
    robot_trans.transform.translation.z = position_[2] / 1000.0;

    tf2::Quaternion q;
    q.setRPY(0, 0, atan2(position_[1], position_[0]));
    robot_trans.transform.rotation = tf2::toMsg(q);

    tf_broadcaster_->sendTransform(robot_trans);
}

void PickAr::pick_callback(const std::shared_ptr<arm_controller::srv::PickPlace::Request> req,
                           std::shared_ptr<arm_controller::srv::PickPlace::Response> res)
{
    stringstream ss;
    string stra = "";
    ss << "/ar_marker_" << (int)req->number;
    ss >> stra;

    if (req->mode == 0) {
        if (!call_goto(CAMREA_X_MAX, CAMREA_Y_MAX, CAMREA_Z_MAX)) {
            res->message = "error!";
            res->success = false;
            return;
        }
    } else if (req->mode != 1) {
        res->message = "Pattern error!";
        res->success = false;
        return;
    }

    std::this_thread::sleep_for(1s);

    geometry_msgs::msg::TransformStamped transform;
    try {
        transform = tf_buffer_->lookupTransform("robot", stra, tf2::TimePointZero, 3s);
    } catch (tf2::TransformException &ex) {
        RCLCPP_ERROR(this->get_logger(), "TF error: %s", ex.what());
        std::this_thread::sleep_for(1s);
        res->success = false;
        return;
    }

    float x_ = transform.transform.translation.x * 1000.0f;
    float y_ = transform.transform.translation.y * 1000.0f;
    float z_ = transform.transform.translation.z * 1000.0f;
    RCLCPP_INFO(this->get_logger(), "r-a X: %.3f Y: %.3f Z: %.3f", x_, y_, z_);

    call_goto(x_, y_, z_ + 50);

    if (call_pick(x_, y_, z_)) {
        res->success = true;
    } else {
        res->message = "Manipulator unattainable!";
        res->success = false;
    }

    std::this_thread::sleep_for(400ms);
    call_goto(x_, y_, z_ + 50);
    std::this_thread::sleep_for(300ms);

    if (abs(req->pose.position.x) > 0.001f || abs(req->pose.position.y) > 0.001f || abs(req->pose.position.z) > 0.001f) {
        RCLCPP_INFO(this->get_logger(), "goto");
        call_goto(req->pose.position.x, req->pose.position.y, req->pose.position.z + 50);
        call_place(req->pose.position.x, req->pose.position.y, req->pose.position.z);
        RCLCPP_INFO(this->get_logger(), "place end");
    } else if (req->mode == 0) {
        RCLCPP_INFO(this->get_logger(), "固定位置");
        call_goto(CAMREA_X_MAX, CAMREA_Y_MAX, CAMREA_Z_MAX);
    } else {
        RCLCPP_INFO(this->get_logger(), "mode == 1");
    }
}

void PickAr::place_callback(const std::shared_ptr<arm_controller::srv::Move::Request> req,
                            std::shared_ptr<arm_controller::srv::Move::Response> res)
{
    call_goto(req->pose.position.x, req->pose.position.y, req->pose.position.z + 50);
    call_place(req->pose.position.x, req->pose.position.y, req->pose.position.z);
    res->success = true;
}

int main(int argc, char** argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<PickAr>();
    rclcpp::executors::MultiThreadedExecutor executor;
    executor.add_node(node);
    executor.spin();
    rclcpp::shutdown();
    return 0;
}
