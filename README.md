
This simple shell script was primarily written to make running the [bids-validator](https://github.com/bids-standard/bids-validator) on the [NIH HCP system](https://hpc.nih.gov) easier.

Usage: `is_bids [options] directory`

Default usage assumes that you have access to the singularity container housed
in /data/DSST/containers. If you do not have access to this directory, you can
specify your own singularity image using the -simg option.

[options]:
  -h             display this help file and exit
  -v             use for `--verbose` option in the validator
                     default is no verbosity
  -docker        choose to use the latest docker image
                    default is no docker
  -simg image    specify path to singularity image
                    default is /data/DSST/containers/bids-validator-1.2.5.simg
