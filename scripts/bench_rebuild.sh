#!/usr/bin/env bash
set -Eeuo pipefail
trap 'echo "failed at line $LINENO"' ERR
D=${BENCH_DATA:-/home/user/bench_data}
cd "${BENCH_CODE:-$(dirname "$0")/..}"
[ -s $D/geometries.csv ] || curl -sSfL -o $D/geometries.csv.part https://zenodo.org/api/records/7070952/files/geometries.csv/content && { [ -s $D/geometries.csv ] || mv $D/geometries.csv.part $D/geometries.csv; }
echo "downloaded $(du -h $D/geometries.csv | cut -f1)"
[ -s $D/pick.json ] || python -m wenart.datasets.bench pick $D/geometries.csv $D/pick.json --floors 200
[ -s $D/projects/manifest.json ] || python -m wenart.datasets.bench convert $D/geometries.csv $D/pick.json $D/projects
echo "converted"
python -m wenart.datasets.bench run $D/projects $D/work_${BENCH_TAG:-head} --timeout 900
python -m wenart.datasets.bench report $D/projects $D/work_${BENCH_TAG:-head} $D/bench_${BENCH_TAG:-head}
echo "BENCH DONE"
