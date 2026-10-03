#!/usr/bin/env python3
"""
uArm Swift Pro 工作空间探索脚本
逐个测试网格位置，记录可达/不可达坐标，最后输出工作空间范围
"""
import rclpy
from rclpy.node import Node
from arm_controller.srv import Move
from geometry_msgs.msg import Point
import time
import sys

class WorkspaceExplorer(Node):
    def __init__(self):
        super().__init__('workspace_explorer')
        self.cli = self.create_client(Move, 'goto_position')
        
        while not self.cli.wait_for_service(timeout_sec=5):
            self.get_logger().info('等待 goto_position 服务...')
        
        self.reachable = []
        self.unreachable = []
        self.home_pos = (200.0, 0.0, 150.0)

    def goto(self, x, y, z, roll=-1.0, retries=2):
        req = Move.Request()
        req.pose.position = Point(x=float(x), y=float(y), z=float(z))
        req.pose.roll = float(roll)
        for attempt in range(retries):
            future = self.cli.call_async(req)
            rclpy.spin_until_future_complete(self, future, timeout_sec=30)
            if future.result() is not None:
                return future.result().success
            self.get_logger().warn(f'重试 ({attempt+1}/{retries}) ({x:.0f},{y:.0f},{z:.0f})')
            time.sleep(0.5)
        return False

    def go_home(self):
        """回到安全起始位置"""
        self.get_logger().info('→ 回到起始点 (200,0,150)')
        self.goto(*self.home_pos)
        time.sleep(1.0)

    def test_line(self, axis, start, end, step, fixed_y=0, fixed_z=100):
        """沿某个轴测试一系列位置"""
        results = []
        vals = list(range(start, end + step, step)) if step > 0 else list(range(start, end + step, -step))
        for i, v in enumerate(vals):
            if axis == 'x':
                pos = (v, fixed_y, fixed_z)
            elif axis == 'y':
                pos = (200, v, fixed_z)
            else:
                pos = (200, 0, v)
            
            success = self.goto(*pos)
            results.append((pos, success))
            icon = '✓' if success else '✗'
            sys.stdout.write(f'\r{axis}={v:4d} {icon}  ')
            sys.stdout.flush()
            time.sleep(0.3)
        return results

    def explore_boundary(self):
        """逐步探索各轴边界"""
        self.get_logger().info('='*50)
        self.get_logger().info('开始工作空间边界探索')
        self.get_logger().info('='*50)
        
        all_results = {'x': [], 'y': [], 'z': []}
        
        # 1. 探索 X 轴（向前/后）— 在 Y=0, Z=100 平面
        self.get_logger().info('\n[1/7] 探索 X 轴正向 (中心Y=0, Z=100)')
        self.go_home()
        all_results['x'] += self.test_line('x', 30, 320, 15)
        
        # 2. 探索 Y 轴（左/右）— 在 X=200, Z=100 平面
        self.go_home()
        self.get_logger().info('\n[2/7] 探索 Y 轴负方向 (左)')
        all_results['y'] += self.test_line('y', 0, -200, -15)
        self.go_home()
        self.get_logger().info('\n[3/7] 探索 Y 轴正方向 (右)')
        all_results['y'] += self.test_line('y', 0, 200, 15)
        
        # 3. 探索 Z 轴（上/下）— 在 X=200, Y=0 平面
        self.go_home()
        self.get_logger().info('\n[4/7] 探索 Z 轴正向 (上)')
        all_results['z'] += self.test_line('z', 100, 250, 10)
        self.go_home()
        self.get_logger().info('\n[5/7] 探索 Z 轴负向 (下)')
        all_results['z'] += self.test_line('z', 100, 0, -10)
        
        # 5. 测试手腕旋转
        self.go_home()
        self.get_logger().info('\n[5/6] 测试手腕旋转 (G2202 N3 V)')
        wrist_angles = [0, 45, 90, 135, 180, 90, 0]
        for angle in wrist_angles:
            success = self.goto(200, 0, 130, roll=angle)
            icon = '✓' if success else '✗'
            self.get_logger().info(f'  手腕 {angle}° {icon}')
            time.sleep(0.5)
        
        # 6. 测试几个角落位置
        self.go_home()
        self.get_logger().info('\n[6/6] 测试角落位置')
        corners = [
            (80, -120, 60),   # 左下前
            (80, 120, 60),    # 右下前
            (80, -120, 180),  # 左上前
            (80, 120, 180),   # 右上前
            (280, -120, 60),  # 左下后
            (280, 120, 60),   # 右下后
            (280, -120, 180), # 左上后
            (280, 120, 180),  # 右上后
        ]
        for corner in corners:
            self.go_home()
            success = self.goto(*corner)
            icon = '✓' if success else '✗'
            self.get_logger().info(f'  角落 ({corner[0]:.0f},{corner[1]:.0f},{corner[2]:.0f}) {icon}')
            time.sleep(0.5)
        
        return all_results

    def save_results(self, all_results):
        """保存并打印结果"""
        print('\n\n' + '='*55)
        print('  uArm Swift Pro — 工作空间探索结果')
        print('='*55)
        
        for axis, results in all_results.items():
            reachable = [r for r, s in results if s]
            label_map = {'x': 'X (前后)', 'y': 'Y (左右)', 'z': 'Z (上下)'}
            if reachable:
                xs = [r[0] for r in reachable]
                ys = [r[1] for r in reachable]
                zs = [r[2] for r in reachable]
                print(f'  {label_map[axis]}: '
                      f'[{", ".join(f"{v:.0f}" for v in (xs if axis=="x" else ys if axis=="y" else zs))}]')
                vals = xs if axis=='x' else ys if axis=='y' else zs
                print(f'    范围: {min(vals):.0f} ~ {max(vals):.0f} mm')
            else:
                print(f'  {label_map[axis]}: 无数据')
        
        print(f'\n  安全起始位置: (200, 0, 150)')
        print(f'  建议工作范围:')
        print(f'    X: 80 ~ 280 mm')
        print(f'    Y: -150 ~ 150 mm')
        print(f'    Z: 30 ~ 200 mm')
        print('='*55)


def main():
    rclpy.init()
    explorer = WorkspaceExplorer()
    
    try:
        # 通信测试
        explorer.get_logger().info('通信测试...')
        test_ok = explorer.goto(210.0, 0.0, 130.0)
        if test_ok:
            explorer.get_logger().info('✓ 通信正常，开始探索')
            time.sleep(0.5)
        else:
            explorer.get_logger().warn('⚠ 通信测试异常，继续尝试')
        
        explorer.go_home()
        results = explorer.explore_boundary()
        explorer.go_home()
        explorer.save_results(results)
        
    except KeyboardInterrupt:
        explorer.get_logger().info('用户中断，归位中...')
        explorer.go_home()
    finally:
        explorer.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
