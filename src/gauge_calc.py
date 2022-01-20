# @Author: Narek Boghozian <narekboghozian>
# @Date:   2022-01-19T14:22:01-08:00
# @Last modified by:   narekboghozian
# @Last modified time: 2022-01-19T20:19:09-08:00

"""
Note:

AWG 0    > 0
AWG 00	 > -1
AWG 000  > -2
AWG 0000 > -3

"""

import math as m



p_cu_meter 	= 	16.78E-9	# Resistivity of copper - Ω x m
p_cu_mm		= 	p_cu_meter * 1000 # Ω x mm

def g2r(gauge_val, distance):
	"""Calculate wire resistance from gauge (AWG) and length (m)
	Returns resistance (Ω)"""
	dia_mm		= 	0.127 * 92 ** ( ( 36 - gauge_val ) / 39)
	a_mm		= 	m.pi * ( dia_mm / 2 ) ** 2
	res			= 	p_cu_mm * distance * 1000 / ( a_mm )
	return res

def r2g(resistance_val, distance):
	"""Calculate wire gauge from resistance (Ω) and length (m)
	Returns gauge (AWG)"""
	a_mm 		= 	resistance_val / ( p_cu_mm * distance * 1000)
	a_mm		= 	p_cu_mm * distance * 1000 / ( resistance_val )
	dia_mm		= 	2 * m.sqrt( a_mm / m.pi )
	awg 		= 	36 - 39 * m.log( dia_mm / 0.127 , 92 )
	return awg






	#
