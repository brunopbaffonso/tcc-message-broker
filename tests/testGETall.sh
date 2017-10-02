#!/usr/bin/env bash
for ((i=1; i<2000; i++));
do
    curl -sG http://localhost:8080/lab/get/message_broker
done
