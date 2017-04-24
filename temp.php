<html>
<?php
// Are we processing paramters? 
if (isset($_REQUEST)) {
    // add a reading
    if (array_key_exists("temp", $_REQUEST)) {
        $temp = $_REQUEST['temp'];

        // record current temperature
        $f = fopen("temp_now.txt", "w");
        fputs($f, $temp."\n");
        fclose($f);

        // update history
        $f = fopen('temp_history.csv', 'a');
        preg_match('/([0-9.]+) degrees F at ([0-9-: ]+)/', $temp, $match);
        fputs($f, $match[2].','.$match[1]."\n");
        fclose($f);

        // limit the duration shown in the history graph
        exec('/usr/bin/tail -n 1440 temp_history.csv > '.
            '/tmp/1 && cp /tmp/1 temp_history.csv');

        echo "Ok.";
        exit();
    }
}

// read the current temperature
$f = fopen("temp_now.txt", "r");
if ($f === false) {
    $temp = "unknown";
} else {
    $temp = fgets($f, 80);
}

preg_match("/([0-9.]+) degrees/", $temp, $matches);

// Chris prefers simple outputs
if (array_key_exists("mode", $_REQUEST) && $_REQUEST['mode'] == 'simple') {
    echo "Hello Chris.<p/>";
    echo $temp;
    exit();
}
?>

<head> 
<script type="text/javascript" 
    src="https://www.gstatic.com/charts/loader.js"></script>
<script type="text/javascript">
      google.charts.load('current', {'packages':['gauge', 'corechart']});
      google.charts.setOnLoadCallback(drawChart);

      function drawChart() {

        var data = google.visualization.arrayToDataTable([
          ['Label', 'Value'],
          ['Temp', <?php echo $matches[1]; ?>]
        ]);

        var options = {
          min:50, max:90,
          width: 350, height: 350,
          yellowFrom: 50, yellowTo: 60,
          greenFrom: 60, greenTo: 80,
          redFrom: 80, redTo: 90,
          yellowColor: '#DC3912',
          majorTicks: ['50', '55', '60', '65', '70', '75', '80', 
            '85', '90'],
          minorTicks: 5,
        };

        var chart = new google.visualization.Gauge(
            document.getElementById('chart_div'));

        chart.draw(data, options);
      
        var histData = google.visualization.arrayToDataTable([
        ["Time", "Temperature"],
<?php
      $f = fopen('temp_history.csv', 'r');
      while (($line = fgets($f, 80)) !== false) {
        $data = explode(',', $line);
        $time = explode(' ', $data[0]);
        $time_data = explode(':', $time[1]);
        $now = $time_data[1];
        if ( $now % 20 == 0) {
            print "[\"$time[1]\", $data[1]],\n";
        }
      }
      fclose($f);
?>
      ]);

      var histOptions = {
        title: "Temperature (previous 24 hours)",
        curveType: "function",
        legend: { position: "none" },
      };

      var histChart = new google.visualization.LineChart(
        document.getElementById("history_div"));
      histChart.draw(histData, histOptions);
  }
    </script>
  </head>

<body>
<h1 align="center">TempBerry Pi: Temperature</h1>
<table><tr>
<td><div id="chart_div" style="width: 350px; height: 350px;"></div></td>
<td align="center">
<div id="history_div" style="width: 600px; height: 400px;"></div>
</td>
</tr>
</table>
<p/>
<div style="text-align:center; text-style:italic; font-size: 100%;
margin-top:100px;">
<i>Last reading at 
<?php
$data = explode(' ', $temp);
echo "$data[4] $data[5]";
?></div>
</body>
</html>
