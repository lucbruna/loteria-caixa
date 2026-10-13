try:
    from evidently.report import Report
    from evidently.metrics import DataDriftTable
    print('evidently ok')
except Exception as e:
    print('err',e)
