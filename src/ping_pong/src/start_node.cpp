#include <chrono>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

using namespace std::chrono_literals;
class FirstNode : public rclcpp::Node {
    public:
        FirstNode() : Node("first_node") {
            publisher_ = this->create_publisher<std_msgs::msg::String>("/first_pub_topic", 10);
            timer_ = this->create_wall_timer(
                500ms, std::bind(&FirstNode::timer_callback, this));
            subscription_ = this->create_subscription<std_msgs::msg::String>(
                "/first_sub_topic", 10, std::bind(&FirstNode::onPong, this, std::placeholders::_1)
            );
        }
    
    private:
        void timer_callback() {
            auto msg = std_msgs::msg::String();
            msg.data = "hi";
            RCLCPP_INFO(this->get_logger(), "Publishing %s", msg.data.c_str());
            publisher_->publish(msg);
        }

        void onPong(const std_msgs::msg::String::SharedPtr msg) const {
            RCLCPP_INFO(this->get_logger(), "I heard %s", msg->data.c_str());
        }
        rclcpp::TimerBase::SharedPtr timer_;
        rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;
        rclcpp::Subscription<std_msgs::msg::String>::SharedPtr subscription_;
};

int main(int argc, char* argv[]) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<FirstNode>());
    rclcpp::shutdown();
    return 0;
}
