#include <rei_robot_base/communication/rei_base_communication.h>
#include <string.h>

#include <thread>
namespace reinovo_base {
RobotBaseCom::RobotBaseCom()
    : err_time_(0), is_connected_(false), read_data_lenth_(27), sleep_ms_(10) {
  memset(buff_, 0, sizeof(buff_));
}
RobotBaseCom::~RobotBaseCom() {
  CloseConnect();
}

int8_t RobotBaseCom::Connect() {
  if (is_connected_) return 1;
  mb_ =
      modbus_new_rtu(communicate_params_.port.c_str(), communicate_params_.baud,
                     communicate_params_.parity, communicate_params_.data_bit,
                     communicate_params_.stop_bit);
  if (mb_ == NULL) return -1;

  modbus_set_slave(mb_, communicate_params_.slave);

  if (modbus_connect(mb_) != 0) {
    modbus_free(mb_);
    mb_ = nullptr;
    return -1;
  }

  is_connected_ = true;
  std::this_thread::sleep_for(std::chrono::milliseconds(500));

#if MODBUS_VERION_COMPARE(>=, 3, 1, 2)
  modbus_set_response_timeout(mb_, 0, 200000);
#else
  struct timeval timeout;
  timeout.tv_sec = 0;
  timeout.tv_usec = 200000;
  modbus_Set_response_timeout(mb_, &timeout);
#endif

  std::vector<double> speed(4, 0.0);
  this->SendSpeed(speed);
  return 0;
}

int8_t RobotBaseCom::CloseConnect() {
  if (is_connected_ && mb_ != nullptr) {
    std::vector<double> speed(4, 0.0);
    this->SendSpeed(speed);
    modbus_close(mb_);
    is_connected_ = false;
  }
  if(mb_ != nullptr) {
    modbus_free(mb_);
    mb_ = nullptr;
  }
  return 0;
}

int8_t RobotBaseCom::ReadData() {
  if (is_connected_ && mb_ != nullptr) {
    std::this_thread::sleep_for(sleep_ms_);
    int size = modbus_read_input_registers(mb_, 0, read_data_lenth_, buff_);
    if (size == read_data_lenth_) {
      err_time_ = 0;
      return 0;

    } else {
      return -1;
      err_time_++;
      if (err_time_ > 5) CloseConnect();
    }
  } else
    return -1;
}
int8_t RobotBaseCom::GetMotorSpeed(std::vector<double> &data_out) {
  if (is_connected_) {
    if(data_out.size() != 16) data_out.resize(16, 0.0);
    int idx=0;
    for (size_t i = DataAdress::MotorSpeed; i < (DataAdress::MotorSpeed + 16);
         i = i + 4) {
      d_to_uint_.id[3] = buff_[i];
      d_to_uint_.id[2] = buff_[i + 1];
      d_to_uint_.id[1] = buff_[i + 2];
      d_to_uint_.id[0] = buff_[i + 3];
      data_out[idx] = d_to_uint_.dd;
      idx++;
    }
    return 0;
  } else
    return -1;
}
int8_t RobotBaseCom::GetUltraSound(std::vector<float> &data_out) {
  if (is_connected_) {
    data_out.clear();
    int dist = buff_[DataAdress::UltruaSound];
    if (dist == 65535) dist = -99900.0f;
    data_out.push_back((float)dist);

    dist = buff_[DataAdress::UltruaSound + 1];
    if (dist == 65535) dist = -99900.0f;
    data_out.push_back((float)dist);

    dist = buff_[DataAdress::UltruaSound + 2];
    if (dist == 65535) dist = -99900.0f;
    data_out.push_back((float)dist);
    return 0;
  } else
    return -1;
}
int8_t RobotBaseCom::GetPower(float &data_out) {
  if (is_connected_) {
    int power = buff_[DataAdress::Power];
    data_out = (float)power / 1000.0;
    return 0;
  } else
    return -1;
}
int8_t RobotBaseCom::GetCharge(int &data_out) {
  if (is_connected_) {
    data_out = 1 >> buff_[DataAdress::Charge];  // 0则取1,1则取0
    return 0;
  } else
    return -1;
}
int8_t RobotBaseCom::GetInputIO(std::vector<int> &data_out) {
  if (is_connected_) {
    if(data_out.size() != 4) data_out.resize(4, 0);
    uint16_t check_bit = 1;
    uint16_t io_data = buff_[DataAdress::InputIO];
    // std::cout<<io_data<<std::endl;
    for (size_t i = 0; i < 4; i++) {
      data_out[i] = ((io_data >> i) & check_bit);
    }
    return 0;
  } else
    return -1;
}
int8_t RobotBaseCom::GetSmoke(int &data_out) {
  if (is_connected_) {
    data_out = 1 >> buff_[DataAdress::Smoke];  // 0则取1,1则取0
    return 0;
  } else
    return -1;
}
int8_t RobotBaseCom::GetTemperature(float &data_out) {
  if (is_connected_) {
    f_to_uint_.id[1] = buff_[DataAdress::Temperature];
    f_to_uint_.id[0] = buff_[DataAdress::Temperature + 1];
    data_out = f_to_uint_.fd;
    return 0;
  } else
    return -1;
}
int8_t RobotBaseCom::GetRelativeHumidity(float &data_out) {
  if (is_connected_) {
    f_to_uint_.id[1] = buff_[DataAdress::RelativeHumidity];
    f_to_uint_.id[0] = buff_[DataAdress::RelativeHumidity + 1];
    data_out = f_to_uint_.fd;
    return 0;
  } else
    return -1;
}
int8_t RobotBaseCom::GetBumper(std::vector<int> &data_out) {
  if (is_connected_) {
    std::vector<int> temp(4);
    if (GetInputIO(temp) == 0) {
      if(data_out.size() != 3) data_out.resize(3, 0);
      data_out[0] = temp[5];
      data_out[1] = temp[1];
      data_out[2] = temp[3];
      return 0;
    } else
      return -1;
  } else
    return -1;
}
int8_t RobotBaseCom::GetCliff(std::vector<int> &data_out) {
  if (is_connected_) {
    std::vector<int> temp(4);
    if (GetInputIO(temp) == 0) {
      if(data_out.size() != 3) data_out.resize(3, 0);
      data_out[0] = temp[5];
      data_out[1] = temp[1];
      data_out[2] = temp[3];
      return 0;
    } else
      return -1;
  } else
    return -1;
}

int8_t RobotBaseCom::SendSpeed(const std::vector<double> &motors_speed) {
  if (is_connected_ && mb_ != nullptr) {
    uint16_t send_data[16];
    uint16_t *p = send_data;
    memset(send_data, 0, sizeof(send_data));
    for (size_t i = 0; i < motors_speed.size(); i++) {
      d_to_uint_.dd = motors_speed[i];
      *p++ = d_to_uint_.id[3];
      *p++ = d_to_uint_.id[2];
      *p++ = d_to_uint_.id[1];
      *p++ = d_to_uint_.id[0];
    }
    std::this_thread::sleep_for(sleep_ms_);
    if (modbus_write_registers(mb_, 0, 16, send_data) == 16)
      return 0;
    else
      return -1;
  } else
    return -1;
}

int8_t RobotBaseCom::SetRelay(bool state) {
  if (is_connected_) {
    uint16_t data;
    if (state)
      data = 1;
    else
      data = 0;
    std::this_thread::sleep_for(sleep_ms_);
    if (modbus_write_registers(mb_, DataAdress::Relay, 1, &data) == 1) {
      registerbuff_[1] = data;
      return 0;
    } else
      return -1;
  } else
    return -1;
}

int8_t RobotBaseCom::SetIO(uint16_t io[7]) {
  uint16_t data = 0;
  for (size_t i = 0; i < 7; i++) {
    data = data + (io[i] << i);
  }
  std::this_thread::sleep_for(sleep_ms_);
  if (modbus_write_registers(mb_, DataAdress::OutputIO, 1, &data) == 1) {
    registerbuff_[2] = data;
    return 0;
  } else
    return -1;
}

int8_t RobotBaseCom::SetExtraMotor(int state) {
  if (is_connected_) {
    uint16_t command;
    if (state < 0)
      command = 1;  // 反转
    else if (state > 0)
      command = 3;  // 正转
    else
      command = 0;  // 停止
    std::this_thread::sleep_for(sleep_ms_);
    if (modbus_write_registers(mb_, DataAdress::ExtraMotor, 1, &command) == 1) {
      return 0;
    } else
      return -1;
  } else
    return -1;
}

int8_t RobotBaseCom::SetBuzzer(int time) {
  if (is_connected_) {
    if ((time > 10) || (time < 0))
      return -2;
    else {
      uint16_t data = (time > 0) ? 1 : 0;
      std::this_thread::sleep_for(sleep_ms_);
      if (modbus_write_registers(mb_, DataAdress::Buzzer, 1, &data) == 1) {
        registerbuff_[0] = data;
        return 0;
      } else
        return -1;
    }
  } else
    return -1;
}

int8_t RobotBaseCom::GetRelay(bool &data_out) {
  if (is_connected_) {
    if (registerbuff_[1] == 1)
      data_out = true;
    else
      data_out = false;
    return 0;
  } else
    return -1;
}

int8_t RobotBaseCom::GetOutputIO(std::vector<int> &data_out) {
  if (is_connected_) {
    if(data_out.size() != 7) data_out.resize(7, 0);
    for (size_t i = 0; i < 7; i++) {
      if ((registerbuff_[2] >> i) & 1)
        data_out[i] = 1;
      else
        data_out[i] = 0;
    }
    return 0;
  } else
    return -1;
}
}  // namespace reinovo_base