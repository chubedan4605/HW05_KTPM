/*
   Licensed to the Apache Software Foundation (ASF) under one or more
   contributor license agreements.  See the NOTICE file distributed with
   this work for additional information regarding copyright ownership.
   The ASF licenses this file to You under the Apache License, Version 2.0
   (the "License"); you may not use this file except in compliance with
   the License.  You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/
var showControllersOnly = false;
var seriesFilter = "";
var filtersOnlySampleSeries = true;

/*
 * Add header in statistics table to group metrics by category
 * format
 *
 */
function summaryTableHeader(header) {
    var newRow = header.insertRow(-1);
    newRow.className = "tablesorter-no-sort";
    var cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 1;
    cell.innerHTML = "Requests";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 3;
    cell.innerHTML = "Executions";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 7;
    cell.innerHTML = "Response Times (ms)";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 1;
    cell.innerHTML = "Throughput";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 2;
    cell.innerHTML = "Network (KB/sec)";
    newRow.appendChild(cell);
}

/*
 * Populates the table identified by id parameter with the specified data and
 * format
 *
 */
function createTable(table, info, formatter, defaultSorts, seriesIndex, headerCreator) {
    var tableRef = table[0];

    // Create header and populate it with data.titles array
    var header = tableRef.createTHead();

    // Call callback is available
    if(headerCreator) {
        headerCreator(header);
    }

    var newRow = header.insertRow(-1);
    for (var index = 0; index < info.titles.length; index++) {
        var cell = document.createElement('th');
        cell.innerHTML = info.titles[index];
        newRow.appendChild(cell);
    }

    var tBody;

    // Create overall body if defined
    if(info.overall){
        tBody = document.createElement('tbody');
        tBody.className = "tablesorter-no-sort";
        tableRef.appendChild(tBody);
        var newRow = tBody.insertRow(-1);
        var data = info.overall.data;
        for(var index=0;index < data.length; index++){
            var cell = newRow.insertCell(-1);
            cell.innerHTML = formatter ? formatter(index, data[index]): data[index];
        }
    }

    // Create regular body
    tBody = document.createElement('tbody');
    tableRef.appendChild(tBody);

    var regexp;
    if(seriesFilter) {
        regexp = new RegExp(seriesFilter, 'i');
    }
    // Populate body with data.items array
    for(var index=0; index < info.items.length; index++){
        var item = info.items[index];
        if((!regexp || filtersOnlySampleSeries && !info.supportsControllersDiscrimination || regexp.test(item.data[seriesIndex]))
                &&
                (!showControllersOnly || !info.supportsControllersDiscrimination || item.isController)){
            if(item.data.length > 0) {
                var newRow = tBody.insertRow(-1);
                for(var col=0; col < item.data.length; col++){
                    var cell = newRow.insertCell(-1);
                    cell.innerHTML = formatter ? formatter(col, item.data[col]) : item.data[col];
                }
            }
        }
    }

    // Add support of columns sort
    table.tablesorter({sortList : defaultSorts});
}

$(document).ready(function() {

    // Customize table sorter default options
    $.extend( $.tablesorter.defaults, {
        theme: 'blue',
        cssInfoBlock: "tablesorter-no-sort",
        widthFixed: true,
        widgets: ['zebra']
    });

    var data = {"OkPercent": 99.9938164324307, "KoPercent": 0.006183567569297787};
    var dataset = [
        {
            "label" : "FAIL",
            "data" : data.KoPercent,
            "color" : "#FF6347"
        },
        {
            "label" : "PASS",
            "data" : data.OkPercent,
            "color" : "#9ACD32"
        }];
    $.plot($("#flot-requests-summary"), dataset, {
        series : {
            pie : {
                show : true,
                radius : 1,
                label : {
                    show : true,
                    radius : 3 / 4,
                    formatter : function(label, series) {
                        return '<div style="font-size:8pt;text-align:center;padding:2px;color:white;">'
                            + label
                            + '<br/>'
                            + Math.round10(series.percent, -2)
                            + '%</div>';
                    },
                    background : {
                        opacity : 0.5,
                        color : '#000'
                    }
                }
            }
        },
        legend : {
            show : true
        }
    });

    // Creates APDEX table
    createTable($("#apdexTable"), {"supportsControllersDiscrimination": true, "overall": {"data": [0.9992818578933488, 500, 1500, "Total"], "isController": false}, "titles": ["Apdex", "T (Toleration threshold)", "F (Frustration threshold)", "Label"], "items": [{"data": [0.9976163095376732, 500, 1500, "TC_E2E_Mua_hang"], "isController": true}, {"data": [0.9997670524859867, 500, 1500, "API05_Checkout_txn"], "isController": false}, {"data": [0.9994420373089841, 500, 1500, "API01_Login_auth"], "isController": false}, {"data": [0.9996324853812874, 500, 1500, "API04_Add_to_cart_txn"], "isController": false}, {"data": [0.9996107902050081, 500, 1500, "API03_Product_detail_read"], "isController": false}, {"data": [0.9996218566836831, 500, 1500, "API02_Search_products_read"], "isController": false}]}, function(index, item){
        switch(index){
            case 0:
                item = item.toFixed(3);
                break;
            case 1:
            case 2:
                item = formatDuration(item);
                break;
        }
        return item;
    }, [[0, 0]], 3);

    // Create statistics table
    createTable($("#statisticsTable"), {"supportsControllersDiscrimination": true, "overall": {"data": ["Total", 1374611, 85, 0.006183567569297787, 32.71155330489882, 0, 3932, 83.0, 108.0, 114.0, 135.0, 2861.4599032448773, 1626.581790233884, 1067.3347556428346], "isController": false}, "titles": ["Label", "#Samples", "FAIL", "Error %", "Average", "Min", "Max", "Median", "90th pct", "95th pct", "99th pct", "Transactions/s", "Received", "Sent"], "items": [{"data": ["TC_E2E_Mua_hang", 274784, 85, 0.030933387679049726, 163.3860959881235, 0, 4167, 379.0, 440.0, 456.0, 489.9900000000016, 571.8888206707807, 1625.0915741386307, 1066.5676591751044], "isController": true}, {"data": ["API05_Checkout_txn", 274740, 0, 0.0, 36.36717259954836, 0, 3898, 88.0, 108.0, 114.0, 141.0, 572.2867724559131, 177.0385207703656, 233.74337537025542], "isController": false}, {"data": ["API01_Login_auth", 275108, 18, 0.00654288497608212, 37.08738386379176, 0, 3928, 88.0, 108.0, 114.0, 142.0, 572.6894805976115, 364.5134293540881, 227.43634615844988], "isController": false}, {"data": ["API04_Add_to_cart_txn", 274819, 10, 0.0036387586011156436, 17.072746061953502, 0, 3901, 35.0, 61.0, 65.0, 76.0, 572.3523764102158, 164.32773307090181, 237.76645662902968], "isController": false}, {"data": ["API03_Product_detail_read", 274916, 31, 0.011276171630607167, 36.52717193615493, 0, 3932, 88.0, 108.0, 114.0, 143.0, 572.5245844284043, 250.6078770165531, 180.36200214515017], "isController": false}, {"data": ["API02_Search_products_read", 275028, 26, 0.009453582907922102, 36.4955168201057, 0, 3908, 88.0, 107.0, 114.0, 140.0, 572.6445363821296, 670.5582041554926, 188.41883214335166], "isController": false}]}, function(index, item){
        switch(index){
            // Errors pct
            case 3:
                item = item.toFixed(2) + '%';
                break;
            // Mean
            case 4:
            // Mean
            case 7:
            // Median
            case 8:
            // Percentile 1
            case 9:
            // Percentile 2
            case 10:
            // Percentile 3
            case 11:
            // Throughput
            case 12:
            // Kbytes/s
            case 13:
            // Sent Kbytes/s
                item = item.toFixed(2);
                break;
        }
        return item;
    }, [[0, 0]], 0, summaryTableHeader);

    // Create error table
    createTable($("#errorsTable"), {"supportsControllersDiscrimination": false, "titles": ["Type of error", "Number of errors", "% in errors", "% in all samples"], "items": [{"data": ["The operation lasted too long: It took 2,564 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,908 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,921 milliseconds, but should not have lasted longer than 3,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 2,627 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,239 milliseconds, but should not have lasted longer than 3,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 2,653 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,217 milliseconds, but should not have lasted longer than 3,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,031 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,364 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 2, 2.3529411764705883, 1.454957075128891E-4], "isController": false}, {"data": ["The operation lasted too long: It took 3,499 milliseconds, but should not have lasted longer than 3,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,661 milliseconds, but should not have lasted longer than 3,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,401 milliseconds, but should not have lasted longer than 3,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 2,937 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,619 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,233 milliseconds, but should not have lasted longer than 3,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 2,215 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 2,759 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,460 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,456 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,413 milliseconds, but should not have lasted longer than 3,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,309 milliseconds, but should not have lasted longer than 3,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,513 milliseconds, but should not have lasted longer than 3,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,388 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,861 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,869 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 2,395 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,702 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 2,260 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,055 milliseconds, but should not have lasted longer than 3,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 2,224 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 2,842 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,170 milliseconds, but should not have lasted longer than 3,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,093 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,928 milliseconds, but should not have lasted longer than 3,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 2,144 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 2,638 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,476 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,839 milliseconds, but should not have lasted longer than 3,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 2,100 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 2,572 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 2,883 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 2,740 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 2,844 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,728 milliseconds, but should not have lasted longer than 3,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,805 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,483 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 2,312 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,564 milliseconds, but should not have lasted longer than 3,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,656 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 2,474 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,124 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 2,486 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 2,582 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,843 milliseconds, but should not have lasted longer than 3,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,470 milliseconds, but should not have lasted longer than 3,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,194 milliseconds, but should not have lasted longer than 3,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,319 milliseconds, but should not have lasted longer than 3,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 2,560 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 2,190 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 2,633 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,605 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,781 milliseconds, but should not have lasted longer than 3,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 2,439 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,430 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 2,138 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,264 milliseconds, but should not have lasted longer than 3,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 2,518 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,231 milliseconds, but should not have lasted longer than 3,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,932 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 2,581 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 2, 2.3529411764705883, 1.454957075128891E-4], "isController": false}, {"data": ["The operation lasted too long: It took 3,214 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 2,152 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,354 milliseconds, but should not have lasted longer than 3,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,373 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,654 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,138 milliseconds, but should not have lasted longer than 3,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 2,809 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,442 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,734 milliseconds, but should not have lasted longer than 3,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,901 milliseconds, but should not have lasted longer than 3,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,507 milliseconds, but should not have lasted longer than 3,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 2,868 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}, {"data": ["The operation lasted too long: It took 3,215 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, 1.1764705882352942, 7.274785375644456E-5], "isController": false}]}, function(index, item){
        switch(index){
            case 2:
            case 3:
                item = item.toFixed(2) + '%';
                break;
        }
        return item;
    }, [[1, 1]]);

        // Create top5 errors by sampler
    createTable($("#top5ErrorsBySamplerTable"), {"supportsControllersDiscrimination": false, "overall": {"data": ["Total", 1374611, 85, "The operation lasted too long: It took 3,364 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 2, "The operation lasted too long: It took 2,581 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 2, "The operation lasted too long: It took 2,564 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, "The operation lasted too long: It took 3,908 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, "The operation lasted too long: It took 3,921 milliseconds, but should not have lasted longer than 3,000 milliseconds.", 1], "isController": false}, "titles": ["Sample", "#Samples", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors"], "items": [{"data": [], "isController": false}, {"data": [], "isController": false}, {"data": ["API01_Login_auth", 275108, 18, "The operation lasted too long: It took 3,928 milliseconds, but should not have lasted longer than 3,000 milliseconds.", 1, "The operation lasted too long: It took 3,921 milliseconds, but should not have lasted longer than 3,000 milliseconds.", 1, "The operation lasted too long: It took 3,264 milliseconds, but should not have lasted longer than 3,000 milliseconds.", 1, "The operation lasted too long: It took 3,413 milliseconds, but should not have lasted longer than 3,000 milliseconds.", 1, "The operation lasted too long: It took 3,309 milliseconds, but should not have lasted longer than 3,000 milliseconds.", 1], "isController": false}, {"data": ["API04_Add_to_cart_txn", 274819, 10, "The operation lasted too long: It took 3,728 milliseconds, but should not have lasted longer than 3,000 milliseconds.", 1, "The operation lasted too long: It took 3,781 milliseconds, but should not have lasted longer than 3,000 milliseconds.", 1, "The operation lasted too long: It took 3,233 milliseconds, but should not have lasted longer than 3,000 milliseconds.", 1, "The operation lasted too long: It took 3,901 milliseconds, but should not have lasted longer than 3,000 milliseconds.", 1, "The operation lasted too long: It took 3,843 milliseconds, but should not have lasted longer than 3,000 milliseconds.", 1], "isController": false}, {"data": ["API03_Product_detail_read", 274916, 31, "The operation lasted too long: It took 3,093 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, "The operation lasted too long: It took 2,144 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, "The operation lasted too long: It took 2,627 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, "The operation lasted too long: It took 3,476 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, "The operation lasted too long: It took 2,653 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1], "isController": false}, {"data": ["API02_Search_products_read", 275028, 26, "The operation lasted too long: It took 2,564 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, "The operation lasted too long: It took 3,908 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, "The operation lasted too long: It took 2,638 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, "The operation lasted too long: It took 2,100 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1, "The operation lasted too long: It took 3,031 milliseconds, but should not have lasted longer than 2,000 milliseconds.", 1], "isController": false}]}, function(index, item){
        return item;
    }, [[0, 0]], 0);

});
