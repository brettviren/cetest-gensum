
# png needs to look like:
# adcTest_20170613T164258_37_intClock_2MHz.png

{ "adcasic":.[] | {"hostname":.hostname,
		    "timestamp":.timestamp,
		    "version":.sumatra.femb_python_location[29:]|split("/")[0],
		    "board_id":.board_id,
		    "serial":.serial,
		    "femb_config": .sumatra.femb_config_name,
		    "pass":.testResults.pass,
		    "png": [
			(["adcTest",.timestamp,(.serial|tostring),"intClock_1MHz.png"]|join("_")),
			(["adcTest",.timestamp,(.serial|tostring),"intClock_2MHz.png"]|join("_")),
			(["adcTest",.timestamp,(.serial|tostring),"extClock_1MHz.png"]|join("_")),
			(["adcTest",.timestamp,(.serial|tostring),"extClock_2MHz.png"]|join("_"))
		    ],
		    "reldir":[.hostname,"/dsk/1/",.sumatra.datadir[12:]]|add,
		    "localdir":["/dsk/1/data/sync-json/",.hostname,"/dsk/1/",.sumatra.datadir[12:]]|add,
		    "datadir":.sumatra.datadir}}

