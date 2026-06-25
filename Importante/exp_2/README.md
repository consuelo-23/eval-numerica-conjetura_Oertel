# exp_2

Experiment folder for rerunning the Oertel tests with candidate diagnostics.

Each run stores the original outputs:

- `vertices`
- `ordenados`
- `candidatos`
- `best_cp`
- `best_f`
- `best_u`

It also stores analysis fields:

- `v0`, `v1`, `v2`, `va`
- `best_candidate_index`
- `best_candidate_type`
- `best_t`
- `cara_cp`
- `t_v1_va`
- `f_v0`, `f_v1`, `f_v2`, `f_va`
- comparison against `1/(2e)` for the current `n=1` setup

## Local smoke test

```bash
python run_experiment.py --seed 1 --n-per-z 5 --nz 10 --nd 10 --n-muestras 5 --outdir results_smoke
python aggregate_results.py --results-dir results_smoke --output summary_smoke.csv
```

## Slurm

```bash
sbatch --array=1-100 slurm_oertel_array.sbatch
```

Example with explicit parameters:

```bash
sbatch --array=1-100 --export=ALL,RUN_NAME=oertel_exp2_n100,SEED_OFFSET=0,N_PER_Z=5,NZ=100,ND=100,N_MUESTRAS=50 slurm_oertel_array.sbatch
```

After the array finishes:

```bash
python aggregate_results.py --results-dir /mnt/beegfs/home/crodriguez/code/Importante/exp_2_runs/oertel_exp2_n100/results --output /mnt/beegfs/home/crodriguez/code/Importante/exp_2_runs/oertel_exp2_n100/summary.csv
```

