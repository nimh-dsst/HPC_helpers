
This shell script makes running the [bids-validator](https://github.com/bids-standard/bids-validator) on the [NIH HPC system](https://hpc.nih.gov) easier.

**HPC usage note**: Script must be run from a compute node since Singularity is not available on the login node. Use `sinteractive` or `spersist` to connect to an interactive session. See [here](https://hpc.nih.gov/docs/userguide.html) for more information.


Usage: `is_bids [options] directory`

Default usage assumes that you have access to the singularity container housed
in /data/DSST/containers. If you do not have access to this directory, you can
specify your own singularity image using the -simg option.

<pre>
[options]:  
  -h             display this help file and exit  
  -v             specify for `--verbose` option in the validator  
                     default is no verbosity  
  -docker        specify to use the latest docker image instead of singularity    
                    default is no docker (docker is not available on the HPC)  
  -simg image    specify path to singularity image  
                    default is /data/DSST/containers/bids-validator-1.2.5.simg  
</pre>