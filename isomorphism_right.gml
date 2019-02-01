Creator "the Wolfram Language : www.wolfram.com"
graph [
	directed 0
	node [ 
		id "a"
		graphics [
			fill "#828FA3"
			outline "#000000"
			x 0
			y 0
		]
		VertexSize "Large"
		VertexStyle "GrayLevel[0.85`]"
	]
	node [ 
		id "b"
		graphics [
			fill "#828FA3"
			outline "#000000"
			x -0.587785
			y -0.809017
		]
		VertexSize "Large"
		VertexStyle "GrayLevel[0.85`]"
	]
	node [ 
		id "c"
		graphics [
			fill "#828FA3"
			outline "#000000"
			x 0.587785
			y -0.809017
		]
		VertexSize "Large"
		VertexStyle "GrayLevel[0.85`]"
	]
	node [ 
		id "d"
		graphics [
			fill "#828FA3"
			outline "#000000"
			x 0.951057
			y 0.309017
		]
		VertexSize "Large"
		VertexStyle "GrayLevel[0.85`]"
	]
	node [ 
		id "e"
		graphics [
			fill "#828FA3"
			outline "#000000"
			x 0
			y 1.
		]
		VertexSize "Large"
		VertexStyle "GrayLevel[0.85`]"
	]
	node [ 
		id 5
		graphics [
			fill "#828FA3"
			outline "#000000"
			x -0.951057
			y 0.309017
		]
		VertexSize "Large"
		VertexStyle "GrayLevel[0.85`]"
	]
	edge [ 
		source "a"
		target "b"
		graphics [
			fill "#828FA3"
		]
	]
	edge [ 
		source "a"
		target "c"
		graphics [
			fill "#828FA3"
		]
	]
	edge [ 
		source "a"
		target "d"
		graphics [
			fill "#828FA3"
		]
	]
	edge [ 
		source "b"
		target "c"
		graphics [
			fill "#828FA3"
		]
	]
	edge [ 
		source "b"
		target 5
		graphics [
			fill "#828FA3"
		]
	]
	edge [ 
		source "c"
		target "e"
		graphics [
			fill "#828FA3"
		]
	]
	edge [ 
		source "d"
		target "e"
		graphics [
			fill "#828FA3"
		]
	]
]
