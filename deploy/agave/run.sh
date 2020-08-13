#!/bin/bash

#SBATCH -p fn1                                      # Use fn1 partition

#SBATCH -N 1                                        # number of compute nodes
#SBATCH -n 28                                       # number of CPU cores to reserve on this compute node
#SBATCH --mem=256G

#SBATCH -t 1-00:00                                  # wall time (D-HH:MM)
#SBATCH -o slurm.%j.out                             # STDOUT (%j = JobId)
#SBATCH -e slurm.%j.err                             # STDERR (%j = JobId)
#SBATCH --mail-type=ALL                             # Send a notification when a job starts, stops, or fails
#SBATCH --mail-user=bmbrownl@asu.edu                # send-to address

# interactive -n 28 -N 1 --mem=128000 -t 1-00:00    # interactive

java -Xms128G -Xmx200G \
    -cp /home/bmbrownl/icarus/run/matsim.jar \
    org.matsim.run.Controler /home/bmbrownl/icarus/run/input/config.xml
