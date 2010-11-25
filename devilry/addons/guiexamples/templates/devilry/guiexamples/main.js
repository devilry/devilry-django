dojo.require("dojox.charting.Chart2D");
dojo.require("dijit.TitlePane");
dojo.require("dijit.Tree");
dojo.require("dijit.layout.BorderContainer");
dojo.require("dijit.layout.ContentPane");
dojo.require("dijit.form.ComboBox");
dojo.require("dojo.data.ItemFileWriteStore");
dojo.require("dojox.data.QueryReadStore");
dojo.require("dojox.charting.DataSeries");


function init_page() {
	//var main = dojo.byId("main");
	//var help = new dijit.TitlePane({
			//href: "{% url devilry-guiexamples-help %}",
			//title: "Help",
			//open: false});
	//help.startup();
	//main.appendChild(help.domNode);
}

dojo.addOnLoad(init_page);



makeCharts = function() {
    var chart1 = new dojox.charting.Chart2D("simplechart");
    chart1.addPlot("default", {
        type: "Lines"
    });
    chart1.addAxis("x");
    chart1.addAxis("y", {
        vertical: true
    });
    chart1.addSeries("Series 1", [1, 2, 2, 3, 4, 5, 5, 7]);
    chart1.render();
};

function datachart() {
    var store = new dojox.data.QueryReadStore({
        url:"{% url devilry-guiexamples-assignment_avg_data %}"
    });
    var dataseries = dojox.charting.DataSeries(store, {},
        function(s, item) {
            return s.getValue(item, "avg_scaled_points");
        }
    );

    var chart1 = new dojox.charting.Chart2D("datachart");
    chart1.addPlot("default", {
        type: "Columns", gap:5,
    });

    // Create X-axis labels from JSON
    dojo.xhrGet({
        url:"{% url devilry-guiexamples-assignment_avg_labels %}",
        handleAs:"json",
        load: function(labels){
            chart1.addAxis("x", {
                labels: labels
            });
        }
    });

    chart1.addAxis("y", {vertical: true});
    chart1.addSeries("Series 1", dataseries);
    chart1.render();
};

dojo.addOnLoad(makeCharts);
dojo.addOnLoad(datachart);
