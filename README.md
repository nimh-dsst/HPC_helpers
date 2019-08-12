

Simple shell script to run the [bids-validator](https://github.com/bids-standard/bids-validator) command on a directory.


Usage:
`is_bids_dock [directory]`

... which will run:

`docker run -ti --rm -v directory:/data:ro bids/validator /data`


or


Usage:
`is_bids_sing [directory]`

... which will run:

`singularity run -B directory:/data bids-validator-1.2.4.simg /data`

note: you must have access to /data/DSST/containers for the singularity command to work




Note: Both scripts will expand [directory] to its absolute path, so no need to specify full path.

