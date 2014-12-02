var fill = d3.scale.category20();

var svg, cursor, nodes, links, node, link, force, placement, zoom, nodeMap = {};
var DEFAULT_COLOR = "#ccc";
var ACCENT_COLOR = "#D25627";
var glyph_width = 40, glyph_height = 50;

var line = d3.svg.line();

var alphabet_scale = d3.scale.ordinal().domain(["a", "b", "c", "d", "e", "f"]).rangePoints([glyph_height - 5, 5]);
var value_color_scale = d3.scale.threshold().domain([10, 50, 100, 1000]).range(["#3B97D3", "#7F8C8D", "#F29C1F", "#D25627", "#E64C3C"]);
var foci = {"no": {x: 50, y: 150}, "yes": {x: 1000, y: 150}, "undefined": {x: 500, y: 150}};

var ok_path = "M17.549,3.011c-4.015-4.015-10.523-4.015-14.538,0c-4.015,4.015-4.015,10.523,0,14.538 c4.015,4.015,10.523,4.015,14.538,0C21.563,13.534,21.564,7.025,17.549,3.011 M16.206,7.751l-7.143,7.143 c-0.106,0.107-0.283,0.107-0.39,0l-4.334-4.335c-0.107-0.106-0.107-0.281,0-0.39l1.791-1.79c0.107-0.107,0.283-0.107,0.39,0 l2.154,2.154c0.107,0.107,0.283,0.107,0.39,0l4.948-4.946c0.106-0.107,0.282-0.108,0.391-0.001l1.802,1.777 C16.312,7.47,16.312,7.645,16.206,7.751"
var cancel_path = "M17.549,3.011c-4.014-4.015-10.523-4.015-14.538,0c-4.015,4.015-4.015,10.523,0,14.538 c4.015,4.015,10.524,4.015,14.538,0S21.563,7.025,17.549,3.011 M13.247,15.026c-0.163,0.164-0.43,0.164-0.593,0l-2.373-2.373 l-2.374,2.373c-0.163,0.164-0.43,0.164-0.593,0l-1.78-1.78c-0.164-0.162-0.164-0.43,0-0.593l2.373-2.374L5.534,7.906 c-0.164-0.164-0.164-0.431,0-0.594l1.78-1.779c0.163-0.164,0.429-0.164,0.593,0l2.374,2.373l2.373-2.373 c0.164-0.164,0.43-0.164,0.593,0l1.78,1.779c0.164,0.163,0.164,0.43,0,0.594l-2.374,2.373l2.374,2.374 c0.164,0.163,0.164,0.431,0,0.593L13.247,15.026z"
var circle_path = "M17.549,3.011c-4.015-4.015-10.523-4.015-14.538,0c-4.015,4.015-4.015,10.523,0,14.538 c4.015,4.015,10.523,4.015,14.538,0C21.563,13.534,21.564,7.025,17.549,3.011"

ChronoAnalisi.graph = {

    // compare function for node or edge to return id 
    // for d3 to compare.
    compare: function (nodeOrEdge) {
        return nodeOrEdge.id;
    },

    createNodeMap: function (nodes) {
        nodes.forEach(function (node) {
            nodeMap[node.id] = node;
        });
    },

    updateNodeMap: function (node, do_delete) {
        if (do_delete) {
            delete nodeMap[node.id];
        } else {
            nodeMap[node.id] = node;
        }
    },

    processLinks: function (linksToProcess) {

        var updated_links = [];
        linksToProcess.forEach(function (link) {

            var source_id = typeof link.source === 'object' ? link.source.id : link.source;
            var target_id = typeof link.target === 'object' ? link.target.id : link.target;

            link.source = nodeMap[source_id];
            link.target = nodeMap[target_id];

            if (link.source && link.target) {
                if (!link.source.children) link.source.children = [];
                link.source.children.push(link.target);

                if (!link.target.parents) link.target.parents = [];
                link.target.parents.push(link.source);

                updated_links.push(link);
            }
        });
        return updated_links;
    },

    path: function (d) {
        if (!d.approximation) d.approximation = "";
        var x = d3.scale.ordinal().domain(d3.range(d.approximation.length)).rangePoints([0, glyph_width], 1);
        return line(d.approximation.split('').map(function (p, i) {
            return [x(i), alphabet_scale(p)];
        }));
    },

    createNetworkVisualization: function (url, place, width, height, callback) {

        placement = place;

        d3.select(placement).html("");

        var x_scale = d3.scale.linear().domain([0, width]).range([0, width]);
        var y_scale = d3.scale.linear().domain([0, height]).range([0, height]);

        d3.json(url, function (json) {

            ChronoAnalisi.graph.createNodeMap(json.nodes);

            ChronoAnalisi.motifs = json.nodes;

            force = d3.layout.force()
                .size([width, height])
                .nodes(json.nodes)
                .friction(.7)
                .linkStrength(1)
                .links(json.links)
                .linkDistance(function (d) {
                    return d.value ? d.value : 400;
                })
                .charge(-300)
                .on("tick", tick);

            window.zoom = d3.behavior.zoom()
                .center([width / 2, height / 2])
                .scaleExtent([0, 10])
                .x(x_scale)
                .y(y_scale)
                .on("zoom", ChronoAnalisi.graph.zoomed);

            svg = d3.select(placement).append("svg")
                .attr("width", width)
                .attr("height", height)
                .append("g")
                .call(zoom)
                .append("g");

            svg.append('svg:rect')
                .attr('width', width)
                .attr('height', height)
                .attr('fill', 'rgba(1,1,1,0)')

            nodes = force.nodes();
            links = force.links();
            node = svg.selectAll(".node");
            link = svg.selectAll(".link");

            if (callback) callback();
            ChronoAnalisi.graph.restart();
        });

        function tick(e) {
            if (ChronoAnalisi.layout_strategy === "selection") {
                var k = .5 * e.alpha;
                nodes.forEach(function (o, i) {
                    var position = o.id in ChronoAnalisi.basket ? ChronoAnalisi.basket[o.id].decision == 1 ? foci.yes : ChronoAnalisi.basket[o.id].decision == -1 ? foci.no : foci.undefined : foci.undefined;
                    o.y += (position.y - o.y) * k;
                    o.x += (position.x - o.x) * k;
                });
            }

            link.attr("x1", function (d) {
                return d.source.x;
            })
                .attr("y1", function (d) {
                    return d.source.y + glyph_height / 2;
                })
                .attr("x2", function (d) {
                    return d.target.x;
                })
                .attr("y2", function (d) {
                    return d.target.y + glyph_height / 2;
                });

            if (ChronoAnalisi.layout_strategy != "distance") {
                link.style("stroke", "#ECF0F1");
            }

            node.attr("cx", function (d) {
                return d.x;
            })
                .attr("cy", function (d) {
                    return d.y;
                })
                .attr("transform", function (d) {
                    return "translate(" + d.x + "," + d.y + ")";
                });
        }
    },

    areNeighbors: function (firstNode, secondNode) {
        return links.some(function (link) {
            return ((link.source.id == firstNode.id && link.target.id == secondNode.id) ||
                (link.source.id == secondNode.id && link.target.id == firstNode.id));
        });
    },

    drawParallelCoordinatesSummary: function (g) {
        g.append("rect")
            .attr("width", glyph_width)
            .attr("height", 15)
            .style({"fill": "#7F8C8D", "stroke": "none"})
            .attr("x", 0).attr("y", glyph_height + 2);

        g.append("path")
            .attr("d", function (d) {
                return ChronoAnalisi.motifPaths[d.approximation];
            })
            .attr("transform", "translate(-2," + (glyph_height + 3) + ") scale(.031)")
            .style({"stroke": "#f1f2f1", "fill": "none", "stroke-width": 40, "stroke-linecap": "round"});
    },

    drawMotifCountInfo: function (g) {

        g.append("rect")
            .attr("width", function (d) {
                return ChronoAnalisi.graph.calculateWidth("8px Helvetica", d.count) + 6;
            })

            .attr("height", 10).attr("x", function (d) {
                return (glyph_width - ChronoAnalisi.graph.calculateWidth("8px Helvetica", d.count) - 6);
            }).attr("y", 0 - 12).style("fill", function (d) {
                return value_color_scale(d.count)
            }).style("stroke", function (d) {
                return value_color_scale(d.count)
            }).attr("rx", 3).attr("ry", 3);

        // draw count label
        g.append("text")
            .text(function (d) {
                return d.count ? d.count : 1;
            }).attr("x", function (d) {
                return (glyph_width - ChronoAnalisi.graph.calculateWidth("8px Helvetica", d.count) - 4);
            }).attr("y", -4).style({"fill": "#fff", "font-size": "9px"});
    },

    plot_detail_line: function (position_array, small_plot_width, plot_g, plot_data, y) {
        var x = d3.scale.ordinal().domain(d3.range(position_array[1] - position_array[0])).rangePoints([0, small_plot_width], 1);
        plot_g.append("path").attr("d", function () {
                return line(plot_data.slice(position_array[0], position_array[1]).map(function (p, i) {
                    return [x(i), y(p)];
                }));
            }
        ).style({"stroke": "#95A5A5", "fill": "none", "stroke-linecap": "rounded", "opacity": .6});
    },

    create_single_detail_graph: function (placement, file, record, small_plot_width) {
        var plot_g = d3.select(placement).append("svg").attr("width", small_plot_width).attr("height", 100).append("g");

        var y = d3.scale.linear().domain([ChronoAnalisi.plots[file].min, ChronoAnalisi.plots[file].max]).range([100, 10]);

        var plot_data = ChronoAnalisi.plots[file].data;

        ChronoAnalisi.graph.plot_detail_line(record["position"], small_plot_width, plot_g, plot_data, y);
        ChronoAnalisi.graph.detail_graph_plot_zero_line(plot_g, y, small_plot_width);
    },


    detail_graph_plot_zero_line: function (plot_g, y, small_plot_width) {
        plot_g.append("text").text("0").attr({"x": 105, "y": y(0) + 3}).style({"font-size": ".8em", "fill": "#D25627"});
        plot_g.append("path").attr("d", function () {
            return line([
                [0, y(0)],
                [small_plot_width, y(0)]
            ])
        }).style({"stroke": "#D25627", "fill": "none", "stroke-linecap": "rounded"});
    },

    create_series_detail_graph: function (placement, d, small_plot_width) {
        var plot_g = d3.select(placement).append("svg").attr("width", small_plot_width).attr("height", 100).append("g");
        var y;
        // finally, render the time series...
        for (var seriesIndex in d.series) {

            var file_appearances = d.series[seriesIndex];
            y = d3.scale.linear().domain([ChronoAnalisi.plots[file_appearances.file].min, ChronoAnalisi.plots[file_appearances.file].max]).range([100, 10]);

            var plot_data = ChronoAnalisi.plots[file_appearances.file].data;
            for (var position in file_appearances.positions) {
                var position_array = file_appearances.positions[position]["position"];
                ChronoAnalisi.graph.plot_detail_line(position_array, small_plot_width, plot_g, plot_data, y);
            }
        }
        ChronoAnalisi.graph.detail_graph_plot_zero_line(plot_g, y, small_plot_width);
    },

    restart: function () {
        links = ChronoAnalisi.graph.processLinks(links);
        force.links(links);

        link = link.data(links, ChronoAnalisi.graph.compare);
        node = node.data(nodes, ChronoAnalisi.graph.compare);

        link.enter()
            .insert("line", ".node")
            .attr("class", "link")
            .style("opacity", .4)
            .style("stroke", function (d) {
                return d.color ? d.color : DEFAULT_COLOR;
            });

        link.exit().remove();

        var g = node.enter()
            .append("g")
            .attr("id", function (d) {
                return "motif-node-" + d.approximation;
            })
            .attr("class", "node")
            .call(force.drag)
            .on("mouseover", function (d) {
                d3.select("#motif-node-" + d.approximation + " rect").transition().duration(400).attr("stroke", "#414241");
                ChronoAnalisi.functions.highlightTimeSeriesRegions(d.series);
            })
            .on("click", function (d) {
                // show panel here
                var source = $("#popup-options-template").html();
                var template = Handlebars.compile(source);
                var html = template({"id": d.id, "name": d.approximation, "count": d.count});

                $('#popup-options').html(html);

                source = $("#motif-stats-template").html();
                template = Handlebars.compile(source);

                var trunc_approximation = d.approximation;
                if (trunc_approximation.length > 25) {
                    trunc_approximation = trunc_approximation.substr(0, 25) + "..."
                }

                $("#popup-approximation").html(trunc_approximation);

                html = template({"metrics": d.metrics});

                $('#motif-stats').html(html);

                d3.select("#popup-series").html("");
                d3.select("#popup-approximation-icon").html("");

                ChronoAnalisi.functions.render_glyph("#popup-approximation-icon", 50, 80, d.approximation, "#ffffff");
                var small_plot_width = 100;
                ChronoAnalisi.graph.create_series_detail_graph("#popup-series", d, small_plot_width);
                d3.select(".popup").style({"top": d3.event.pageY + "px", "left": d3.event.pageX + "px"});
                d3.select(".popup").classed("hidden", false);
                d3.select(".popup").transition().duration(500).style({"opacity": .95});


//                ChronoAnalisi.functions.toggleItemVisible(d.id, d.approximation, d.count, 1);

            })
            .on("mouseout", function (d) {
                d3.select("#motif-node-" + d.approximation + "rect").transition().duration(400).attr("stroke", "#ccc");
                ChronoAnalisi.functions.unHighlightTimeSeriesRegions(d.series);
            });


        g.append("rect")
            .attr("width", glyph_width)
            .attr("height", glyph_height)
            .style({"fill": "#f6f7f6", "stroke": "#ccc", "stroke-width": 1});

        g.append("path")
            .attr("d", function (d) {
                return ChronoAnalisi.graph.path(d);
            })
            .style({"stroke": "#414241", "fill": "none", "stroke-linecap": "rounded"});

        //draw the cancel
        g.append("path")
            .attr("id", function (d) {
                return"motif-selected-" + d.approximation;
            })
            .attr("d", function (d) {

                if (ChronoAnalisi.basket[d.id]) {
                    return ChronoAnalisi.basket[d.id].decision == 1 ? ok_path :
                            ChronoAnalisi.basket[d.id].decision == -1
                        ? cancel_path
                        : circle_path;
                }
                return circle_path;

            }).style("fill", function (d) {

                if (ChronoAnalisi.basket[d.id]) {
                    return ChronoAnalisi.basket[d.id].decision == 1 ? "#39B54A" :
                            ChronoAnalisi.basket[d.id].decision == -1
                        ? "#BE1E2D"
                        : "#ccc";
                }
                return "#ccc";
            })
            .attr("transform", "translate(" + 0 + "," + (-12) + ") scale(.5)");

        this.drawMotifCountInfo(g);
        // showing summary of parallel coordinate system...
        this.drawParallelCoordinatesSummary(g);

        g.append("text")
            .attr("x", 12)
            .attr("dy", ".35em")
            .text(function (d) {
                return d.name;
            })
            .style("fill", "#67686B")
            .style("stroke", "none")
            .style("font-size", function (d) {
                return d.count ? (Math.log(d.count) + 10) + "px" : "10px";
            });

        node.exit().remove();

        force.start();
    },

    addLinks: function (nodeLinks) {
        for (var linkIndex in nodeLinks) {
            links.push(nodeLinks[linkIndex]);
        }
        ChronoAnalisi.graph.restart();
    },

    updateLinks: function (nodeLinks) {
        links = [];
        for (var linkIndex in nodeLinks) {
            links.push(nodeLinks[linkIndex]);
        }
        ChronoAnalisi.graph.restart();
    },

    addNode: function (newNode, nodeLinks) {
        nodes.push(newNode);
        ChronoAnalisi.graph.updateNodeMap(newNode);
        nodeMap[newNode.id] = newNode;
        for (var linkIndex in nodeLinks) {
            links.push(nodeLinks[linkIndex]);
        }

        ChronoAnalisi.graph.restart();
    },

    removeNode: function (nodeId) {

        var nodeObject;
        for (var nodeIndex in nodes) {
            if (nodes[nodeIndex].id == nodeId) {
                nodeObject = nodes[nodeIndex];
                break;
            }
        }
        ChronoAnalisi.graph.updateNodeMap(nodeObject, true);
        nodes.splice(nodeObject.index, 1);
        ChronoAnalisi.graph.spliceLinksForNode(nodeObject);
        ChronoAnalisi.graph.restart();
    },

    spliceLinksForNode: function (node) {
        var toSplice = links.filter(function (l) {
            return (l.source === node || l.target === node);
        });

        toSplice.map(function (l) {
            links.splice(links.indexOf(l), 1);
        });
    },

    zoomed: function () {
        svg.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");

    },

    toggleBrushing: function () {
        var contents = $("#brushOption").html();
        if (contents.indexOf('Turn on') != -1) {

            brushing = true;

            brush = d3.select("svg").append("g")
                .attr("class", "brush")
                .call(d3.svg.brush()
                    .x(window.zoom.x())
                    .y(window.zoom.y())
                    .on("brush", function () {
                        var extent = d3.event.target.extent();
                        d3.selectAll(".node").select("path").classed("selected", function (d) {
                            return d.selected = (extent[0][0] <= d.x && d.x < extent[1][0]
                                && extent[0][1] <= d.y && d.y < extent[1][1]);
                        });
                    })
                    .on("brushend", function () {

                        d3.select(this).call(d3.event.target);
                    }));
            $("#brushOption").html('Turn off brushing');
        } else {
            brushing = false;
            $("#graph-view").css('cursor', 'move');
            d3.select(".brush").remove();
            $("#brushOption").html('Turn on brushing');
            d3.selectAll(".node").select("circle").classed("selected", false);
        }
    },

    calculateWidth: function (font, string) {
        var f = font || '9px Helvetica',
            o = $('<div>' + string + '</div>')
                .css({'position': 'absolute', 'float': 'left', 'white-space': 'nowrap', 'visibility': 'hidden', 'font': f})
                .appendTo($('body')),
            w = o.width();

        o.remove();

        return w;
    }
}
