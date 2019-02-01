graph [
	directed 0
	node [ 
		id 1
		graphics [
			x 2.829088
			y 0.779514
		]
		VertexSize "Small"
		VertexStyle "GrayLevel[0.85`]"
	]
	node [ 
		id 2
		graphics [
			x 2
			y 0.646367
		]
		VertexSize "Small"
		VertexStyle "GrayLevel[0.85`]"
	]
	node [ 
		id 3
		graphics [
			x 2
			y -0.4
		]
		VertexSize "Small"
		VertexStyle "GrayLevel[0.85`]"
	]
	node [ 
		id 4
		graphics [
			x 3.57447
			y 0.1
		]
		VertexSize "Small"
		VertexStyle "GrayLevel[0.85`]"
	]
	node [ 
		id 5
		graphics [
			x 2.831804
			y -0.6
		]
		VertexSize "Small"
		VertexStyle "GrayLevel[0.85`]"
	]
	node [ 
    	id a
  
    	graphics [
      		x -0.25
      		y -0.5
    	]
    	VertexSize "Small"
		VertexStyle "GrayLevel[0.85`]"
  	]
  	node [ 
	    id b
	 
	    graphics [
	    	x -0.587785
	    	y 0
	    ]
	    VertexSize "Small"
		VertexStyle "GrayLevel[0.85`]"
	]
	node [ 
	    id c
	 
	    graphics [
	    	x 0.587785
	    	y -0.809017
	    ]
	    VertexSize "Small"
		VertexStyle "GrayLevel[0.85`]"
	]
	node [ 
	    id d
	 
	    graphics [
	      x 0.951057
	      y -0.2
	    ]
	    VertexSize "Small"
		VertexStyle "GrayLevel[0.85`]"
	]
	node [ 
	    id e
	 
	    graphics [
	    	x 0.2
	    	y 1.
	    ]
	    VertexSize "Small"
		VertexStyle "GrayLevel[0.85`]"
	]	
	edge [ 
	    source 1
	    target 3
	]
	edge [
		source 1
		target 2
	]
	edge [ 
	    source 1
	    target 4
	]
	edge [ 
	    source 2
	    target 3
	]
	edge [ 
	    source 2
	    target 5
	]
	edge [ 
	    source 3
	    target 5
	]
	edge [ 
	    source 4
	    target 5
	]
	edge [ 
	    source a
	    target b
	]
	edge [ 
	    source a
	    target c
	]
	edge [ 
	    source a
	    target d
	]
	edge [ 
	    source b
	    target c
	]
	edge [ 
	    source b
	    target e
	]
	edge [ 
	    source c
	    target e
	]
	edge [ 
	    source d
	    target e
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
	edge [
		source 5
		target e
		fill "#32CD32"
		EdgeStyle 10
	]
]
