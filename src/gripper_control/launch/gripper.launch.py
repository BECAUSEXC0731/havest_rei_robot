<launch>
  <!-- 夹爪舵机参数 -->
  <arg name="port" default="/dev/ttyGripper" />
  <arg name="servo_id" default="1" />
  <!-- 实测(2026-08-08): 2000=抓紧(闭合), 500=松开(张开) -->
  <arg name="pulse_grip" default="2000" />
  <arg name="pulse_release" default="500" />

  <!-- 夹爪控制节点 -->
  <node pkg="gripper_control" exec="gripper_node.py" name="gripper_node" output="screen">
    <param name="port" value="$(var port)" />
    <param name="baudrate" value="115200" />
    <param name="servo_id" value="$(var servo_id)" />
    <param name="pulse_min" value="$(var pulse_release)" />
    <param name="pulse_max" value="$(var pulse_grip)" />
  </node>
</launch>
