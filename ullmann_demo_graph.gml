graph [
	directed 0
	node [ 
		id "a"
		label "a"
		graphics [
			x 0
			y 0
		]
		VertexSize "Large"
	]
	node [ 
		id "b"
		label "b"
		graphics [
			x 1
			y 0
		]
		VertexSize "Large"
	]
	node [ 
		id "c"
		label "c"
		graphics [
			x 2
			y 0
		]
		VertexSize "Large"
	]
	node [ 
		id "d"
		label "d"
		graphics [
			x 3
			y 0
		]
		VertexSize "Large"
	]
	node [ 
		id 1
		label 1
		graphics [
			x 4
			y 0
		]
		VertexSize "Large"
	]
	node [ 
		id 2
		label 2
		graphics [
			x 5
			y 0
		]
		VertexSize "Large"
	]
	node [ 
		id 3
		label 3
		graphics [
			x 6
			y 0
		]
		VertexSize "Large"
	]
	node [ 
		id 4
		label 4
		graphics [
			x 7
			y 0
		]
		VertexSize "Large"
	]
	node [ 
		id 5
		label 5
		graphics [
			x 8
			y 0
		]
		VertexSize "Large"
	]
	node [ 
		id 6
		label 6
		graphics [
			x 9
			y 0
		]
		VertexSize "Large"
	]
	node [ 
		id 7
		label 7
		graphics [
			x 10
			y 0
		]
		VertexSize "Large"
	]
	node [ 
		id 8
		label 8
		graphics [
			x 11
			y 0
		]
		VertexSize "Large"
	]
	edge [
		source "a"
		target "b"
	]
	edge [
		source "a"
		target "c"
		EdgeShapeFunction "GraphElementData[{CurvedArc, Curvature -> 2}]"
	]
	edge [
		source "c"
		target "b"
	]
	edge [
		source "c"
		target "d"
	]
	edge [
		source 1
		target 2
	]
	edge [
		source 1
		target 6
	]
	edge [
		source 3
		target 2
	]
	edge [
		source 4
		target 5
	]
	edge [
		source 5
		target 6
	]
	edge [
		source 6
		target 7
	]
	edge [
		source 7
		target 8
	]
]

