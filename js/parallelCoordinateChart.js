/****Importatnt file****/
// This script is used to plot parallel cord charts in third and fourth svg

// d3V4 implementation of code similar to that by Mike Bostock
// https://bl.ocks.org/mbostock/1341021
// https://gist.github.com/kotomiDu/d1fd0fe9397db41f5f8ce1bfb92ad20d
// https://gist.github.com/titipignataro/47135818bad65a439174038227e0eb20

function parallelCord(chart, selectedId, lassoSelectedIds, featurelist) {
    var featuresNames
    var importanceScores

    postForm = { "featureColumns": featurelist }
    $.ajax({
        type: "POST",
        contentType: 'application/json',
        data: JSON.stringify(postForm),
        url: "/featureImportance",
        async: false,
        success: function(data) {
            featuresNames = Object.keys(data);
            importanceScores = Object.values(data);
        }
    })

    var featuresCodes = featuresNames
    var titleText = "Feature comparison View"

    var margin = { left: 30, top: 10, right: 40, bottom: 20 },
        width = Math.floor(+$("#" + chart).width()),
        height = Math.floor(+$("#" + chart).height()),
        xHigh = (width - margin.left - margin.right),
        yHigh = (height - margin.top - margin.bottom)
    deltawidth = xHigh / 4;
    const colorClusters = d3.scaleOrdinal().domain(["Setosa", "Versicolor", "Virginica"]).range(d3.schemeCategory10);
    const featureImportanceScale = d3.scaleSequential(d3.interpolateRdYlBu).domain([1, 0])

    // featureLength = featurelist.length
    // if (featureLength == 2) {
    //     margin.left = margin.left + deltawidth
    //     margin.right = margin.right + deltawidth
    // }
    var x = d3.scalePoint().domain(featuresCodes).range([margin.left, xHigh - margin.right]),
        y = {},
        formatDecimal = d3.format(".0f");

    var line = d3.line(),
        background,
        foreground;

    var svg = d3.select("#" + chart)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    postForm = { "id": selectedId }
    dragging = {}

    d3.csv("fetchAggFeatures")
        .header("Content-Type", "application/json")
        .post(JSON.stringify(postForm),
            function(data) {
                var filteredData = data
                if (lassoSelectedIds.length > 1) {
                    filteredData = data.filter(d => {
                        if (lassoSelectedIds.includes(+d.id))
                            return d
                    })
                }

                // Create a scale and brush for each trait.
                featuresCodes.forEach(function(d) {
                    // Coerce values to numbers.
                    if (d == "id") {
                        // y[d] = d3.scaleOrdinal()
                        //     .domain(date_num)
                        //     .range(d3.range(height, 0, -height/date_num.length));
                        data.forEach(function(p) { p[d] = formatDecimal(p[d]) });
                        y[d] = d3.scaleLinear()
                            .domain(d3.extent(data, function(p) { return +p[d]; }))
                            .range([yHigh, 0])
                    }
                    // else if (d == "date") {
                    //     y[d] = d3.scateTime()
                    //         .domain(p[d])
                    //         .range([0, height]);
                    // }
                    else {
                        data.forEach(function(p) { p[d] = +p[d] });
                        y[d] = d3.scaleLinear()
                            .domain(d3.extent(data, function(p) { return +p[d]; }))
                            .range([yHigh, 0]);
                    }

                    if (true) {
                        // if (feature == "aggregatedFeatures"){ 
                        y[d].brush = d3.brushY()
                            .extent([
                                [-7, y[d].range()[1]],
                                [7, y[d].range()[0]]
                            ]) //刷子范围
                            .on("brush", brush)
                            .on("start", brushstart)
                            .on("end", brush);
                    }
                });


                // Add gray background lines for context.
                background = svg.append("svg:g")
                    .attr("class", "background")
                    .selectAll("path")
                    .data(data)
                    .enter().append("svg:path")
                    .attr("d", path)
                    .attr("stroke", d => colorClusters(d.variety))

                // Add a title.
                var title = svg.append("text")
                    .attr("transform", "translate(" + (-margin.left) + "," + 0 + ")")
                    .attr("x", width / 2)
                    .attr("y", margin.top/2)
                    .style("fill", "rgb(18, 113, 249)")
                    .style("font-size", "15px")
                    .style("font-weight", "normal")
                    .style("text-anchor", "middle")
                    .text(titleText)

                // Add a legend.
                // var legendSequential = d3.legendColor()
                //     .shapePadding(0)
                //     .shapeWidth(20)
                //     .shapeHeight(20)
                //     .cells(10)
                //     .orient("vertical")
                //     .scale(featureImportanceScale);

                // svg.append("g")
                // .attr("class", "legendSequential")
                // .attr("transform", `translate(${xHigh-20}, ${0}) scale(${0.6})`)
                // .call(legendSequential);

                // var legend = svg.selectAll("g.legend")
                //     .data(featuresNames)
                //     .enter().append("svg:g")
                //     .attr("class", "legend")
                //     // .attr("transform", function(d, i) { return "translate(0," + (i * 20 + 584) + ")"; });
                //     .attr("transform", function(d) { return `translate(${x(d)}, ${yHigh + margin.bottom}),rotate(-45)` });

                // *************
                // Color legend.
                var colorScale = d3.scaleQuantize()
                    .domain([ 0, 1 ])
                    .range(["red", "blue", "green"]);

                var colorLegend = d3.legendColor()
                    .labelFormat(d3.format(".2f"))
                    .scale(featureImportanceScale)
                    .cells(10)
                    .shapePadding(-5)
                    .shapeWidth(20)
                    .shapeHeight(20)


                svg.append("g")
                    .attr("transform", `translate(${xHigh-margin.right/2}, ${0}) scale(${0.6})`)
                    .call(colorLegend)
                    .style("opacity", 0.8);
                // *************

                // legend.append("svg:line")
                //     .attr("class", String)
                //     .attr("x2", 8);

                // legend.append("svg:text")
                //     .attr("x", 12)
                //     .attr("dy", ".31em")
                //     .text(function(d) { return d; });

                // featureImportanceScale = d3.scaleLinear().domain([0, 1]).range(["#fee5d9", "#cb181d"])
                // .range(["#f0f0f0", "#636363"])

                // add boxes behind each axis 
                var boxes = svg.selectAll("g.tootltip")
                    .data(featuresNames)
                    .enter()
                    .append("rect")
                    .attr("class", "boxes")
                    .attr("x", function(d) { return x(d)})
                    .attr("y", -margin.top * 0.25)
                    .attr("width", 10)
                    .attr("height", yHigh )
                    // .attr("fill", function(d, i) { return feature == "aggregatedFeatures" ? featureImportanceScale(i / featurelist.length) : "#f0f0f0" })
                    .attr("fill", function(d, i) {
                        return featureImportanceScale(importanceScores[i])
                    })
                    .attr("opacity", 0.8)

                // Add foreground lines.
                foreground = svg.append("svg:g")
                    .attr("class", "foreground")
                    .selectAll("path")
                    .data(filteredData)
                    .enter().append("svg:path")
                    .attr("d", path)
                    // .attr("stroke", "red")
                    .attr("stroke-width", function(d) {
                        // if (feature == "aggregatedFeatures") {
                        return d.id != selectedId ? "0.5px" : "2px";
                        // } else {
                        // return "1.5px"
                        // }
                    })
                    .attr("stroke", function(d) {
                        // if (feature == "aggregatedFeatures") {
                        return d.id != selectedId ? colorClusters(d["variety"]) : "#252525";
                        // return d.id != selectedId ? colorClusters(d.variety) : colorClusters(d.variety);
                        // } else {
                        // return line_color
                        // }

                    })
                    .attr("opacity", function(d) {
                        // if (feature == "aggregatedFeatures") {
                        return d.id == selectedId ? 1 : 0.7;
                        // } else {
                        // return 1
                        // }
                        // //     return (feature == "aggregatedFeatures") ? 2 : 1;
                    })
                    // .attr("class", function(d) { return d.featuresNames; });     can use cluster label to color code the lines


                // Add a group element for each trait.
                var g = svg.selectAll(".featuresCodes")
                    .data(featuresCodes)
                    .enter().append("svg:g")
                    .attr("class", "featuresCodes")
                    .attr("transform", function(d) { return "translate(" + x(d) + ")"; })
                    .call(d3.drag()
                        .subject(function(d) { return { x: x(d) }; })
                        .on("start", function(d) {
                            dragging[d] = x(d);
                            background.attr("visibility", "hidden");
                        })
                        .on("drag", function(d) {
                            dragging[d] = Math.min(width, Math.max(0, d3.event.x));
                            foreground.attr("d", path);
                            featuresCodes.sort(function(a, b) { return position(a) - position(b); });
                            x.domain(featuresCodes);
                            g.attr("transform", function(d) { return "translate(" + position(d) + ")"; })
                        })
                        .on("end", function(d) {
                            delete dragging[d];
                            transition(d3.select(this)).attr("transform", "translate(" + x(d) + ")");
                            transition(foreground).attr("d", path);
                            background
                                .attr("d", path)
                                .transition()
                                .delay(500)
                                .duration(0)
                                .attr("visibility", null);
                        })
                    );

                // Add an axis and title.
                g.append("svg:g")
                    .attr("class", "axis")
                    .each(function(d) { d3.select(this).call(d3.axisLeft(y[d])); })
                    .append("svg:text")
                    .attr("text-anchor", "middle")
                    .style("font-size", "15px")
                    .attr("y", -0)
                    .attr("transform", `translate(${0}, ${yHigh + margin.bottom * 0.75}) rotate(0)`)
                    .text(d => { return d })

                function position(d) {
                    var v = dragging[d];
                    return v == null ? x(d) : v;
                }

                function transition(g) {
                    return g.transition().duration(500);
                    ``
                }
                // Returns the path for a given data point.
                function path(d) {
                    return line(featuresCodes.map(function(p) {
                        return [position(p), y[p](d[p])];
                    }));
                }

                function dragstart(d) {
                    i = featuresCodes.indexOf(d);
                }

                function drag(d) {
                    x.range()[i] = d3.event.x; //unsovled issue
                    featuresCodes.sort(function(a, b) { return x(a) - x(b); });
                    g.attr("transform", function(d) { return "translate(" + x(d) + ")"; });
                    foreground.attr("d", path);
                }

                function dragend(d) {
                    //x.domain(featuresCodes).rangePoints([0, w]);
                    var t = d3.transition().duration(500);
                    t.selectAll(".trait").attr("transform", function(d) { return "translate(" + x(d) + ")"; });
                    t.selectAll(".foreground path").attr("d", path);
                }


                function brushstart() {
                    d3.event.sourceEvent.stopPropagation();
                }
                // Handles a brush event, toggling the display of foreground lines.
                function brush() {
                    var actives = [];
                    //filter brushed extents
                    svg.selectAll(".brush")
                        .filter(function(d) {
                            return d3.brushSelection(this);
                        })
                        .each(function(d) {
                            actives.push({
                                dimension: d,
                                extent: d3.brushSelection(this)
                            });
                        });

                    //set un-brushed foreground line disappear
                    foreground.classed("fade", function(d, i) {
                        return !actives.every(function(active) {
                            var dim = active.dimension;
                            return active.extent[0] <= y[dim](d[dim]) && y[dim](d[dim]) <= active.extent[1];
                        });
                    });
                }
                foreground.classed("fade", function(d, i) {
                    // console.log(d.id, lassoSelectedIds.includes(d.id))
                    if (lassoSelectedIds.includes(d.id)) {
                        return d
                    }
                });

                d3.select("#" + chart).selectAll('.buffer').remove();
            });
}

function updateParallelCord(chart, selectedId, lassoSelectedIds, featurelist) {
    if (Array.isArray(selectedId)) {
        selectedId = selectedId[0]
    }
    d3.select("#" + chart).selectAll('*').remove(); //clearing the chart before plotting new data
    // buffering(chart, selectedId); //calling method that plots buffering symbol
    parallelCord(chart, selectedId, lassoSelectedIds, featurelist)
}