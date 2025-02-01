# import necessary libraries and functions 
from flask import Flask, request, url_for, render_template # type: ignore
from scipy.optimize import minimize # type: ignore
import numpy as np
from datetime import datetime
import json

# creating a Flask app 
app = Flask(__name__) 

# Block name, length square side, X offset, Y offset, sensors in block (top left, top right, bottom left, bottom right)
blocks = [
		["A", 5.5, 0, 0, [1001, 1002, 1003, 1004]],
		["B", 5.5, 10, 10, [1005, 1006, 1007, 1008]],
	]

path = 'devices.json'
allMacs = []
uniqueMacs = []

point_list = []

P_t = -32	# Transmit power in dBm
n = 4.0 	# Path loss exponent
L_f = 3		# Fixed losses in dB


# on the terminal type: curl http://127.0.0.1:5000/ 
# returns hello world when we use GET. 
# returns the data that we send when we use POST. 
@app.route('/') 
def home():
	return "OK"

# @app.route('/app.js') 
# def js():
	# return render_template("app.js")

@app.route('/current-time', methods = ['GET']) 
def current_time():
	# print(datetime.now().strftime('%H:%M.%S'))
	return datetime.now().strftime('%H:%M.%S')

@app.route('/calibrate', methods = ['GET']) 
def calibrate():
	return n
	
@app.route('/json-post', methods = ['POST']) 
def save_json():
	if request.get_json() is None:
		print("Error receiving POST!")
		return "Nothing received"
	else:
		request_data = request.get_json()

		# Get current POST scannerID
		for item in request_data:
			scanner_id = item.get('scannerID')
			break
		print("Received POST from scanner", scanner_id)
		
		# Read current file
		with open(path, "r") as f:
			data = json.load(f)
		
		# Replace current file with everything except current scannerID
		with open(path, "w") as f:
			f.write("[\n")
			for item in data:
				if scanner_id != item["scannerID"]:
					json.dump(item, f)
					f.write(",\n")

		# Write current scanner data and calculate distance from RSSI
		with open(path, "a") as f:
			entry = 0
			for item in request_data:
				entry += 1

				# RSSI reading
				P_r = item["rssi"]
				
				# Calculate distance
				distance = 10 ** ((P_t - P_r - L_f) / (10 * item["calibration"]))
				item["distance"] = distance

				json.dump(item, f) # Write the updated item dictionary to our file
				if len(request_data) != entry:	# This is not the last entry, so add a comma
					f.write(",\n")
				
			f.write("\n]") # Close the JSON array

		return "OK"

@app.route('/points', methods = ['GET', 'POST']) 
def point_translation():
	point_list.clear()
	uniqueMacs = unique_macs()
	for currentBlock in blocks:
		print("Calculating points for block", currentBlock[0])
		for uniqueMac in uniqueMacs:
			scanners_that_found_mac = scanners_found_mac(uniqueMac)
			scanners_that_found_mac.sort()
			if scanners_that_found_mac == currentBlock[4]:
				d_A = distance_scanner_mac(uniqueMac, currentBlock[4][0])
				d_B = distance_scanner_mac(uniqueMac, currentBlock[4][1])
				d_C = distance_scanner_mac(uniqueMac, currentBlock[4][2])
				d_D = distance_scanner_mac(uniqueMac, currentBlock[4][3])

				L = currentBlock[1]

				# Initial guess
				initial_guess = [L/2, L/2]

				# Minimize the function
				result = minimize(point_angle, initial_guess, args=(L, d_A, d_B, d_C, d_D), method='BFGS')

				# Extract the estimated position
				x, y = result.x
				point = []
				point.append(float(x))
				point.append(float(y))
				point_list.append(point)
	file_path = "history/"+datetime.now().strftime('%y-%m-%d %H:%M:%S')
	f = open(file_path, "w")
	json.dump(point_list, f)
	return render_template('index.html', point_list=point_list)

def unique_macs():
	# Read current file
	unique_macs = []
	with open(path, "r") as f:
		data = json.load(f)
		for item in data:
			if not item["mac"] in unique_macs:
				unique_macs.append(item["mac"])
	return unique_macs


# Return all scanners that found a specific MAC
def scanners_found_mac(mac):
	scanners = []
	with open(path, "r") as f:
		data = json.load(f)
	for item in data:
		if item["mac"] == mac and item["scannerID"] not in scanners:
			scanners.append(item["scannerID"])
	return scanners

# Return the distance to a MAC from a specific scanner
def distance_scanner_mac(mac, scanner):
	with open(path, "r") as f:
		data = json.load(f)
	for item in data:
		if item["mac"] == mac and item["scannerID"] == scanner:
			return item["distance"]

def point_angle(pos, L, d_A, d_B, d_C, d_D):
	x, y = pos
	eq_A = (x**2 + (y - L)**2 - d_A**2)**2
	eq_B = ((x - L)**2 + (y -L)**2 - d_B**2)**2
	eq_C = (x**2 + y**2 - d_C**2)**2
	eq_D = ((x - L)**2 + y**2 - d_D**2)**2
	return eq_A + eq_B + eq_C + eq_D

# Driver function 
if __name__ == '__main__': 
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=False)
