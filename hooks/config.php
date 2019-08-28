<?php
	ini_set('display_errors', 1);
	ini_set('display_startup_errors', 1);
	error_reporting(E_ALL);

    include_once("./secrets.php");

	// This must be created and chown'd to the user that handles php requests.
	// This might be www-data, for example, or apache.
	if (BASE_DIR == null)
		define("BASE_DIR", "/home/james/MuseBot/queue/");

?>
