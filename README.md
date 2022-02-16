# power-loss-calc

This script is used to calculate power losses in the system. It will also tell you what the minimum gauge of your wires should be to achieve certain default maximum power losses on those wires.  

Future functionality may be added. See 'To-do' section at the end.

---

## Usage

1. Go to the root directory of this repo
2. To evaluate system v0.1, use the command:  

``` bash
python3 calc.py v0_1
```

---

## Working with sys files

The sys files are where the config for each system is stored. This will tell the script how everything is connected.  

### Data format

![Image of rooted tree](https://www.tutorialspoint.com/discrete_mathematics/images/rooted_tree.jpg "Rooted Tree")

The system is represented as a [rooted tree](https://www.tutorialspoint.com/discrete_mathematics/introduction_to_trees.htm) where the ***root node*** is what the source (battery, power supply, etc...) sees, the ***internal nodes*** represent the components in between (power converters, filters, etc...), and the ***leaf nodes*** represent clients (end devices which are the end users of the power).  

Note: Example rooted tree has symmetrical structure. This is not necessary.

### Node properties

Each node has values associated with it that are necessary to run the script.

#### Required values:
- ***'name'***
	- The thing that goes in the parent nodes 'branches' list
- ***'type'***
	- Will tell script how to treat this node
	- Recognized types:
		- 'client' or 'cli' - End user of power
		- 'dcc' - DC / DC Converter
	- Not required by the 'system' / root node
- ***'voltage'***
	- Required for:
		- DC / DC Converter type nodes
		- The 'system' / root node
- ***'distance'***
	- How long the wire is between this node and its parent node
	- Given in centimeters
- ***'power'*** or ***'branches'***
	- Internal nodes need 'branches' while leaf nodes need 'power'
	- For power, given in watts
- ***'efficiency'***
	- Required for:
		- DC / DC Converter type nodes
	- Given in %

#### Optional values:
- ***'description'***
	- Use this to add a comment to the node
- ***'quiescent_power'***
	- Given in watts

### Sys file example

``` json

{
	"description": "Explain this system here",
	"system":{
		"type":	"root",
		"efficiency": 100,
		"distance":	50,
		"voltage": 12,
		"branches":{
			"computer": {
				"description":"The computer. Model #qwerty123",
				"type": "client",
				"distance": 50,
				"power": 50
			},
			"converter": {
				"description":"A DC / DC Converter",
				"type": "dcc",
				"distance": 15,
				"voltage": 5,
				"efficiency": 80,
				"branches":{
					"camera": {
						"description": "The rear camera",
						"type": "client",
						"distance": 100,
						"power": 2
					},
					"radio": {
						"description": "The controller radio",
						"type": "client",
						"distance": 100,
						"power": 2
					}
				}
			}
		}
	}
}

```

The above example describes a system which looks like this:

```
12v Supply
|
|--- Computer
|
|--- 5v Power Converter
	|
	|--- Camera
	|
	|--- Radio
```

Running the calculator on this system yields:
``` bash

>>> python calc.py test_sys

   sys/test_sys.json

   Total Power:
   55.195 (W)


   Supply > root <-- 50 cm --> computer ............. 14 AWG .... 4.17 A
   Supply > root > converter <-- 100 cm --> camera .. 24 AWG .... 0.4 A
   Supply > root > converter <-- 100 cm --> radio ... 24 AWG .... 0.4 A
   Supply > root <-- 15 cm --> converter ............ 24 AWG .... 0.42 A
   Supply <-- 50 cm --> root ........................ 14 AWG .... 4.59 A

```

---

## To-do

Mostly nice-to-have's. Create an 'issue' to ask for one of these.

- Add base option so that another system can be copied and modified
- Add Min/Nom/Max voltage and to calculate under various conditions
- Add 'lin' - linear regulator node type
- Add 'poe' - power over ethernet node type. This will allow ethernet cable classes rather than gauge sizes to be used.
- Add template nodes so no need to repeat listing for modules used multiple times
- Power profile support
	- Time constant support
	- Convolution to find peak power spikes
- Add 'path_dcr' as alternative to distance.
- Add 'current' option for clients if necessary. Will either use last declared voltage on path or something else...
- Add more node types (as needed)
- Add DC / DC Converter efficiency curve feature
- Separate into descriptions & comments?
- Stop ignoring voltage drop?
- Allow sys file specific overrides to config stuff
- Make it object oriented  

Done:

- Add 'gauge' so path dcr can be calculated from that instead of default loss parameters in config.
- Use only even gauge sizes
