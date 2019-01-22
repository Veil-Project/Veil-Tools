#!/bin/bash
homeDir=~
veilBinaryLocation=""
veilDataDir="$homeDir/.veil"
lastDebug=`tail -n 1 $veilDataDir/debug.log`
snapDate=$(date --iso-8601)

if [ -z $veilBinaryLocation ] ; then
        echo "veil binary location is not set. Please edit line 3 of this file to correct."
        echo "Example:"
        echo "$homeDir/Downloads/veil-1.0.0/veil-1.0.0/bin/"
        echo "Exiting... " >&2; exit 1
fi

if ! [[ $lastDebug == *"Shutdown: done"* ]]; then
        echo "veild is already running or did not shudown cleanly.  Attempting to stop..."

        block=`$veilBinaryLocation/veil-cli getblockcount`

        if ! [[ "$block" =~ ^[0-9]{5,6}$ ]] ; then
                echo "Error: Block number out of range: $block"
                block=""
        else
                echo "Block value confirmed: $block"
                block="-$block"
        fi

        echo "Stopping veild..."
        $veilBinaryLocation/veil-cli stop
        sleep 10
fi

lastDebug=`tail -n 1 $veilDataDir/debug.log`
if ! [[ $lastDebug == *"Shutdown: done"* ]]; then
        echo "Unclean shutdown, can't make snapshot, exiting..." >&2; exit 1
fi

echo "Successfully stopped veild"

if [ -z $block ] ; then
        echo "Could not determine block number.  Will not include in filename"
fi

fileName="veilSnapshot-$snapDate$block.zip"

echo "Starting zip process"
7z a -tzip -mx=9 -r $veilDataDir/$fileName ~/.veil/zerocoin ~/.veil/blocks ~/.veil/chainstate

echo "Completed and saved in your .veil data directory.  Restarting veild..."
$veilBinaryLocation/veild -daemon
