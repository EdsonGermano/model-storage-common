import dill as pickle
import os
import shutil
import tempfile
import unittest
from moto import mock_s3

from model_storage import connect, get_, get_to_file, parse_s3_url, set_


class EqualityMixin(object):
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other


class StubModel(EqualityMixin):
    def __init__(self, coefficients):
        self.coefficients = coefficients


class TestModelStorage(unittest.TestCase):
    def test_parse_url(self):
        url = "s3://bucket-name/path/to/some/data.pickle"
        bucket, path = parse_s3_url(url)
        self.assertEquals("bucket-name", bucket)
        self.assertEquals("path/to/some/data.pickle", path)

    @mock_s3
    def test_set_and_get(self):
        model = StubModel(range(10))
        s3 = connect()
        bucket = "test-model-storage"
        key = "test/model.pickle"
        s3.create_bucket(Bucket=bucket)

        set_(pickle.dumps(model), bucket, key, s3)
        self.assertEquals(model, pickle.loads(get_(bucket, key, s3)))

    @mock_s3
    def test_set_and_get_to_file(self):
        model = StubModel(range(10))
        s3 = connect()
        bucket = "test-model-storage"
        key = "test/model.pickle"
        s3.create_bucket(Bucket=bucket)

        set_(pickle.dumps(model), bucket, key, s3)

        test_dir = tempfile.mkdtemp()
        local_path = os.path.join(test_dir, "model.pickle")
        get_to_file(local_path, bucket, key, s3)

        self.assertTrue(os.path.exists(local_path))
        with open(local_path, "rb") as infile:
            self.assertEquals(model, pickle.load(infile))
        shutil.rmtree(test_dir)