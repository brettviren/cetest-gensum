{ "feasic": [.[] | {"type":.feasic.type,
		    "label":.feasic.filedir|split("/")[-1],
		    "local_timestamp":.feasic.timestamp,
		    "png":([.params.outlabel,"summaryPlot.png"])|join("-"),
		    "gain":.feasic.config_gain,
		    "base":.feasic.config_base,
		    "shape":.feasic.config_shape,
		    "passed":[.feasic.results[0]["fail"] == "0",
			      .feasic.results[1]["fail"] == "0",
			      .feasic.results[2]["fail"] == "0",
			      .feasic.results[3]["fail"] == "0"],
		   }]
		   
}
