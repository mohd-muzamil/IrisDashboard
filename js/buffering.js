/****Importatnt file****/
// This script is used to render buffering icon while loading data

function buffering(chart, participantId, toggleText = true) {
    d3.select("#" + chart).selectAll('*').remove();
    const margin = { left: 10, top: 10, right: 10, bottom: 10 },
        width = $("#" + chart).width(),
        height = $("#" + chart).height()
    const R = Math.round(Math.min(height, width) / 20)
    const dR = 0.2 * R
    const speed = 50
    const phi0 = 30
    const color = "RGB(26,97,247)"
    const dx = width / 2;
    var dy = height / 2
    if (toggleText) { dy = 1 / 3 * height + R }

    var t0 = Date.now();

    // Create svg
    const svg = d3.select("#" + chart)
        .attr("width", margin.left + width + margin.right)
        .attr("height", margin.top + height + margin.bottom);

    var container = svg.append('g')
        .attr("class", "buffer")
        .attr('transform', `translate(${dx}, ${dy})`);

    function arc(innerRadius, outerRadius) {
        return d3.arc()
            .cornerRadius(R / 10)
            .innerRadius(innerRadius)
            .outerRadius(outerRadius)
            .startAngle(0)
            .endAngle(0.85 * 2 * Math.PI);
    }

    container.append("path")
        .attr("class", "arc1")
        .attr("d", arc(R, R + dR))
        .attr("fill", color);

    container.append("path")
        .attr("class", "arc2")
        .attr("d", arc(0.666 * R, 0.666 * R + dR))
        .attr("fill", color)
        .attr('transform', "rotate(90)");

    container.append("path")
        .attr("class", "arc3")
        .attr("d", arc(0.333 * R, 0.333 * R + dR))
        .attr("fill", color)
        .attr('transform', "rotate(180)");

    if (toggleText) {
        container.append("text")
            .attr("dy", 3 * R + "px")
            .text(`Loading data for ${ participantId }...`)
            .style("font-size", 1.5 * R + "px")
            .style("text-anchor", "middle");
    }

    d3.timer(function() {
        var delta = Date.now() - t0;
        svg.selectAll('.arc1')
            .attr('transform', 'rotate(' + (phi0 + delta * speed / 200) + ')');
        svg.selectAll('.arc2')
            .attr('transform', 'rotate(' + (phi0 + delta * speed / 150) + ')');
        svg.selectAll('.arc3')
            .attr('transform', 'rotate(' + (phi0 + delta * speed / 100) + ')');
    });
}