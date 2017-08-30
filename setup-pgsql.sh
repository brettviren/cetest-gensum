mydir=$(dirname $(readlink -f $BASH_SOURCE))
hostname=$(hostname -s)
user=$(id -nu)
export PGSSLCERT=~/.postgresql/${hostname}_${user}.crt
export PGSSLKEY=~/.postgresql/${hostname}_${user}.key
export PGSSLMODE=require
export PGUSER=cetester_${user}
#export PGDATABASE=cetest_${user}
export PGDATABASE=cetest_oper
export PGHOST=hothstor2.phy.bnl.gov

if [ -d venv ] ; then
    source venv/bin/activate
else
    echo "No venv found, make one in $venv"
fi
