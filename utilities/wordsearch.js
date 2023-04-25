function choice(list) {
    let n = Math.floor(Math.random() * list.length)
    return list[n]
}

function placeWord(p,grid) {
    for (i=0;i<p.length;i++) {
	grid[p[i][0]][p[i][1]] = p[i][2]
    }
}

function cleanWords(words) { 
    words.sort((a,b)  =>b.length-a.length)
    let wrds = words.map(str => str.toUpperCase())
    return wrds
}


function retry(grid, word) {
    let s = 0
    
    let  directions = [[0,1], [1,0], [1,1]]
    let validPositions = []
    for (let row=0;row<grid.length;row++) {
    	for(let col=0;col<grid[row].length;col++) {
    		if (grid[row][col] =="*" || grid[row][col] == word[0])  {
    				validPositions.push([row,col])
    			}
    		}
    	}

	for (const p of validPositions) {
	    for (const d of directions) {
		let poses = []
		for (let l=0;l<word.length;l++) {
		if (p[0]+l*d[0]>=grid.length || p[1]+l*d[1]>= grid[0].length) {
		    poses.length = 0
		    break
		    
		}
		let pos = grid[p[0]]+l*d[0][p[1]+l*d[1]]
		if (pos == "*" || pos == word[l]) {
			poses.push([p[0]+l*d[0], p[1]+l*d[1]], word[l])
		} else {
		    poses.length = 0
		    break
		}

		}
		if (poses.length == word.length) {
		    placeWord(poses,grid)
		    return [poses, true]
		}

	    }
	}
	return [[], false] 
}





function tryPlaceWord(word, grid, width, height) {
    let tries = 0
    var directions = [[0,1], [1,0], [1,1]]
    var choices = [word, word.split("").reverse().join("")]

    var word = choice(choices)
    let  placed = false
    while (tries<=2000) {
       var direction = directions[ Math.floor(Math.random() * 3)   ]
       var x = Math.floor(Math.random() * width)
       var y = Math.floor(Math.random() * height)
       var ystart = y+word.length > height ?  y-word.length:y  
       var xstart = x+word.length > width ?  x-word.length:x
       var positions = []
       for (let i=0;i<word.length;i++) {
           if (xstart < 0) {
	       break
           }
	   if (ystart<0) {
	       break
	  }
          var xpos = xstart + i * direction[1]
	  var ypos = ystart +i * direction[0]
	  pos = grid[ypos][xpos]
	  if (pos == "*" || pos == word[i]) {
	  	positions[i] = [ypos, xpos, word[i]]
	} else {
	    positions.length = 0
	    break
	}
       }
       if (positions.length == word.length) {
	   placeWord(positions,grid)
	   return true 
       }
    tries+=1
    if (tries==2000) {
	const [poses, added]= retry(grid,word)
	if (added != true) {
	   console.log("could not add  "+word)
	   break
	}

    }
    
    }
}

function show(grid) {
    for (let i=0;i<grid.length;i++) {
	console.log(grid[i].join(" "));
    }
}





function makeGrid(width, height) {
    var grid = []
    for (let i=0;i<height;i++) {
	grid[i] = []
	for (let y=0;y<width;y++) {
	    grid[i][y] = "*"
	}
    }
    return grid
}

function fillGrid(grid) {
    let letters = [
					'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
					'K', 'L', 'M', 'N', 'O', 'P','Q', 'R', 'S', 'T',
					'U', 'V', 'W', 'X', 'Y', 'Z'
				]
    
    for (let row=0;row<grid.length;row++) {
	for (let column=0;column<grid[row].length;column++) {
	   if (grid[row][column]=="*") {
		grid[row][column] = choice(letters)
	   }
	}
    }
}

function main() {
    var width = 16
    var height = 16
    var grid = makeGrid(width, height)
    var words = ["tomato","alex","satisfaction", "maria",
"minimizing", "pedro", "python","excellent","alexander",
"boxer","buldog","jamas", "perdonar","desenmascarar","entregar",
"recibir", "devolver","integrar","retornar","aceptar","pedir", "mirar","sentir"]
    const  wrds = cleanWords(words)
    //console.log(wrds)
    for (let i=0;i<wrds.length;i++) {
	    //console.log(words[i])
        tryPlaceWord(wrds[i],grid,width, height)
        
    }
    //fillGrid(grid)
    show(grid)
}
main()











