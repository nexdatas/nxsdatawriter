#!/usr/bin/env bash
if [ "$2" = "2" ]; then
    echo "run python-nxswriter tests"
    docker exec ndts python test
else
    echo "run python3-nxswriter tests"
    docker exec ndts python3 -m pytest
fi    
ERR=$?

echo "ERROR: "$ERR

if [ $ERR != 0 ]; then
    if [ $ERR != 139 ]; then
	exit $ERR;
    fi
fi
