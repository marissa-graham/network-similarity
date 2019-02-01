graph [
	directed 0
	node [ 
		id 1
		graphics [
			x -0.5
			y 0
		]
		VertexSize "Small"
		VertexStyle "GrayLevel[0.85`]"
	]
	node [ 
		id 2
		graphics [
			x 0
			y -0.5
		]
		VertexSize "Small"
		VertexStyle "GrayLevel[0.85`]"
	]
	node [ 
		id 3
		graphics [
			x 0.5
			y 0
		]
		VertexSize "Small"
		VertexStyle "GrayLevel[0.85`]"
	]
	node [ 
		id 4
		graphics [
			x 0
			y 0.5
		]
		VertexSize "Small"
		VertexStyle "GrayLevel[0.85`]"
	]
	node [ 
    	id a
    	graphics [
      		x 1
      		y 0.25
    	]
    	VertexSize "Small"
		VertexStyle "GrayLevel[0.85`]"
  	]
  	node [ 
	    id b
	    graphics [
	    	x 1.5
	    	y -0.25
	    ]
	    VertexSize "Small"
		VertexStyle "GrayLevel[0.85`]"
	]
	node [ 
	    id c
	    graphics [
	    	x 2
	    	y 0.25
	    ]
	    VertexSize "Small"
		VertexStyle "GrayLevel[0.85`]"
	]
	node [ 
	    id d
	    graphics [
	      x 1.5
	      y 0.75
	    ]
	    VertexSize "Small"
		VertexStyle "GrayLevel[0.85`]"
	]
	edge [
		source 1
		target 2
	]
	edge [
		source 2
		target 3
	]
	edge [ 
	    source 3
	    target 1
	]
	edge [ 
	    source 1
	    target 4
	]
	edge [ 
	    source b
	    target a
	]
	edge [ 
	    source d
	    target a
	]
	edge [ 
	    source b
	    target c
	]
	edge [
		source c
		target d
	]
	edge [
		source 1
		target a
		fill "#32CD32"
		EdgeStyle 10
	]
	edge [
		source 2
		target b
		fill "#32CD32"
		EdgeStyle 10
	]
	edge [
		source 3
		target c
		fill "#32CD32"
		EdgeStyle 10
	]
	edge [
		source 4
		target d
		fill "#32CD32"
		EdgeStyle 10
	]
]
