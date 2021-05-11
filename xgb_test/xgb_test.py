import os
import pandas as pd
from mlrun.datastore import DataItem
from mlrun.artifacts import get_model
from cloudpickle import load

from mlrun.mlutils.models import eval_model_v2


def xgb_test(
        context,
        models_path: DataItem,
        test_set: DataItem,
        label_column: str,
        plots_dest: str = "plots",
        default_model: str = "model.pkl"
) -> None:
    """Test one or more classifier models against held-out dataset

    Using held-out test features, evaluates the peformance of the estimated model

    Can be part of a kubeflow pipeline as a test step that is run post EDA and
    training/validation cycles

    :param context:         the function context
    :param models_path:     model artifact to be tested
    :param test_set:        test features and labels
    :param label_column:    column name for ground truth labels
    :param plots_dest:      dir for test plots
    :param default_model:   'model.pkl', default model artifact file name
    """
    xtest = test_set.as_df()
    ytest = xtest.pop(label_column)

    try:
        model_file, model_obj, _ = get_model(models_path.url, suffix='.pkl')
        model_obj = load(open(model_file, "rb"))
    except Exception as a:
        raise Exception("model location likely misspecified")

    eval_metrics = eval_model_v2(context, xtest, ytest.values, model_obj)