<launch>
  <!-- 夹爪控制 + 集成桥接一键启动 -->

  <!-- 串口参数 -->
  <arg name="gripper_port" default="/dev/ttyGripper" />
  <arg name="servo_id" default="1" />
  <!-- 实测(2026-08-08): 2000=抓紧(闭合), 500=松开(张开) -->
  <arg name="pulse_grip" default="2000" />
  <arg name="pulse_release" default="500" />

  <!-- 夹爪舵机节点 -->
  <node pkg="gripper_control" exec="gripper_node.py" name="gripper_node" output="screen">
    <param name="port" value="$(var gripper_port)" />
    <param name="baudrate" value="115200" />
    <param name="servo_id" value="$(var servo_id)" />
    <param name="pulse_min" value="$(var pulse_release)" />
    <param name="pulse_max" value="$(var pulse_grip)" />
  </node>

  <!-- 夹爪-机械臂集成节点 (预抓取偏移30mm, 抬升50mm) -->
  <node pkg="gripper_control" exec="gripper_integration.py" name="gripper_integration" output="screen">
    <param name="grip_delay" value="0.5" />
    <param name="pre_grasp_offset_z" value="30.0" />
    <param name="lift_height" value="50.0" />
  </node>
</launch>
