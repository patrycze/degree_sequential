#!/bin/bash
#PBS -q main
#PBS -l walltime=72:00:00
#PBS -l select=1:ncpus=1:mem=20000MB
#PBS -l software=python
#PBS -m be



module load pandas/0.21.0-intel-2017b-Python-3.6.3

cd /home/jarekj/vr_ext/without_calculate/
source $HOME/jj/bin/activate
source $HOME/jj/bin/activate

pip install networkx

python start_without.py $pp $limit >& wyniki_${pp}_${limit}.txt
deactivate
