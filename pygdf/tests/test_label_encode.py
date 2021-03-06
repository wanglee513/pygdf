import pytest
import random
from itertools import product

import numpy as np

from pygdf.dataframe import DataFrame


def _random_float(nelem, dtype):
    return np.random.random(nelem).astype(dtype)


def _random_int(nelem, dtype):
    return np.random.randint(low=0, high=nelem, size=nelem, dtype=dtype)


def _random(nelem, dtype):
    dtype = np.dtype(dtype)
    if dtype.kind in 'iu':
        return _random_int(nelem, dtype)
    elif dtype.kind in 'f':
        return _random_float(nelem, dtype)


_param_sizes = [1, 7, 10, 100, 1000]
_param_dtypes = [np.int32, np.float32]


@pytest.mark.parametrize('nelem,dtype',
                         list(product(_param_sizes, _param_dtypes)))
def test_label_encode(nelem, dtype):
    df = DataFrame()
    np.random.seed(0)

    # initialize data frame
    df['cats'] = _random(nelem, dtype)
    vals = df['cats'].unique()
    lab = dict(zip(vals, range(len(vals))))

    # label encode series
    ncol = df['cats'].label_encoding(cats=vals)
    arr = ncol.to_array()

    # verify labels of new column
    for i in range(arr.size):
        np.testing.assert_equal(arr[i], lab.get(df.cats[i], None))

    # label encode data frame
    df2 = df.label_encoding(column='cats', prefix='cats', cats=vals)

    assert df2.columns[0] == 'cats'
    assert df2.columns[1] == 'cats_labels'


def test_label_encode_drop_one():
    random.seed(0)
    np.random.seed(0)

    df = DataFrame()

    # initialize data frame
    df['cats'] = np.random.randint(7, size=10, dtype=np.int32)
    vals = list(df['cats'].unique())
    # drop 1 randomly
    del vals[random.randrange(len(vals))]

    lab = dict(zip(vals, list(range(len(vals)))))

    # label encode series
    ncol = df['cats'].label_encoding(cats=vals, dtype='float32')
    arr = ncol.to_array()

    # verify labels of new column

    for i in range(arr.size):
        # assuming -1 is used for missing value
        np.testing.assert_equal(arr[i], lab.get(df.cats[i], -1))

    # label encode data frame
    df2 = df.label_encoding(column='cats', prefix='cats', cats=vals, dtype='float32')

    assert df2.columns[0] == 'cats'
    assert df2.columns[1] == 'cats_labels'


def test_label_encode_float_output():
    random.seed(0)
    np.random.seed(0)

    df = DataFrame()

    # initialize data frame
    df['cats'] = arr = np.random.randint(7, size=10, dtype=np.int32)
    cats = [1, 2, 3, 4]
    encoder = {c: i for i, c in enumerate(cats)}
    df2 = df.label_encoding(column='cats', prefix='cats',
                            cats=cats, dtype=np.float32,
                            na_sentinel=np.nan)

    got = df2['cats_labels'].to_array()

    handcoded = np.array([encoder.get(v, np.nan) for v in arr])
    np.testing.assert_equal(got, handcoded)


if __name__ == '__main__':
    test_label_encode()
    test_label_encode_drop_one()
