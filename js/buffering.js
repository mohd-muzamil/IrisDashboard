// This script is generates a buffering icon rendering various charts.
function buffering(chart, participantId, toggleText = true) {
    const margin = { left: 25, top: 5, right: 25, bottom: 25 },
        width = $("#" + chart).width(),
        height = $("#" + chart).height()
        xHigh = (width - margin.left - margin.right),
        yHigh = (height - margin.top - margin.bottom)

    const R = 15
    const dR = 0.2 * R
    const speed = 50
    const phi0 = 30
    const color = "RGB(26,97,247)"

    var t0 = Date.now();

    // Create svg
    const svg = d3.select("#" + chart)
        .attr("width", margin.left + width + margin.right)
        .attr("height", margin.top + height + margin.bottom);

    var container = svg.append('g')
        .attr("class", "buffer")
        .attr("transform", `translate(${margin.left + xHigh/2}, ${margin.top + yHigh/2})`);

    function arc(innerRadius, outerRadius) {
        return d3.arc()
            .cornerRadius(R / 10)
            .innerRadius(innerRadius)
            .outerRadius(outerRadius)
            .startAngle(0)
            .endAngle(0.75 * 2 * Math.PI);
    }

    // container.append("path")
    //     .attr("class", "arc1")
    //     .attr("d", arc(R, R + dR))
    //     .attr("fill", color);

    container.append("path")
        .attr("class", "rotate")
        .attr("d", arc(0.666 * R, 0.666 * R + dR))
        .attr("fill", color)
        .attr('transform', "rotate(0)");

    container.append("path")
        .attr("class", "rotate1")
        .attr("d", arc(0.333 * R, 0.333 * R + dR))
        .attr("fill", color)
        .attr('transform', "rotate(45)");

    if (toggleText) {
        container.append("text")
            .attr("dy", 3 * R + "px")
            .text(`Loading data for '${ participantId }'`)
            .style("font-size", 0.75 * R + "px")
            .style("text-anchor", "middle");
    }

    // rotating using css - this code not needed
    // d3.timer(function() {
    //     var delta = Date.now() - t0;
    //     svg.selectAll('.buffer')
    //         .attr('transform', 'rotate(' + (phi0 + delta * speed / 200) + ')');
    //     svg.selectAll('.buffer')
    //         .attr('transform', 'rotate(' + -(phi0 + delta * speed / 150) + ')');
        // svg.selectAll('.arc3')
            // .attr('transform', 'rotate(' + (phi0 + delta * speed / 100) + ')');
    // });
}