# @Author: Narek Boghozian <narekboghozian>
# @Date:   2022-01-19T12:26:41-08:00
# @Last modified by:   narekboghozian
# @Last modified time: 2022-01-19T20:22:18-08:00


# Python 3.9.4

import src.gauge_calc as gc
import json
import math as m

branching_types = [
	"root",
	"dcc"
]

changes_voltage = [
	"root",
	"dcc"
]

abs_loss = 0.1 # watts
ratio_loss = 0.01 # proportion

rec_gauges = []

def load_config():

	with open('config.json', 'r') as f:
		conf = json.load(f)

	abs_loss	= conf["default"]["abs_loss"]["value"]
	ratio_loss	= conf["default"]["ratio_loss"]["value"]

	# Add override within sys file

def find_gauge(power, voltage, distance):

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
	return (rec_gauge, min_loss_val, target_res)

def find_branch_power(name, branch, voltage, location):

	# Find info about branch
	# print("\n")
	# print(location)
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



	# Else, use stated power
	else:

		branch_power += branch["power"]

	# Wire DCR stuff

	dist_m = branch["distance"] / 100
	rec_gauge, dcr_loss, opt_res = find_gauge(branch_power, voltage, dist_m)
	# full_loc = " > ".join(location) + " > " + name
	full_loc = location.copy()
	full_loc.insert(0, "Supply")
	full_loc = " > ".join(full_loc) + " <-- " + str(int(dist_m*100)) + " cm --> " + name
	temp = {
		"path": full_loc,
		"gauge": m.floor(rec_gauge),
		"dcr": opt_res
		}
	# rec_gauges.append(full_loc + "  :  " + str(m.floor(rec_gauge)))# + " for " + str(opt_res))
	rec_gauges.append(temp)

	return branch_power + dcr_loss

def main():

	load_config()
	system = {}
	with open('sys/v0_1.json', 'r', encoding = 'utf-8') as f:
		# file = f.read()
		# print(file)
		system = json.load(f)
	# print(system)
	location = []
	total_power = find_branch_power("root", system["system"], 24, location)

	print("\n   Total Power:")
	print("   " + str(total_power))
	print("\n")
	# print(rec_gauges)
	recs = []
	max_name_len = 0
	for rec in rec_gauges:
		recs.append(rec)
		if len(rec["path"]) > max_name_len:
			max_name_len = len(rec["path"])
	max_name_len += 3
	for rec in rec_gauges:
		print("   "+rec["path"].ljust(max_name_len, '.') + "  " + str(rec["gauge"]) + "  ..  " + str(rec["dcr"]) )

	print("\n")

main()
