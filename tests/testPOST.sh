#!/usr/bin/env bash
for ((i=1; i<=1000; i++));
do
    curl -s -X POST "http://localhost:8080/lab/set/message_broker" --data '{"state" : "on" , "status" : "new"}' -H "Content-Type: application/json"
    curl -s -X POST "http://localhost:8080/lab/set/message_broker" --data '{"state" : "off" , "status" : "new"}' -H "Content-Type: application/json"

done