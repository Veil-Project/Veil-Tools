#!/bin/bash
AMOUNT=100
DENOM=10
ADDRESS=svchangemetoyouraddress

[ ! -z "$1" ] && AMOUNT=$1
[ ! -z "$2" ] && DENOM=$2

# Check for zero amount
if [ $AMOUNT -eq 0 ]
then
  echo "ERROR: Amount can't be zero"
  exit
fi

# check denom
fLog=$(echo $DENOM | awk '{printf "%5.10f\n",log($DENOM)/log(10)}')
dLog=${fLog:2}
if [ "$dLog" != "0000000000" ] || [ $DENOM -lt 10 ] || [ $DENOM -gt 10000 ]
then
  echo "ERROR: Denom $DENOM is not correct"
  exit
fi

# check amount
oddLot=$(($AMOUNT % $DENOM))
if [ $oddLot -ne 0 ]
then
  echo "ERROR: Amount ($AMOUNT) must be a multiple of denom ($DENOM)"
  exit
fi

# check destination amount
NEXTDENOM=$(($DENOM*10))
multiple=$(($AMOUNT % $NEXTDENOM))
if [ $multiple -ne 0 ]
then
  echo "ERROR: Amount ($AMOUNT) must be a multiple of destination denom ($NEXTDENOM)"
  exit
fi

echo "Spending $AMOUNT zerocoin"
veil-cli spendzerocoin $AMOUNT false true 100 "$ADDRESS" $DENOM
errorcode=$?
[ $errorcode -eq 0 ] || exit
echo "Waiting 30"
while : ; do
  sleep 30
  echo "Sending to RingCT"
  veil-cli sendstealthtoringct "$ADDRESS" $AMOUNT "" "" true
  errorcode=$?
  [ $errorcode -eq 0 ] && break
  [ $errorcode -eq 6 ] || exit
  echo "Sleeping another 30 seconds"
done
echo "Waiting 660"
sleep 600
while : ; do
  sleep 60
  veil-cli mintzerocoin $AMOUNT
  errorcode=$?
  [ $errorcode -eq 0 ] && break
  [ $errorcode -eq 4 ] || exit
  echo "Sleeping another 60 seconds"
done
