try:
    import shap
    print('shap ok', shap.__version__)
except Exception as e:
    print('err',e)
