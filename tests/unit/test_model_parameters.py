import pytest
import warnings
import os
from sasctl.pzmm import ModelParameters as mp


class BadModel:
    attr = None


@pytest.fixture
def bad_model():
    return BadModel()


@pytest.fixture
def train_data():
    """Returns the Iris data set as (X, y)"""

    try:
        import pandas as pd
    except ImportError:
        pytest.skip('Package `pandas` not found.')

    try:
        from sklearn import datasets
    except ImportError:
        pytest.skip('Package `sklearn` not found.')

    raw = datasets.load_iris()
    iris = pd.DataFrame(raw.data, columns=raw.feature_names)
    iris = iris.join(pd.DataFrame(raw.target))
    iris.columns = ['SepalLength', 'SepalWidth', 'PetalLength', 'PetalWidth', 'Species']
    iris['Species'] = iris['Species'].astype('category')
    iris.Species.cat.categories = raw.target_names
    return iris.iloc[:, 0:4], iris['Species']


@pytest.fixture
def sklearn_model(train_data):
    """Returns a simple Scikit-Learn model"""

    try:
        from sklearn.linear_model import LogisticRegression
    except ImportError:
        pytest.skip('Package `sklearn` not found.')

    X, y = train_data
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        model = LogisticRegression(multi_class='multinomial', solver='lbfgs')
        model.fit(X, y)
    return model


@pytest.mark.incremental
class TestSKLearnModel:
    PROJECT_NAME = 'PZMM SKLearn Test Project'
    MODEL_NAME = 'SKLearnModel'
    PATH = '.'

    def test_generate_hyperparameters(self, sklearn_model):
        mp.generate_hyperparameters(sklearn_model, self.MODEL_NAME, self.PATH)
        assert os.path.exists('./PythonModelHyperparameters.json')
        os.remove('./PythonModelHyperparameters.json')

    def test_bad_model_hyperparameters(self, bad_model):
        with pytest.raises(ValueError):
            mp.generate_hyperparameters(bad_model, self.MODEL_NAME, self.PATH)