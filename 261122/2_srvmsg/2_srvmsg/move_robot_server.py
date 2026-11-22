import math
import rclpy
from rclpy.node import Node
from custom_interfaces.srv import MoveRobot

class MoveRobotServer(Node):
    def __init__(self):
        super().__init__('move_robot_server')

        self.srv = self.create_service(MoveRobot, '/move_robot', self.srv_callback)
        self.get_logger().info('Move Robot Server Ready')
    def srv_callback(self,request,response):
        pose = request.current_pose
        distance = request.distance

        if distance < 0:
            response.result_pose = pose
            response.success = False
            self.get_logger().info(f'Invalid distance: {distance}')
            return response

        response.result_pose.x = pose.x + distance * math.cos(pose.theta)
        response.result_pose.y = pose.x + distance * math.sin(pose.theta)
        response.result_pose.theta= pose.theta
        response.success = True

        self.get_logger().info(
            f'Incoming request\nx:  {pose.x}, y: {pose.y}, theta: {pose.theta},distance: {distance}')
        self.get_logger().info(
            f'Sending back response: [x: {response.result_pose.x:.2f},'
            f'y: {response.result_pose.y:.2f}, theta: {response.result_pose.theta:.2f}]]')
        return response

def main():
    rclpy.init()
    node = MoveRobotServer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ =='__main--':
    main()
        