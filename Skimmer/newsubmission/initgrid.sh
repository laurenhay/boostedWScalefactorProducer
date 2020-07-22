mkdir -p ${HOME}/private/voms
export X509_USER_PROXY=${HOME}/private/voms/x509_voms
voms-proxy-init  --voms cms --valid 200:00:00
GRIDCONTROLDIR=($CMSSW_BASE/src/*/Skimmer/grid-control)
PATHADDITION=$GRIDCONTROLDIR:$GRIDCONTROLDIR/scripts
export PATH=$PATH:$PATHADDITION
