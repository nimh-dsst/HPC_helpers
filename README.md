# NIH HPC helper tools

Simple shell scripts for making your life on the [NIH HPC system](https://hpc.nih.gov) easier.


## spersist helpers

The pair of spersist helper scripts store environemnt information about and re-connect to a continuous spersist session.
`spersist-store.sh` is a script that should be kept remotely, whereas `spersist-connect.sh` should be stored locally. 

The workflow occurs in two steps:

1. Create an spersist session (only required once after each Biowulf reboot)
  * Log onto the Biowulf login node: `ssh user@biowulf.nih.gov`
  * Start a tmux session: `tmux`
  * Initiate an spersist session: `spersist --vnc --tunnel`
  * Save your session environment variables using helper script: `spersist-store.sh`

  At this point you can keep your terminal open, or close out. As long as you do not `exit` the session, it will remain open.

  `spersist-store.sh` records relevant session environment variables to `~/.spersist`, which will allow you to re-connect to the session. If you'd like to activate these variables run `source ~/.spersist`. Perhaps unintuitively, the `.spersist` environemnt variables are not preseved when you connect to your spersist session. If you'd like access to these variables (say to run a jupyter notebook), you can source the `.spersist` file or examine the file to manually enter the variables.

2. Connecting to your spersist session
  * Open Terminal
  * Run helper script from your local machine: `spersist-connect.sh`

`spersist-connect.sh` downloads your remote `.spersist` file and uses it to create an ssh tunnel from your local computer to the compute node. Since we used `--vnc` you can also open a TurboVNC Desktop if you so choose.


**Note**: It is in your best interest to set up [ssh keys](https://www.cyberciti.biz/faq/how-to-set-up-ssh-keys-on-linux-unix/) to connect to the system. Otherwise you will need to enter your password three (yes *three*) times to run `spersist-connect.sh`. The purpose of this is not to annoy you but to 1. check if the `.spersist` file exists remotely, 2. download the `.spersist` file, and 3. connect to te compute node.



## is_bids

This shell script helps you run the [bids-validator](https://github.com/bids-standard/bids-validator).

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



