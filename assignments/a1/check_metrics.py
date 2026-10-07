"""Public small-example checks. Run after implementing student.metrics."""
import math
import numpy as np
from student import metrics


def close(actual, expected):
    assert actual is not None and math.isclose(actual, expected, abs_tol=1e-10), (actual, expected)


def check(fn):
    # A=0 predictions (0,0), labels (0,1).
    # A=1 predictions (0,1,0,1), labels (0,0,1,1).
    y = np.array([0, 1, 0, 0, 1, 1])
    a = np.array([0, 0, 1, 1, 1, 1])
    score = np.array([.1, .2, .1, .5, .2, .9])
    m = fn(y, score, a)
    for key, value in dict(accuracy=.5, rw_accuracy=.5, dp_gap=.5).items():
        close(m[key], value)
    close(m['groups']['0']['positive_rate'], 0.)
    close(m['groups']['1']['positive_rate'], .5)
    assert m['groups']['0']['n'] == 2 and m['groups']['1']['n'] == 4
    # Unequal group sizes distinguish the two accuracy measures.
    m = fn(np.array([0, 1, 1, 1]), np.array([.1, .1, .1, .1]), np.array([0, 1, 1, 1]))
    close(m['accuracy'], .25)
    close(m['rw_accuracy'], .5)
    # Undefined group rates propagate to group comparisons.
    m = fn(np.array([0, 1]), np.array([.1, .9]), np.array([0, 0]))
    assert m['groups']['1']['n'] == 0
    assert m['groups']['1']['accuracy'] is None
    assert m['groups']['1']['positive_rate'] is None
    assert m['dp_gap'] is None and m['rw_accuracy'] is None


if __name__ == '__main__':
    check(metrics)
    print('Small-example metric checks passed.')
