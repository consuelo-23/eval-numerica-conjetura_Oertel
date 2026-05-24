#!/bin/bash
#SBATCH --job-name=oertel
#SBATCH --output=logs/%x_%A_%a.out
#SBATCH --error=logs/%x_%A_%a.err
#SBATCH --array=1-20
#SBATCH --time=00:30:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G

set -euo pipefail

# Ajusta estas variables al enviar con --export o editando este archivo.
RUN_NAME="${RUN_NAME:-oertel_${SLURM_ARRAY_JOB_ID:-manual}}"
BASE_DIR="${BASE_DIR:-/mnt/beegfs/home/crodriguez/code/Importante/oertel_runs}"
PROJECT_DIR="${PROJECT_DIR:-/mnt/beegfs/home/crodriguez/version_0}"
OUTDIR="${BASE_DIR}/${RUN_NAME}/results"

N_PER_Z="${N_PER_Z:-5}"
NZ="${NZ:-100}"
ND="${ND:-100}"
N_MUESTRAS="${N_MUESTRAS:-50}"
SEED_OFFSET="${SEED_OFFSET:-0}"
SEED=$((SLURM_ARRAY_TASK_ID + SEED_OFFSET))

mkdir -p "${PROJECT_DIR}/logs" "${OUTDIR}"
cd "${PROJECT_DIR}"

if command -v module >/dev/null 2>&1; then
  module load python 2>/dev/null || true
fi

if [ ! -x ".venv/bin/python" ]; then
  while ! mkdir .venv.lock 2>/dev/null; do
    sleep 2
  done
  trap 'rmdir .venv.lock 2>/dev/null || true' EXIT
  if [ ! -x ".venv/bin/python" ]; then
    python3 -m venv .venv
    . .venv/bin/activate
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
  fi
  rmdir .venv.lock
  trap - EXIT
fi

. .venv/bin/activate

python run_experiment.py \
  --seed "${SEED}" \
  --n-per-z "${N_PER_Z}" \
  --nz "${NZ}" \
  --nd "${ND}" \
  --n-muestras "${N_MUESTRAS}" \
  --outdir "${OUTDIR}"
