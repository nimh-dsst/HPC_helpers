#!/usr/bin/env bash

# check if you're in the right environment
if [[ -z ${PORT1} || -z ${PORT_VNC} || -z ${SLURMD_NODENAME} ]]; then
	echo
	echo "ERROR: Environemnt variables not found"
	echo "Please run 'spersist --vnc --tunnel' prior to running this script"
	echo
	exit 1
else
	cat > ~/.spersist <<-EOM
	export PORT1="${PORT1}"
	export PORT_VNC="${PORT_VNC}"
	export SLURMD_NODENAME="${SLURMD_NODENAME}"
EOM
	echo
	echo "--------------------"
	echo "PORT1 is ${PORT1}"
	echo "PORT_VNC is ${PORT_VNC}"
	echo "NODENAME is ${SLURMD_NODENAME}"
	echo "--------------------"
	echo
	echo "Environment variables written to ~/.spersist"
	echo
	exit 0
fi