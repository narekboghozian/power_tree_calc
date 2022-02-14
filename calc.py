# @Author: Narek Boghozian <narekboghozian>
# @Date:   2022-01-19T12:26:41-08:00
# @Last modified by:   narekboghozian
# @Last modified time: 2022-01-20T18:55:52-08:00


# Python 3.9.4

import src.gauge_calc as gc
import json, os, sys
import math as m
import pandas as pd

branching_types = [
	"root",
	"dcc"
]

changes_voltage = [
	"root",
	"dcc"
]

abs_loss = 0.05 # watts
ratio_loss = 0.001 # proportion
rec_gauges = []
standard_gauge_info = pd.read_csv("lib/gauge_info.csv")

def get_args():
	if len(sys.argv) > 2:
		print('You have specified too many arguments')
		sys.exit()
	if len(sys.argv) < 2:
		print('You need to specify the sys file to be used\nEx: python calc.py v0_1')
		sys.exit()
	input_path = "sys/%s.json" % (str(sys.argv[1]))
	print("\n   "+input_path)
	if not os.path.exists(input_path):
		print('The sys file specified does not exist')
		sys.exit()
	return input_path

def load_config():

	with open('config.json', 'r') as f:
		conf = json.load(f)

	abs_loss	= conf["default"]["abs_loss"]["value"]
	ratio_loss	= conf["default"]["ratio_loss"]["value"]

	# Add override within sys file

def find_gauge_power(power, voltage, distance):

	# find target resistance
	## calc power lost from ratio loss and compare to abs loss, take min

	ratio_loss_val = power * ratio_loss

	# find target power loss

	min_loss_val = min(ratio_loss_val, abs_loss)

	current = power / voltage
	# print("V: %f , I: %f , P: %f"%(voltage, current, power))

	target_res = min_loss_val / current
	# use target resistance and distance to find gauge
	# print(min_loss_val)
	# print(target_res)
	rec_gauge = gc.r2g(target_res, distance)
	# print(rec_gauge)
	return (rec_gauge, min_loss_val, target_res, current)

def find_gauge_standard(power, voltage, distance):
	# print("Power: %s, Voltage: %s, distance: %s"%(power, voltage, distance))
	current = power / voltage
	rec_gauge = -100
	ind = -100
	for index, row in standard_gauge_info[::-1].iterrows():
		# print(row["max_amps_chassis"])
		even = False
		awg = row["awg"]
		if awg > 0:
			if awg % 2 == 0:
				even = True
		if (current <= row["max_amps_transmission"]) and (even):
			rec_gauge = row["awg"]
			ind = index
			break
	res = standard_gauge_info.iloc[ind]["ohm_1000_m"] * distance / 1000
	dcr_loss = current ** 2 * res
	# print("res: %s"%(str(standard_gauge_info.iloc[ind]["ohm_1000_m"])))
	return (rec_gauge, dcr_loss, res, current)

def find_branch_power(name, branch, voltage, location):
	type = branch["type"]
	branching = type in branching_types
	branch_power = 0
	# If has branches, use recursion
	if branching:
		new_loc = location.copy()
		new_loc.append(name)
		new_voltage = voltage
		if type in changes_voltage:
			new_voltage = branch["voltage"]
		for sub_branch in branch["branches"]:
			branch_power +=	find_branch_power(sub_branch, branch["branches"][sub_branch], new_voltage, new_loc)
		# divide by efficiency
		branch_power /= (branch["efficiency"] / 100)
		if "quiescent_power" in branch.keys():
			quiescent_power = branch["quiescent_power"]
			branch_power += quiescent_power
	# Else, use stated power
	else:
		branch_power += branch["power"]
	# print("branch power: %s"%(branch_power))
	# Wire DCR stuff

	dist_m = branch["distance"] / 100
	rec_gauge, dcr_loss, opt_res, current = find_gauge_standard(branch_power, voltage, dist_m)
	# full_loc = " > ".join(location) + " > " + name
	full_loc = location.copy()
	full_loc.insert(0, "Supply")
	full_loc = " > ".join(full_loc) + " <-- " + str(int(dist_m*100)) + " cm --> " + name
	temp = {
		"path": full_loc,
		"gauge": m.floor(rec_gauge),
		"dcr": opt_res,
		"current": current
		}
	# rec_gauges.append(full_loc + "  :  " + str(m.floor(rec_gauge)))# + " for " + str(opt_res))
	rec_gauges.append(temp)

	return branch_power + dcr_loss

def main():
	sys_path = get_args()
	load_config()
	system = {}
	with open(sys_path, 'r', encoding = 'utf-8') as f:
		system = json.load(f)
	location = []
	total_power = find_branch_power("root", system["system"], system["system"]["voltage"], location)
	print("\n   Total Power:")
	print("   " + str(round(total_power, 3)) + " (W)")
	print("\n")
	recs = []
	max_name_len = 0
	for rec in rec_gauges:
		recs.append(rec)
		if len(rec["path"]) > max_name_len:
			max_name_len = len(rec["path"])
	max_name_len += 3
	for rec in rec_gauges:
		print("   "+(rec["path"] + " ").ljust(max_name_len, '.') + " " + str(rec["gauge"]) + " AWG .... " + str(round(rec["current"], 2)) + " A" )

	print("\n")

main()
