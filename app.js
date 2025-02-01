
// create a heatmap instance
var heatmap = h337.create({
	container: document.getElementById('heatmap'),
	radius: 90,
	// backgroundColor with alpha so you can see through it
	backgroundColor: 'rgba(0, 0, 58, 0.96)'
});

for (let i = 0; i < points_list.length; i++) {
	const point = points_list[i];
	let x = point[0];
	let y = point[1];
	console.log(point)
	heatmap.addData({ x: x, y: y, value: 1 });
};

			