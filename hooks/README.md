# Hooks

## What are these?

These handle notifications from MuseBot's webhook integrations. Currently, these come from Travis CI, and from GitHub (pull requests and pushes).

## Why PHP?

I wrote these in PHP originally, and can't be bothered to rewrite them in something better like Node.js or Python.

## How do I configure this?

Add a file called secrets.php with something like this in it:

```php
<?php
    define("GITHUB_TOKEN", "your_token_goes_here");

    // You may also want to change the webhooks directory. You can do that here.
    // If you do, make sure to update lib/config.py
    define("BASE_DIR", "/your/directory/name/here/");
?>
```

Then copy the entire hooks directory to `/var/www/`, or somewhere in there. Point your webhooks at the relevant
addresses. It should work fine.

The server these are stored on _must_ be the same one running MuseBot. It must also have a port open and forwarded to allow HTTP connections.
