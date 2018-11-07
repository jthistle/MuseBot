<?php
	ini_set('display_errors', 1);
	ini_set('display_startup_errors', 1);
	error_reporting(E_ALL);

	define("TOKEN", "temptoken");

	if (!isset($_GET["token"])) {
		http_response_code(501);
		exit;
	}

	$token = $_GET["token"];
	if ($token != TOKEN) {
		http_response_code(501);
		exit;
	}

	$headers = getallheaders();
	$eventType = $headers["X-GitHub-Event"];
	$payload = json_decode(file_get_contents('php://input'));

	echo "Got event: ".$eventType."\n";

	$command = escapeshellcmd("/home/pi/MuseBot/runWebhook.py eventPush");	// THIS ISN't OWKRING
	echo "Executing: $command\n";
	$output = shell_exec($command);
	echo "Output: $output\n";

	
	exit;

?>