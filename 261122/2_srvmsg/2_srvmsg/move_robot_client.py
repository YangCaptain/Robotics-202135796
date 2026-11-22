import math
import rclpy
from rclpy.node import Node
from custom_interfaces.srv import MoveRobot

class MoveRobotClient(Node):
    def __init__(self):
        super().__init__('move_robot_client')

        self.cli = self.create_client(MoveRobot, '/move_robot')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waitng for service')

        self.req = MoveRobot.Request()

    def send_request(self, x, y, theta, distance):
        self.req.current_pose.x = float(x)
        self.req.current_pose.y = float(y)
        self.req.current_pose.theta = float(theta)
        self.req.distance = float(distance)

        self.future = self.cli.call_async(self.req)
        rclpy.spin_until_future_complete(self, self.future)

        return self.future.result()

def main():
    rclpy.init()
    node = MoveRobotClient()
    response = client.send_request(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

    pose = response.result_pose
    client.get_logger().info(
        f'Result: x={pose.x:.2f}, y={pose.y:.2f}, theta={pose.theta:.2f},success={response.success}')
    node.destroy_node()
    rclpy.shutdown()

if __name__ =='__main--':
    main()
        
