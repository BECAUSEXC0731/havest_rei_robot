/* 
 * Software License Agreement (BSD License)
 * Copyright (c) 2020, reinovo, Inc.
 * All rights reserved.
 * Author: LN  <825255961@qq.com>
 * 
 * ROS2 Humble migration by GitHub Copilot
 */

#include <string>
#include <vector>
#include <sstream>
#include <cmath>
#include <cstdlib>
#include <cstdio>
#include <cstring>
#include <algorithm>
#include <memory>
#include <chrono>
#include <thread>
#include <sys/ioctl.h>

#include <rclcpp/rclcpp.hpp>

#include <termios.h>
#include <fcntl.h>
#include <unistd.h>

#include "arm_controller/msg/control.hpp"
#include "arm_controller/srv/move.hpp"
#include "arm_controller/srv/relative_pos.hpp"
#include "std_srvs/srv/set_bool.hpp"

using namespace std;
using namespace std::chrono_literals;

// 简单的 POSIX 串口封装
class SerialPort {
    int fd_ = -1;
public:
    SerialPort() {}
    ~SerialPort() { close(); }

    bool open(const char* port, int baud) {
        fd_ = ::open(port, O_RDWR | O_NOCTTY | O_NDELAY);
        if (fd_ < 0) return false;

        struct termios tty;
        memset(&tty, 0, sizeof(tty));
        if (tcgetattr(fd_, &tty) != 0) return false;

        cfsetospeed(&tty, baud);
        cfsetispeed(&tty, baud);

        tty.c_cflag = (tty.c_cflag & ~CSIZE) | CS8;
        tty.c_iflag &= ~IGNBRK;
        tty.c_lflag = 0;
        tty.c_oflag = 0;
        tty.c_cc[VMIN] = 0;
        tty.c_cc[VTIME] = 10;
        tty.c_iflag &= ~(IXON | IXOFF | IXANY);
        tty.c_cflag |= (CLOCAL | CREAD);
        tty.c_cflag &= ~(PARENB | PARODD);
        tty.c_cflag &= ~CSTOPB;
        tty.c_cflag &= ~CRTSCTS;

        if (tcsetattr(fd_, TCSANOW, &tty) != 0) return false;
        return true;
    }

    bool isOpen() const { return fd_ >= 0; }
    void close() { if (fd_ >= 0) { ::close(fd_); fd_ = -1; } }

    int write(const string& data) {
        return ::write(fd_, data.c_str(), data.size());
    }

    int available() {
        int n = 0;
        ioctl(fd_, FIONREAD, &n);
        return n;
    }

    string read(int n) {
        char buf[1024];
        int r = ::read(fd_, buf, min(n, 1024));
        if (r > 0) return string(buf, r);
        return "";
    }

    int readline(string& line, int maxlen, const char* delim) {
        line.clear();
        char c;
        int r;
        while ((r = ::read(fd_, &c, 1)) > 0 && (int)line.size() < maxlen) {
            line += c;
            if (delim[0] == c) break;
        }
        return line.size();
    }
};

static string read_data;
static SerialPort _serial;
static arm_controller::msg::Control pos_;
static rclcpp::Publisher<arm_controller::msg::Control>::SharedPtr pub;
static std::shared_ptr<rclcpp::Node> node;

// 获取位姿
bool get_pos()
{
    std::string Gcode = "", data = "";
    Gcode = (std::string)"P2220" + "\r\n";
    _serial.write(Gcode.c_str());
    data = _serial.read(_serial.available());

    std::vector<std::string> v;
    std::string::size_type pos1, pos2, pos3;
    pos1 = data.find("X");
    pos2 = data.find("Y");
    pos3 = data.find("Z");
    if (pos1 == string::npos || pos2 == string::npos || pos3 == string::npos)
        return false;

    v.push_back(data.substr(pos1+1, pos2-pos1));
    v.push_back(data.substr(pos2+1, pos3-pos2));
    v.push_back(data.substr(pos3+1, data.length()-pos3-1));

    if (v.size() >= 3) {
        pos_.position.x = std::atof(v[0].c_str());
        pos_.position.y = std::atof(v[1].c_str());
        pos_.position.z = std::atof(v[2].c_str());
        return true;
    }
    return false;
}

// 获取第四轴（手腕）角度
bool get_wrist_angle()
{
    std::string data;
    _serial.write("P2206 N3\r\n");
    std::this_thread::sleep_for(50ms);
    data = _serial.read(_serial.available());
    auto pos = data.find("V");
    if (pos != string::npos) {
        pos_.roll = std::atof(data.substr(pos+1).c_str());
        return true;
    }
    return false;
}

// goto pos（支持手腕旋转，wrist_angle: 0~180°, -1 表示不控制手腕）
bool goto_pos(float gx, float gy, float gz, float wrist_angle = -1)
{
    std::string Gcode = "";
    string result;
    rclcpp::WallRate loop_rate(20);

    if (_serial.available())
        _serial.read(_serial.available());

    // 边界限制（防止标定偏差导致目标超出物理范围）
    gx = std::clamp(gx, 30.0f, 320.0f);
    gy = std::clamp(gy, -180.0f, 180.0f);
    gz = std::clamp(gz, 20.0f, 200.0f);

    char x[10], y[10], z[10];
    sprintf(x, "%.2f", gx);
    sprintf(y, "%.2f", gy);
    sprintf(z, "%.2f", gz);

    // 检测可达性，不可达时在 XY 平面螺旋搜索附近位置
    bool reachable = false;
    // 螺旋搜索 + 朝向工作空间中心收缩
    for (int radius = 0; radius <= 60; radius += 10) {
        static const float offsets[][2] = {
            {0,0}, {1,0}, {-1,0}, {0,1}, {0,-1},
            {1,1}, {-1,1}, {1,-1}, {-1,-1}
        };
        for (auto& o : offsets) {
            float tx = gx + o[0] * radius;
            float ty = gy + o[1] * radius;
            // 限制边界内
            tx = std::clamp(tx, 30.0f, 320.0f);
            ty = std::clamp(ty, -180.0f, 180.0f);
            char sx[10], sy[10];
            sprintf(sx, "%.2f", tx);
            sprintf(sy, "%.2f", ty);
            Gcode = (std::string)"M2222 X" + sx + " Y" + sy + " Z" + z + "\n";
            _serial.write(Gcode.c_str());
            std::this_thread::sleep_for(20ms);
            result = _serial.read(_serial.available());
            if (result.find("V1") < 100) {
                reachable = true;
                if (radius > 0)
                    RCLCPP_INFO(rclcpp::get_logger("arm_swiftpro"), "Adjusted (r%d): X%s Y%s Z%s", radius, sx, sy, z);
                strcpy(x, sx); strcpy(y, sy);
                goto MOVE;
            }
        }
    }
    // 最终兜底：尝试安全位置
    RCLCPP_WARN(rclcpp::get_logger("arm_swiftpro"), "Target unreachable, trying home");
    sprintf(x, "%.2f", 200.0f);
    sprintf(y, "%.2f", 0.0f);
    sprintf(z, "%.2f", 130.0f);
    Gcode = (std::string)"M2222 X200.00 Y0.00 Z130.00\n";
    _serial.write(Gcode.c_str());
    std::this_thread::sleep_for(100ms);
    result = _serial.read(_serial.available());
    if (result.find("V1") < 100) {
        RCLCPP_WARN(rclcpp::get_logger("arm_swiftpro"), "Even home unreachable!");
        return false;
    }
    MOVE:
    Gcode = (std::string)"G0 X" + x + " Y" + y + " Z" + z + " F10000" + "\n";
    RCLCPP_INFO(rclcpp::get_logger("arm_swiftpro"), "%s", Gcode.c_str());
    _serial.write(Gcode.c_str());
    std::this_thread::sleep_for(200ms);
    result = _serial.read(_serial.available());

    if (result.find("E26") < 100) {
        char x1[10], y1[10], z1[10];
        sprintf(x1, "%.2f", 200.0);
        sprintf(y1, "%.2f", 0.0);
        sprintf(z1, "%.2f", 100.0);
        Gcode = (std::string)"G0 X" + x1 + " Y" + y1 + " Z" + z1 + " F10000" + "\r\n";
        RCLCPP_INFO(rclcpp::get_logger("arm_swiftpro"), "%s", Gcode.c_str());
        _serial.write(Gcode.c_str());
        result = _serial.read(_serial.available());

        int i = 0;
        while (!(abs(pos_.position.x-200.0)<1 && abs(pos_.position.y-0.0)<1 && abs(pos_.position.z-100.0)<1)) {
            get_pos();
            loop_rate.sleep();
            i++;
            if (i > 200) return false;
        }

        Gcode = (std::string)"G0 X" + x + " Y" + y + " Z" + z + " F10000" + "\n";
        _serial.write(Gcode.c_str());
        result = _serial.read(_serial.available());
    }

    // 等待到达目标位置
    {
        int i = 0;
        while (!(abs(pos_.position.x-gx)<1 && abs(pos_.position.y-gy)<1 && abs(pos_.position.z-gz)<1)) {
            get_pos();
            loop_rate.sleep();
            i++;
            if (i > 200) return false;
        }
    }

    // 设置手腕旋转角度（如指定）
    if (wrist_angle >= 0 && wrist_angle <= 180) {
        char w[10];
        sprintf(w, "%.0f", wrist_angle);
        Gcode = (std::string)"G2202 N3 V" + w + "\n";
        RCLCPP_INFO(rclcpp::get_logger("arm_swiftpro"), "Wrist: %s", Gcode.c_str());
        _serial.write(Gcode.c_str());
        std::this_thread::sleep_for(300ms);
        result = _serial.read(_serial.available());
        pos_.roll = wrist_angle;
    }

    return true;
}

// 服务回调: goto_position
void goto_position_deal(const std::shared_ptr<arm_controller::srv::Move::Request> req,
                        std::shared_ptr<arm_controller::srv::Move::Response> res)
{
    res->success = goto_pos(req->pose.position.x, req->pose.position.y, req->pose.position.z, req->pose.roll);
}

// 服务回调: place
void place_deal(const std::shared_ptr<arm_controller::srv::Move::Request> req,
                std::shared_ptr<arm_controller::srv::Move::Response> res)
{
    res->success = goto_pos(req->pose.position.x, req->pose.position.y, req->pose.position.z, req->pose.roll);
    if (!res->success) return;

    std::string Gcode = (std::string)"M2231 V0" + "\r\n";
    RCLCPP_INFO(rclcpp::get_logger("arm_swiftpro"), "%s", Gcode.c_str());
    _serial.write(Gcode.c_str());
    read_data = _serial.read(_serial.available());
}

// 服务回调: pick
void pick_deal(const std::shared_ptr<arm_controller::srv::Move::Request> req,
               std::shared_ptr<arm_controller::srv::Move::Response> res)
{
    res->success = goto_pos(req->pose.position.x, req->pose.position.y, req->pose.position.z, req->pose.roll);
    if (!res->success) {
        res->success = false;
        return;
    }
    std::string Gcode = (std::string)"M2231 V1" + "\r\n";
    RCLCPP_INFO(rclcpp::get_logger("arm_swiftpro"), "%s", Gcode.c_str());
    _serial.write(Gcode.c_str());
    res->success = true;
    read_data = _serial.read(_serial.available());
}

// 服务回调: relative_position
void relativeMotion_deal(const std::shared_ptr<arm_controller::srv::RelativePos::Request> req,
                         std::shared_ptr<arm_controller::srv::RelativePos::Response> res)
{
    float x = pos_.position.x + req->dx;
    float y = pos_.position.y + req->dy;
    float z = pos_.position.z + req->dz;
    res->success = goto_pos(x, y, z);
}

// 服务回调: pump
void pump_deal(const std::shared_ptr<std_srvs::srv::SetBool::Request> req,
               std::shared_ptr<std_srvs::srv::SetBool::Response> res)
{
    std::string Gcode;
    if (req->data) {
        Gcode = (std::string)"M2231 V1" + "\r\n";
    } else {
        Gcode = (std::string)"M2231 V0" + "\r\n";
    }
    RCLCPP_INFO(rclcpp::get_logger("arm_swiftpro"), "%s", Gcode.c_str());
    _serial.write(Gcode.c_str());
    res->success = true;
    read_data = _serial.read(_serial.available());
}

int main(int argc, char** argv)
{
    rclcpp::init(argc, argv);
    node = rclcpp::Node::make_shared("swiftpro_write_node");

    // 服务端
    auto pick_server = node->create_service<arm_controller::srv::Move>("pick", pick_deal);
    auto place_server = node->create_service<arm_controller::srv::Move>("place", place_deal);
    auto goto_position_server = node->create_service<arm_controller::srv::Move>("goto_position", goto_position_deal);
    auto relativeMotion_server = node->create_service<arm_controller::srv::RelativePos>("relative_position", relativeMotion_deal);
    auto pump_server = node->create_service<std_srvs::srv::SetBool>("pump", pump_deal);

    // 🆕 新增服务
    auto home_server = node->create_service<std_srvs::srv::SetBool>("home", 
        [](const std::shared_ptr<std_srvs::srv::SetBool::Request>, 
           std::shared_ptr<std_srvs::srv::SetBool::Response> res) {
            res->success = goto_pos(200, 0, 150);
        });
    auto set_zero_server = node->create_service<std_srvs::srv::SetBool>("set_zero",
        [](const std::shared_ptr<std_srvs::srv::SetBool::Request>,
           std::shared_ptr<std_srvs::srv::SetBool::Response> res) {
            _serial.write("M2401\r\n");
            std::this_thread::sleep_for(100ms);
            _serial.read(_serial.available());
            RCLCPP_INFO(rclcpp::get_logger("arm_swiftpro"), "Current position set as zero");
            res->success = true;
        });
    auto unlock_server = node->create_service<std_srvs::srv::SetBool>("unlock",
        [](const std::shared_ptr<std_srvs::srv::SetBool::Request>,
           std::shared_ptr<std_srvs::srv::SetBool::Response> res) {
            _serial.write("M2019\r\n");
            std::this_thread::sleep_for(100ms);
            _serial.read(_serial.available());
            RCLCPP_INFO(rclcpp::get_logger("arm_swiftpro"), "Motors unlocked, you can move arm manually");
            res->success = true;
        });

    // 发布者
    pub = node->create_publisher<arm_controller::msg::Control>("arm_controller/position_info", 1);

    // 串口连接
    if (_serial.open("/dev/ttyACM0", B115200)) {
        RCLCPP_INFO(node->get_logger(), "Port has been open successfully");
    } else {
        RCLCPP_ERROR(node->get_logger(), "Unable to open port");
        return -1;
    }

    if (_serial.isOpen()) {
        std::this_thread::sleep_for(3500ms);
        _serial.write("M2120 V0\r\n");
        std::this_thread::sleep_for(100ms);
        _serial.write("M17\r\n");
        std::this_thread::sleep_for(100ms);
        RCLCPP_INFO(node->get_logger(), "Attach and wait for commands");
    }

    // 等待初始化完成
    while (rclcpp::ok()) {
        string read_line;
        _serial.readline(read_line, 65535, "\n");
        cout << read_line;
        if (read_line.find("@5 V1") < 1000) break;
        std::this_thread::sleep_for(50ms);
    }

    rclcpp::WallRate loop_rate(10);
    while (rclcpp::ok()) {
        get_pos();
        get_wrist_angle();
        if (abs(pos_.position.x) < 0.1 && abs(pos_.position.y) < 0.1 && abs(pos_.position.z) < 0.1) {
            rclcpp::spin_some(node);
            loop_rate.sleep();
            continue;
        }
        pub->publish(pos_);
        rclcpp::spin_some(node);
        loop_rate.sleep();
    }

    return 0;
}
