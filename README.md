## NIH HPC helper scripts

### is_bids

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

### spersist helpers

The pair of spersist- scripts help create, save, and return to a continuous spersist session.
`spersist-store.sh` is a script that should be kept remotely, whereas `spersist-connect.sh` should be stored locally.

The workflow occurs in two steps:

1. Create an spersist session (this only needs to be done once after each Biowulf reboot)
  * Log onto Biowulf login node: `ssh user@biowulf.nih.gov`
  * Start a tmux session: `tmux`
  * Initiate an spersist session: `spersist --vnc --tunnel`
  * Save your session environment variables: `./spersist-store.sh`

  At this point you can keep your terminal open, or close out. As long as you do not `exit` the session, it will remain open.

2. Connecting to your spersist session
  * Open Terminal
  * Run: `./spersist-connect.sh` from your local machine