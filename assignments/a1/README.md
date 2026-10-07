# ECE 750T Assignment 1

Handout: [A1.pdf](A1.pdf). Starter zip: [`A1-starter.zip`](A1-starter.zip).

Python 3.13. From this directory:

```sh
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python check_metrics.py
```

All runs use seed 0 and the supplied settings: 10 epochs, batch size 256, Adam with learning rate \(10^{-3}\), weight decay \(10^{-5}\), and 64 hidden units. `train.py` refuses to overwrite an existing directory.

Written answers and final tables/plots: [report/report.pdf](report/report.pdf). Full-precision JSON and plot PNGs: `results/`. Do not submit `data/`, `.venv/`, `runs/`, or model checkpoints.

## Alpha selection (training set only)

The DP penalty is the squared difference of batch-wise mean sigmoid scores. Candidate strengths were compared with training-set predictions only (no test labels):

```sh
for alpha in 0 0.1 1 3 10 30 100 300 1000; do
  tag=$(printf '%g' "$alpha" | tr '.' 'p')
  python train.py --alpha "$alpha" --seed 0 --out "runs/explore/a${tag}"
  python run_analysis.py --train-metrics "runs/explore/a${tag}"
done
```

| Alpha | Train acc. | Train RW acc. | Train DP gap |
| ---: | ---: | ---: | ---: |
| 0 | 0.8649 | 0.8826 | 0.1773 |
| 0.1 | 0.8637 | 0.8816 | 0.1631 |
| 1 | 0.8607 | 0.8782 | 0.1002 |
| 3 | 0.8531 | 0.8699 | 0.0547 |
| 10 | 0.8462 | 0.8634 | 0.0254 |
| 30 | 0.8346 | 0.8547 | 0.0014 |
| 100 | 0.7999 | 0.8293 | 0.0095 |
| 300 | 0.7602 | 0.7933 | 0.0010 |
| 1000 | 0.7592 | 0.7924 | 0.0000 |

Alpha 0.1 barely changes the gap; 300 and 1000 drive both positive rates near zero. Reported test comparison:

\[
\alpha \in \{0, 1, 3, 10, 30, 100\}.
\]

## Reproduce test tables and plots

```sh
for tag in a0 a1 a3 a10 a30 a100; do
  python evaluate.py "runs/explore/${tag}"
done
python run_analysis.py --q11
python run_analysis.py --q13 runs/explore/a0
python run_analysis.py --q14 \
  runs/explore/a0 runs/explore/a1 runs/explore/a3 \
  runs/explore/a10 runs/explore/a30 runs/explore/a100
```
