# ECE 750T Assignment 1

Python 3.13. From this directory:

```sh
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python check_metrics.py
```

All runs use seed 0 and the supplied settings: 10 epochs, batch size 256, Adam with learning rate \(10^{-3}\), weight decay \(10^{-5}\), and 64 hidden units. `train.py` refuses to overwrite an existing directory.

## Alpha range

The penalty is the squared difference between the batch-wise mean sigmoid scores of the two groups. Candidate strengths were compared using training-set predictions only:

```sh
for alpha in 0 0.1 1 3 10 30 100 300 1000; do
  tag=$(printf '%g' "$alpha" | tr '.' 'p')
  python train.py --alpha "$alpha" --seed 0 --out "runs/explore/a${tag}"
  python run_analysis.py --train-metrics "runs/explore/a${tag}"
done
```

| Alpha | Train accuracy | Train reweighted accuracy | Train DP gap |
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

Alpha 0.1 barely changes the gap. Alphas 300 and 1000 drive both positive rates to approximately zero. The reported test comparison therefore uses

\[
\alpha \in \{0, 1, 3, 10, 30, 100\}.
\]

## Test evaluation and tables

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

Values below are rounded to four decimals. `results/` contains the full-precision JSON files and the three plots `q14_accuracy.png`, `q14_rw_accuracy.png`, and `q14_dp_gap.png`.

### Question 1.1, training correlations

| Feature | Correlation with Y | Feature | Correlation with A |
| --- | ---: | --- | ---: |
| marital-status_Married-civ-spouse | 0.4447 | relationship_Husband | 0.5801 |
| relationship_Husband | 0.4010 | marital-status_Married-civ-spouse | 0.4318 |
| education_num | 0.3352 | relationship_Unmarried | -0.3213 |
| marital-status_Never-married | -0.3184 | relationship_Wife | -0.3193 |
| age_u30 | -0.2381 | occupation_Adm-clerical | -0.2631 |
| hours-per-week | 0.2297 | hours-per-week | 0.2293 |
| relationship_Own-child | -0.2285 | marital-status_Divorced | -0.2286 |
| capital-gain | 0.2233 | occupation_Craft-repair | 0.2231 |
| occupation_Exec-managerial | 0.2149 | marital-status_Widowed | -0.1885 |
| relationship_Not-in-family | -0.1885 | marital-status_Never-married | -0.1714 |

### Question 1.2, unregularized test metrics

| Accuracy | Reweighted accuracy | DP gap | Positive rate, A=0 | Positive rate, A=1 |
| ---: | ---: | ---: | ---: | ---: |
| 0.8557 | 0.8738 | 0.1707 | 0.0880 | 0.2587 |

A=1 (Male) has the higher positive-prediction rate.

### Question 1.3, test correlations with predictions

| Subset | Feature | Correlation |
| --- | --- | ---: |
| All | marital-status_Married-civ-spouse | 0.4686 |
| All | education_num | 0.4336 |
| All | relationship_Husband | 0.4177 |
| A=0 | relationship_Wife | 0.5620 |
| A=0 | marital-status_Married-civ-spouse | 0.5273 |
| A=0 | capital-gain | 0.2987 |
| A=1 | education_num | 0.4913 |
| A=1 | relationship_Husband | 0.4151 |
| A=1 | marital-status_Married-civ-spouse | 0.4105 |

### Question 1.4, test metrics

| Alpha | Accuracy | Reweighted accuracy | DP gap |
| ---: | ---: | ---: | ---: |
| 0 | 0.8557 | 0.8738 | 0.1707 |
| 1 | 0.8509 | 0.8678 | 0.0958 |
| 3 | 0.8442 | 0.8599 | 0.0514 |
| 10 | 0.8389 | 0.8554 | 0.0211 |
| 30 | 0.8325 | 0.8516 | 0.0012 |
| 100 | 0.8018 | 0.8312 | 0.0040 |

Written solutions are in [report/report.pdf](report/report.pdf). Do not submit `data/`, `.venv/`, `runs/`, or model checkpoints.
