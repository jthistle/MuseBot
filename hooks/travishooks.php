<?php
	include_once("./config.php");

	$headers = getallheaders();
	if (isset($headers["Signature"])) {
		$signature = $headers["Signature"];
		$decodedSig = base64_decode($signature);
	} else {
		exit;
	}

	// get public key
	$ch = curl_init("https://api.travis-ci.org/config");
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
	curl_setopt($ch, CURLOPT_HEADER, 0);

	$result = curl_exec($ch);

	if (curl_error($ch)) {
		file_put_contents(BASE_DIR."error.txt", "Error: ".curl_error($ch));
		exit;
	}

	curl_close($ch);

	if (!$result) {
		file_put_contents(BASE_DIR."error.txt", "Error: no result");
		exit;
	}

	$decodedResult = json_decode($result, true);
	$pubKey = $decodedResult["config"]["notifications"]["webhook"]["public_key"];

	// Get payload
	$payload = file_get_contents('php://input');
	$decodedPayload = trim(urldecode($payload), "payload=");

	// Verify the payload with the public key and the private signature
	$verified = openssl_verify($decodedPayload, $decodedSig, $pubKey);

	if ($verified)
		file_put_contents(BASE_DIR."travis.txt", $decodedPayload);
	else
		file_put_contents(BASE_DIR."unverified.txt", $decodedPayload);

	exit;

?>