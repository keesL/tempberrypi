<html>
<?php
// Are we processing parameters?
if (isset($_REQUEST)) {
	// add a reading
	$temp=$hum=$time=0;
	if (array_key_exists("temp", $_REQUEST)) {
		$temp = $_REQUEST['temp'] * 9/5 + 32;
	}
	if (array_key_exists("humidity", $_REQUEST)) {
		$hum = $_REQUEST['humidity'];
	}
	if (array_key_exists("timestamp", $_REQUEST)) {
		$time = $_REQUEST['timestamp'];
	}
	
	if (($hum > 0) || ($temp > 0)) {
		// record current temperature
		$f = fopen("/var/temperature/temp_now.txt", "w");
		fputs($f, "$temp,$hum\n");
		fclose($f);
		
		// update history
		$f = fopen('/var/temperature/temp_history.csv', 'a');
		fputs($f,"$time,$temp,$hum\n");
		fclose($f);
		
		// limit the duration shown in the history graph
		exec('/usr/bin/tail -n 288 /var/temperature/temp_history.csv > '.
		'/tmp/1 && cp /tmp/1 /var/temperature/temp_history.csv');
		
		echo "Ok.";
		exit();
	}
}

// read the current temperature
$f = fopen("/var/temperature/temp_now.txt", "r");
if ($f === false) {
	$data = "unknown";
} else {
	$data = explode(",", fgets($f, 80));
	$temp=$data[0];
	$hum=$data[1];
}

?>

<head>
<script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
<script type="text/javascript">
google.charts.load('current', {'packages':['gauge', 'corechart']});
google.charts.setOnLoadCallback(drawChart);

function drawChart() {
	
	var tempdata = google.visualization.arrayToDataTable([
		['Label', 'Value'],
		['Temp', <?php echo $temp; ?>]
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
	
	var tempchart = new google.visualization.Gauge(
		document.getElementById('tempchart_div'));
		
		tempchart.draw(tempdata, options);
		
		
		
		
		
		var humdata = google.visualization.arrayToDataTable([
			['Label', 'Value'],
			['Hum.%', <?php echo $hum; ?>]
		]);
		
		var options = {
			min:0, max:100,
			width: 350, height: 350,
			yellowFrom: 0, yellowTo: 50,
			greenFrom: 50, greenTo: 75,
			redFrom: 75, redTo: 100,
			yellowColor: '#DC3912',
			majorTicks: ['0', '10', '20', '30', '40', '50', '60', '70', '80',
			'90', '100'],
			minorTicks: 5,
		};
		
		var humchart = new google.visualization.Gauge(
			document.getElementById('humchart_div'));
			
			humchart.draw(humdata, options);
			
			
			
			
			
			
			
			var histData = google.visualization.arrayToDataTable([
				["Time", "Temperature", "Humidity"],
				<?php
				// 2021-09-18 02:30:14.272303,80.6,61.79999923706055
				$f = fopen('/var/temperature/temp_history.csv', 'r');
				while (($line = fgets($f, 80)) !== false) {
					$data = explode(',', $line);
					$time = date_parse($data[0]);
					if ($time['minute'] % 15 == 0) {
						printf("[\"%02.0f:%02.0f\", %.1f, %.1f],\n",
						$time['hour'], $time['minute'],
						$data[1], $data[2]);
					}
				}
				fclose($f);
				?>
			]);
			
			var histOptions = {
				title: "Temperature and Humidity (previous 24 hours)",
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
			<td><div id="tempchart_div" style="width: 400px; height: 400px;"></div></td>
			<td><div id="humchart_div" style="width: 400px; height=400px;"></div></td>
			</tr>
			<tr>
			<td colspan="2"><div id="history_div" style="width: 800px; height: 400px;"></div>
			</td>
			</tr>
			</table>
			<p/>
			<div style="text-align:center; text-style:italic; font-size: 100% margin-top:100px;">
			<i>Last reading at
			</div>
			</body>
			</html>
			
