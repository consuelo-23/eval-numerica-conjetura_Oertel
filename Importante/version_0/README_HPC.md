# Ejecucion en Slurm para radio de Oertel

Estos archivos preparan corridas reproducibles para el codigo de `version_0`.
Cada corrida guarda un `.json` legible y un `.npz` con arreglos numericos.

## 1. Subir codigo al HPC

Desde PowerShell en Windows:

```powershell
scp -r "C:\Users\consu\OneDrive\UOH\papers_please\code\Importante\version_0" crodriguez@172.16.105.194:/mnt/beegfs/home/crodriguez/
```

Luego entrar al nodo maestro:

```bash
ssh crodriguez@172.16.105.194
cd /mnt/beegfs/home/crodriguez/version_0
mkdir -p logs
```

## 2. Prueba corta interactiva

Antes de mandar muchas tareas a cola, conviene probar una corrida pequena:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python run_experiment.py --seed 1 --nz 10 --nd 10 --n-muestras 5 --outdir test_results
```

Si esto termina y escribe un JSON, el flujo base esta bien.

## 3. Enviar barrido con Slurm

El script `slurm_oertel_array.sbatch` usa un job array. Por defecto corre semillas
`1..20`, con `NZ=100`, `ND=100`, `N_MUESTRAS=50` y `N_PER_Z=5`.

```bash
sbatch slurm_oertel_array.sbatch
```

Para ajustar el tamano de la prueba sin editar el archivo:

```bash
sbatch --array=1-100 --export=ALL,RUN_NAME=oertel_n100,NZ=100,ND=100,N_MUESTRAS=50,N_PER_Z=5 slurm_oertel_array.sbatch
```

Para una prueba rapida:

```bash
sbatch --array=1-5 --export=ALL,RUN_NAME=oertel_smoke,NZ=20,ND=20,N_MUESTRAS=10 slurm_oertel_array.sbatch
```

Los resultados quedan en:

```bash
/mnt/beegfs/home/crodriguez/oertel_runs/<RUN_NAME>/results
```

Los logs quedan en:

```bash
/mnt/beegfs/home/crodriguez/version_0/logs
```

## 4. Revisar estado

```bash
squeue -u crodriguez
sacct -j <JOB_ID> --format=JobID,JobName,State,Elapsed,MaxRSS
tail -f logs/oertel_<JOB_ID>_1.out
```

## 5. Crear CSV resumen

Cuando termine el array:

```bash
source .venv/bin/activate
python aggregate_results.py \
  --results-dir /mnt/beegfs/home/crodriguez/oertel_runs/<RUN_NAME>/results \
  --output /mnt/beegfs/home/crodriguez/oertel_runs/<RUN_NAME>/summary.csv
```

## 6. Descargar resultados

Desde PowerShell en Windows:

```powershell
scp -r crodriguez@172.16.105.194:/mnt/beegfs/home/crodriguez/oertel_runs/<RUN_NAME> "C:\Users\consu\OneDrive\UOH\papers_please\code\Importante\version_0\hpc_results\"
```

## Notas

- No guardes tu password en scripts.
- Si Kutral usa un nombre especifico de particion o cuenta Slurm, agrega al `.sbatch` una linea como `#SBATCH --partition=<particion>` o `#SBATCH --account=<cuenta>`.
- El costo escala aproximadamente con `n_candidatos * NZ * ND`, asi que primero prueba mallas pequenas.
