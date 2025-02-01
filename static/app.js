import HeatmapJS from "./heatmap.js"

// create a heatmap instance
var heatmap = HeatmapJS.h337.create({
	container: document.getElementById('heatmap'),
	radius: 100,
	// backgroundColor with alpha so you can see through it
	backgroundColor: 'rgba(0, 0, 58, 0.96)'
});

// const points_list = [[0,0],[2,3],[3,3]]
const point_list = JSON.parse(document.querySelector("#pl").innerText);

for (let i = 0; i < point_list.length; i++) {
	const point = point_list[i];
	let x = point[0];
	x*=100
	let y = point[1];
	y*=100
	console.log(point)
	heatmap.addData({ x: x, y: y, value: 1 });
};

			