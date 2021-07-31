
#!/bin/sh

for pp in 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9
	do
		for limit in 1 2 3 4 5
			do 
				qsub -v "pp=$pp,limit=$limit" start_sim.sh
			done
	done
