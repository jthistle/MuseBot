<?php
	ini_set('display_errors', 1);
	ini_set('display_startup_errors', 1);
	error_reporting(E_ALL);

	define("TOKEN", "temptoken");
	define("BASE_DIR", "/var/www/html/queue/");

	if (!file_exists(BASE_DIR))
		mkdir(BASE_DIR, 0744);

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
	$payload = file_get_contents('php://input');

	echo "Got event: ".$eventType."\n";
	file_put_contents(BASE_DIR."$eventType.txt", $payload);
	echo "Wrote event file: $payload\n";

	exit;

?>