#!/bin/bash
homeDir=~
veilBinaryLocation="/usr/local/bin"

### MAINNET ###
veilDataDir="$homeDir/.veil"                   
veilExplorerUrl="https://explorer.veil-project.com/"
testnetPrefix=""
testnetVersion=""

### TESTNET ###
#testnetPrefix="-testnet"
#testnetVersion="testnet4"
#veilDataDir="$homeDir/.veil/$testnetVersion"                   
#veilExplorerUrl="https://testnet.veil-project.com"

exportPath="/var/www/html"                                 
snapDate=$(date --iso-8601)
lastDebug=`tail -n 1 $veilDataDir/debug.log`
blockHash=""
retryCount=0

if [ -z $veilBinaryLocation ] ; then
        echo "veil binary location is not set. Please edit line 3 of this file to correct."
        echo "Example:"
        echo "$homeDir/Downloads/veil-1.0.0/veil-1.0.0/bin/"
        echo "Exiting... " >&2; exit 1
fi

restart_veild () {
        echo "Restarting veild..."    
        sudo $veilBinaryLocation/veild &
        echo "Restarting veild complete" 
        retryCount=$((retryCount + 1))
        echo "Retry number $retryCount"
        sleep 300  #5 minutes - wait 5 minutes to resync
        lastDebug=`tail -n 1 $veilDataDir/debug.log`
}

block=""
while [ "$retryCount" -lt 3  ]; do
        if ! [[ $lastDebug == *"Shutdown: done"* ]]; then
                echo "veild is already running or did not shudown cleanly.  Attempting to stop..."

                block=`$veilBinaryLocation/veil-cli getblockcount`
                blockHash=`$veilBinaryLocation/veil-cli getblockhash $block`

                if ! [[ "$block" =~ ^[0-9]{5,6}$ ]] ; then
                        echo "Error: Block number out of range: $block"
                        block=""
                else
                        echo "Block value confirmed: $block"
                        block="$block"
                fi

                echo "Stopping veild..."
                $veilBinaryLocation/veil-cli stop
                echo "Veild stopped, waiting 2 minutes to check the block hash..."
                sleep 120  #2 minutes - allow time to pass to know if the tip was an orphan
        fi

        lastDebug=`tail -n 1 $veilDataDir/debug.log`
        if ! [[ $lastDebug == *"Shutdown: done"* ]]; then
                echo "Unclean shutdown, can't make snapshot!"
                restart_veild
        fi
        echo "Successfully stopped veild"

        if [ -z $block ] ; then
                echo "Could not determine block number!" 
                restart_veild
        fi

        if [ -z $blockHash ] ; then
                echo "Could not determine block hash!"
                restart_veild   
        fi

        echo "Checking block hash($blockHash) against the explorer"
        blockResponse=$(curl -s "${veilExplorerUrl}/api/block/${blockHash}")
        validBlock=$(echo $blockResponse | grep "error")

        if [ ! -z "${validBlock}" ] ; then
                echo "Last block was an orphan "  
                restart_veild
       else
       break
       fi
       echo "Block valid - ID:$block; Hash: $blockHash"
done

if [ "$retryCount" -gt 2  ]; then
        echo "Unable to create a valid snapshot after 3 attempts, exiting script..." >&2; exit 1
fi

fileName="$snapDate-veil$testnetPrefix-snapshot-$block.zip"

echo "Starting zip process ($filename)..."
7z a -tzip -mx=9 -r $exportPath/$fileName ~/.veil/$testnetVersion/zerocoin ~/.veil/$testnetVersion/blocks ~/.veil/$testnetVersion/chainstate ~/.veil/$testnetVersion/indexes
echo "Zip complete and saved in your .veil data directory"

echo "Signing snapshot..."
shaFileName="sha256sum_${snapDate}_${block}.txt"
sha256sum $exportPath/$fileName > $exportPath/$shaFileName
echo "Snapshot signed ($shaFileName)"   

# Clean up old snaps.
echo "Deleting old snapshots" 
ls -t $exportPath/*.zip | tail -n +3 | xargs rm --
ls -t $exportPath/*.txt | tail -n +3 | xargs rm --
echo "Deleting old snapshots complete"

echo "Restarting veild..."   
sudo $veilBinaryLocation/veild &
echo "veild started, exiting script..." >&2; exit 1






