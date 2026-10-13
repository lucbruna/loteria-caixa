import numpy as np
from scipy import stats


def ks_drift(ref, cur, alpha=0.05):
    try:
        res = stats.ks_2samp(ref, cur)
        return res.pvalue < alpha, res.pvalue
    except Exception:
        return False, 1.0


if __name__ == '__main__':
    ref = np.random.normal(0,1,1000)
    cur = np.random.normal(0,1,1000)
    print(ks_drift(ref,cur))
