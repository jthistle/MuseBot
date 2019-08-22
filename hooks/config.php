<?php
	ini_set('display_errors', 1);
	ini_set('display_startup_errors', 1);
	error_reporting(E_ALL);

    define("BASE_DIR", "/home/james/MuseBot/queue/");

	if (!file_exists(BASE_DIR))
        mkdir(BASE_DIR, 0744);

    include_once("./secrets.php");
?>
