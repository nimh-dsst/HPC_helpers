#!/usr/bin/env bash

# check if .spersist exists on remote server
ssh ${USER}@biowulf.nih.gov "test -e ~/.spersist"

# download remote .spersist and connect
if [ $? -eq 0 ]; then
	echo
	echo "Updating .spersist..."
	echo
	scp -q ${USER}@biowulf.nih.gov:~/.spersist ~
	echo
	echo "Connecting to session..."
	echo
	source ~/.spersist
	# connect to spersist compute node
	ssh -Y -t -L ${PORT1}:localhost:${PORT1} -L ${PORT_VNC}:localhost:${PORT_VNC} biowulf.nih.gov ssh -Y -t ${SLURMD_NODENAME}
else
	echo
	echo "ERROR: Session information not found in biowulf.nih.gov:~/.spersist"
	echo "Please run 'spersist-store.sh' within spersist session to record session information"
	echo
	exit 1
fi