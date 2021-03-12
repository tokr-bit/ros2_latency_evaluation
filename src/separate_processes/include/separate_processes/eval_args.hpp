#pragma once

#include "cxxopts/include/cxxopts.hpp"
#include <iostream>

class EvalArgs {
    public:
        EvalArgs() {
            pubFrequency = 0.;
            noNodes = 1;
            msgSize = "100b";
        }

        EvalArgs(int argc, char* argv[]) : EvalArgs() {
            parse(argc, argv);
        }

        void parse (int argc, char* argv[]) {
            cxxopts::Options options(argv[0], "ROS2 performance benchmark in separate processes");
            options.allow_unrecognised_options();
            options.add_options()
                ("n,no-nodes", "Number of Nodes",
                    cxxopts::value<uint>(noNodes))
                ("f,publisher-frequency", "Publisher Frequency of start node",
                    cxxopts::value<float>(pubFrequency))
                ("m,msg-size", "Size of msg, Supported: 100b, 1kb, 10kb, 100kb, 500kb",
                    cxxopts::value<std::string>(msgSize))
                ("h,help", "Print usage")
            ;
            auto result = options.parse(argc, argv);

            if (result.count("help")) {
                std::cout << options.help() << std::endl;
                exit(0);
            }
            verifyArgs();
        }

        void print() {
            std::cout << "Arguments are set as follows:" << std::endl;
            std::cout << "Publisher frequency in Hz: " << pubFrequency << std::endl;
            std::cout << "Number of nodes between start and end node: " << noNodes << std::endl;
            std::cout << "Msg size: " << msgSize << std::endl;
        }

        float pubFrequency;
        uint noNodes;
        std::string msgSize;

    private:
        std::array<std::string, 5> SUPPORTED_MSG_SIZES_ = {"100b", "1kb", "10kb", "100kb", "500kb"};

        void verifyArgs() {
            if (std::find(
                    SUPPORTED_MSG_SIZES_.begin(), 
                    SUPPORTED_MSG_SIZES_.end(),
                    msgSize) == SUPPORTED_MSG_SIZES_.end()) {
                std::cout << "Message size not supported" << std::endl;
                exit(0);
            }
                
        }
};