#!/bin/bash

rabbitmqctl add_user grandma "test"
rabbitmqctl set_user_tags grandma administrator
rabbitmqctl set_permissions grandma ".*" ".*" ".*"
rabbitmq-plugins enable rabbitmq_management
