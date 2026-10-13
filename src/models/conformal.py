from pathlib import Path
import csv
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split


def main():
    # dummy to ensure works
    X = np.random.rand(100,3)
    y = np.random.randint(0,2,100)
    from mapie.classification import MapieClassifier
    clf = RandomForestClassifier(n_estimators=10, random_state=42)
    mapie = MapieClassifier(clf, cv=2, random_state=42)
    mapie.fit(X,y)
    print('ok')


if __name__=='__main__':
    main()
