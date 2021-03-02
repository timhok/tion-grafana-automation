#!/usr/bin/env python3
import sys
import time
import requests
from tion_btle.s3 import S3 as s3device
from flask import Flask, request
import json

tion_mac = 'DE:AD:BE:EF:CA:FE' # change to your breezer mac
fan_speed = 4
low_speed = 2

app = Flask(__name__)
s3 = s3device(tion_mac)

def set_speed(speed):
	try:
		s3.set({'fan_speed': int(speed)})
		print("fan_speed is set to" + speed)
	except Exception as e:
		print("unable to set fan_speed:" + repr(e))

@app.route('/grafana_alert',methods=['POST'])
def webhook_grafana_alert():
	global fan_speed
	data = json.loads(request.data)
	print(data)
	if data['ruleName'] == 'fan_speed':
		target_speed = int(data['message'])
		state = data['state']
		if state == "alerting" and fan_speed < target_speed:
			fan_speed = target_speed
			set_speed(fan_speed, False)
		if state == "ok" and fan_speed >= target_speed:
			if target_speed == 4:
				fan_speed = low_speed
			else:
				fan_speed -= 1
			set_speed(fan_speed, False)
	return "OK"

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8087)