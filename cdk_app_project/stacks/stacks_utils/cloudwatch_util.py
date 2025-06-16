def get_cloudwatch_config(group_name: str) -> dict:
    return {
        "agent": {
            "metrics_collection_interval": 60,
            "run_as_user": "root"
        },
        "metrics": {
            "namespace": "EC2/CustomMetrics",
            "append_dimensions": {
                "InstanceId": "${aws:InstanceId}"
            },
            "metrics_collected": {
                "mem": {
                    "measurement": ["mem_used_percent"],
                    "metrics_collection_interval": 60
                },
                "disk": {
                    "measurement": ["used_percent"],
                    "metrics_collection_interval": 60,
                    "resources": ["/"]
                }
            }
        },
        "logs": {
            "logs_collected": {
                "files": {
                    "collect_list": [
                        {
                            "file_path": "/var/log/messages",
                            "log_group_name": "/ec2/my-instance/messages",
                            "log_stream_name": group_name,  # now injected
                            "timestamp_format": "%b %d %H:%M:%S"
                        },
                        {
                            "file_path": "/var/log/cloud-init.log",
                            "log_group_name": "/ec2/my-instance/cloud-init",
                            "log_stream_name": group_name
                        }
                    ]
                }
            }
        }
    }
