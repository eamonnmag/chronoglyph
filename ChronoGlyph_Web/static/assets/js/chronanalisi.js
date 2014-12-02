/**
 * Created by eamonnmaguire on 10/02/2014.
 */

var ChronoAnalisi = {};

// Contains the items that have been selected by the user. Key is the item id...value is the object definition
ChronoAnalisi.basket = {};

ChronoAnalisi.motifPaths = {};
ChronoAnalisi.plots = {};
ChronoAnalisi.motifs = {};
ChronoAnalisi.layout_strategy = "distance";

ChronoAnalisi.functions = {
    filter: function (filterInputId, listId) {
        var valThis = $(filterInputId).val().toLowerCase();
        $(listId + '>li').each(function () {
            var text = $(this).text().toLowerCase().trim();
            (text.indexOf(valThis) != -1) ? $(this).show() : $(this).hide();
        });
    },

    removeItemFromBasket: function (id) {
        delete ChronoAnalisi.basket[id];
    },

    updateBasketView: function () {

        this.filterAndShowBasketView("yes");
        this.filterAndShowBasketView("no");

        for (var key in ChronoAnalisi.basket) {
            ChronoAnalisi.functions.render_glyph("#motif-" + ChronoAnalisi.basket[key].name, 30, 30, ChronoAnalisi.basket[key].name);
        }
    },

    filterAndShowBasketView: function (selection) {

        var filteredBasket = {};
        for (var basketItemKey in ChronoAnalisi.basket) {
            if (ChronoAnalisi.basket[basketItemKey].decision == (selection == "yes" ? 1 : -1)) {
                filteredBasket[basketItemKey] = ChronoAnalisi.basket[basketItemKey];
            }
        }

        var html = "There are no items yet...";
        var basketCount = Object.keys(filteredBasket).length;
        if (basketCount > 0) {
            html = "" + basketCount + " items are marked as " + (selection === "yes" ? "accepted" : "not accepted");
        }

        $("#basket-count-" + selection).html(html);

        var source = $("#basket-list-template").html();
        var template = Handlebars.compile(source);
        var html = template({"basket": filteredBasket});

        $('#basket-list-' + selection).html(html);
    },

    changeSelectedIcon: function (name, id) {
        d3.select("#motif-selected-" + name).attr("d", ChronoAnalisi.basket[id].decision == 1 ? ok_path : ChronoAnalisi.basket[id].decision == -1 ? cancel_path : circle_path).transition().delay(100).duration(300).style("fill", ChronoAnalisi.basket[id].decision == 1 ? "#39B54A" : ChronoAnalisi.basket[id].decision == -1 ? "#D25627" : "#ccc");
        d3.select("#path-" + name).style("stroke", ChronoAnalisi.basket[id].decision == 1 ? "#39B54A" : ChronoAnalisi.basket[id].decision == -1 ? "#D25627" : "#ccc");
    },

    toggleItemVisible: function (id, name, count, decision) {

        if (!(id in ChronoAnalisi.basket)) {
            ChronoAnalisi.basket[id] = {"id": id, "name": name, "count": count, "decision": decision}
        } else {
            if (decision != undefined) {
                ChronoAnalisi.basket[id].decision = decision
            } else {
                ChronoAnalisi.basket[id].decision *= -1;
            }

            ChronoAnalisi.functions.toggleHighlightNodeInGraph(name, false);
        }

        this.changeSelectedIcon(name, id);

        if (ChronoAnalisi.layout_strategy === "selection") {
            ChronoAnalisi.graph.updateLinks(ChronoAnalisi.functions.createLinksForSelectedAndNonSelected());
        }

        this.updateBasketView();
    },

    emptyBasket: function () {
        for (var key in ChronoAnalisi.basket) {
            ChronoAnalisi.basket[key].decision = 0;
            this.changeSelectedIcon(ChronoAnalisi.basket[key].name, ChronoAnalisi.basket[key].id);
            this.removeItemFromBasket(key);
        }

        if (ChronoAnalisi.layout_strategy === "selection") {
            ChronoAnalisi.graph.updateLinks(ChronoAnalisi.functions.createLinksForSelectedAndNonSelected());
        }

        this.updateBasketView();
    },

    toggleHighlightNodeInGraph: function (approximation, toggle) {
        d3.select("#motif-node-" + approximation + " rect").style("stroke", toggle ? "#D25627" : "#ccc").style("stroke-width", toggle ? 2 : 1);
    },

    render_glyph: function (placement, width, height, approximation, background) {
        var motif_g = d3.select(placement).append("svg").attr("width", width).attr("height", height).append("g");
        motif_g.append("rect").attr("width", width).attr("height", height).style("fill", background ? background : "#ECF0F1");

        var alphabet_scale = d3.scale.ordinal().domain(["a", "b", "c", "d", "e", "f"]).rangePoints([height - 5, 5]);
        var x = d3.scale.ordinal().domain(d3.range(approximation.length)).rangePoints([0, width], 1);

        motif_g.append("path").attr("d", function () {
                return line(approximation.split('').map(function (p, i) {
                    return [x(i), alphabet_scale(p)];
                }));
            }
        ).style({"stroke": "#414241", "fill": "none", "stroke-linecap": "rounded", "stroke-width": 2});
    },


    plotTimeSeriesFromObject: function (placement, time_series, width, plotHeight, height) {
        var g = d3.select(placement).append("svg").attr("id", time_series.file).attr("width", width).attr("height", plotHeight).append("g");
        var x = d3.scale.ordinal().domain(d3.range(time_series.series.length)).rangePoints([0, width], 1);
        var y = d3.scale.linear().domain([time_series.min, time_series.max]).range([plotHeight - 10, 10]);

        g.append("rect").attr("width", width).attr("height", height).style("fill", "#f6f7f6");
        g.append("text").text(time_series.file).attr({"x": 5, "y": 15}).style({"font-size": ".8em", "fill": "#D25627"});
        g.append("path").attr("d", function () {
                return line(time_series.series.map(function (p, i) {
                    return [x(i), y(p)];
                }));
            }
        ).style({"stroke": "#7F8C8D", "fill": "none", "stroke-linecap": "rounded"});

        g.append("path").attr("d", function () {
            return line([
                [0, y(0)],
                [width, y(0)]
            ])
        }).style({"stroke": "#BDC3C7", "fill": "none", "stroke-linecap": "rounded"});

        // we maintain the x scale to figure out where to plot markers for where glyphs appear later.
        ChronoAnalisi.plots[time_series.file] = {"x": x, "height": plotHeight, "svg": g, "data": time_series.series, "min": time_series.min, "max": time_series.max};
    },

    plotTimeSeriesData: function (placement, dataurl, width, height) {

        d3.json(dataurl, function (timeseries_data) {
            var plotHeight = Math.min(100, height / timeseries_data["time-series"].length);

            for (var data in timeseries_data["time-series"]) {
                var time_series = timeseries_data["time-series"][data];

                ChronoAnalisi.functions.plotTimeSeriesFromObject(placement, time_series, width, plotHeight, height);

            }
        })
    },

    highlightTimeSeriesRegions: function (motifOccurrences) {
        for (var series in motifOccurrences) {
            var file_appearances = motifOccurrences[series];

            var plot_data = ChronoAnalisi.plots[file_appearances.file];
            var x_scale = plot_data.x;
            var height = plot_data.height;
            for (var position in file_appearances.positions) {
                d3.select("#" + file_appearances.file + " g").append("rect").attr("id", "highlight-" + file_appearances.file)
                    .attr("x", x_scale(file_appearances.positions[position][0])).attr("y", 0)
                    .attr("width", (x_scale(file_appearances.positions[position][1]) - x_scale(file_appearances.positions[position][0])))
                    .attr("height", height).style("fill", "#95A5A5").style("opacity", .2);
            }
        }
    },

    unHighlightTimeSeriesRegions: function (motifOccurrences) {
        for (var series in motifOccurrences) {
            var file_appearances = motifOccurrences[series];
            d3.selectAll("#highlight-" + file_appearances.file).transition().duration(500).style("opacity", 0).remove();
        }
    },

    createLinksForSelectedAndNonSelected: function () {
        var links = [];
        var count = 1;
        var seen = [];

        // group the yes, then the no then everything else

        var decisions = [-1, 0, 1];
        for (var decision_index in decisions) {
            for (var key in ChronoAnalisi.basket) {
                if (ChronoAnalisi.basket[key].decision === decisions[decision_index]) {
                    for (var key2 in ChronoAnalisi.basket) {
                        if (ChronoAnalisi.basket[key2].decision === decisions[decision_index]) {
                            if (key != key2) {
                                if (seen.indexOf("s" + key + "t" + key2) == -1 && seen.indexOf("s" + key2 + "t" + key)) {
                                    links.push({"id": count, "source": key, "target": key2})
                                    seen.push("s" + key + "t" + key2)
                                    count++;
                                }
                            }
                        }
                    }
                }
            }
        }

        // everything else
        for (var n_index in nodes) {
            var n1_id = nodes[n_index].id;
            if (!(n1_id in ChronoAnalisi.basket)) {
                for (var n2_index in nodes) {
                    var n2_id = nodes[n2_index].id;
                    if (!(n2_id in ChronoAnalisi.basket)) {
                        if (seen.indexOf(n1_id) != -1) {
                            links.push({"id": count, "source": n1_id, "target": n2_id});
                            seen.push(n1_id);
                            count++;
                        }
                    }
                }
            }
        }

        return links;
    },

    showOptions: function () {
        $("#layout-options").removeClass("hidden")
    },

    hideOptions: function () {
        $("#layout-options").addClass("hidden")
    },

    changeLayoutStrategy: function (type) {

        if (type == 'network') {
            $('#glyph-table').addClass('hidden');
            $('#network').removeClass('hidden');
        } else {
            $('#glyph-table').removeClass('hidden');
            $('#network').addClass('hidden');
            ChronoAnalisi.functions.generate_and_show_table(ChronoAnalisi.functions.create_summary_from_motif(ChronoAnalisi.motifs));
        }

        ChronoAnalisi.layout_strategy = type;
        $("#current-layout").html(type);
    },

    addRefinement: function (parameter, decision) {

        var source = $("#parameter-item-template").html();
        var template = Handlebars.compile(source);

        var min = $("#min-value").val();
        var max = $("#max-value").val();

        var html = template({"parameter_name": parameter, "min": min, "max": max, "symbol": "X",
            "buttontype": decision == 'accept' ? 'green-button' : "orange-button",
            "operation": decision == 'accept' ? 'IFF' : 'SUB'});

        $('#formulai-list').append(html);
        $('.parallel-coords-popup').addClass("hidden");

        for (var approximation in selected_pc_dimensions) {
            this.toggleItemVisible(selected_pc_dimensions[approximation].id, approximation, selected_pc_dimensions[approximation].Frequency, decision == 'accept' ? 1 : -1);
        }
    },

    addModel: function () {
        $("#create_model_modal").modal('show');
    },

    loadModel: function (model_name) {
        $(".model-option").each(function () {
            $("#" + this.id).removeClass("active-model");
        });

        $('#glyph-table').addClass('hidden');
        $('#network').removeClass('hidden');
        $("#" + model_name).addClass("active-model");
        $("#parallel-coords").html('');
        $("#network").html('');
        $("#time-series-plots").html('');
        ParallelCoordinates.rendering.loadAndDraw("#parallel-coords", ["/get_file?model_name=" + model_name + "&file_type=parallel_coords"], 1400, 240, ["Approximation"]);
        ChronoAnalisi.graph.createNetworkVisualization("/get_file?model_name=" + model_name + "&file_type=network", '#network', 650, 400);
        ChronoAnalisi.functions.plotTimeSeriesData("#time-series-plots", "/get_file?model_name=" + model_name + "&file_type=time_series", 300, 350);
    },


    create_summary_from_motif: function (motifs) {
        var summary_representation = [];
        for (var motif in motifs) {
            var motif_representation = {};
            var motif_metrics = motifs[motif].metrics;
            for (var metric in  motif_metrics) {
                motif_representation[motif_metrics[metric].name] = motif_metrics[metric].value;
            }

            motif_representation["approximation"] = motifs[motif].approximation;
            motif_representation["series"] = motifs[motif]["series"];
            summary_representation.push(motif_representation)
        }

        return summary_representation;
    },

    generate_and_show_table: function (to_show) {

        var source = $("#motif-table-item-template").html();
        var template = Handlebars.compile(source);

        var html = template(to_show);

        $('#glyph-table').html(html);
        $('#glyph-table').removeClass('hidden');
        $('#network').addClass('hidden');
//        now populate each of the approximation and time series plots
        for (var approximation in to_show) {
            var approximation = to_show[approximation]["approximation"];
            ChronoAnalisi.functions.render_glyph("#approximation-" + approximation, 50, 40, approximation, "#f6f7f7");
        }
    },

    deleteModel: function (model_name) {
        d3.json('/delete_analysis/' + model_name, function (data) {
            console.log(data.name);
            $("#" + model_name).remove()
        })
    }

}
