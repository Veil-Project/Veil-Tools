# Snapshot.sh

This script will create a compressed file containing the folders required to sync the Veil wallet.
Script logic:
1. Get the current block number and hash
2. Shutdown the wallet
3. Wait two minutes
4. Check the block hash with the block explorer
5. If the block hash is valid:  
   --   Create a zip file containing: block, chainstate, indexes, zerocoin  
   Else  
   --   Restart the wallet, wait 5 minutes and try again.  
   
6. Sign the zip file  
   The zip file and signed result are located in the export folder  
7. Restart the Veil wallet

Script Retry
---
Should the block hash belong to an orphan the script will rerun itself up to 3 times.
