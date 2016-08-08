#PBS -N Micro
#PBS -l nodes=1:gpus=1,walltime=12:00:00,qos=flux
#PBS -A rlarson_fluxoe
#PBS -V
#PBS -j oe
#PBS -q fluxoe

cd ${PBS_O_WORKDIR}

###################
# Job status info
echo "Job: ${PBS_JOBNAME}"
echo "Directory: ${PBS_O_WORKDIR}"
echo "Nodes:"
cat $PBS_NODEFILE
echo "-----"
echo ""
###################

###################
# run the job
hoomd run_init_new.py --mode=gpu
hoomd run_flow_new.py --mode=gpu
echo "job done"
