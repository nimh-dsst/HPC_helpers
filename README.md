

Simple shell script to run the [bids-validator](https://github.com/bids-standard/bids-validator) docker command on a directory:


Usage:
`check_bids [directory]`


... which will run:

`docker run -ti --rm -v directory:/data:ro bids/validator /data`


Note: This script will expand [directory] to its absolute path, so no need to specify full path.

