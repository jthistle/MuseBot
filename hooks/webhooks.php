<?php
	include_once("./config.php");

	if (!isset($_GET["token"])) {
		http_response_code(501);
		exit;
	}

	$token = $_GET["token"];
	if ($token != GITHUB_TOKEN) {
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