import pytest
import numpy as np
import mjooln as mj
import pandas as pd
import pandas.testing as pdt


@pytest.fixture()
def ground(tmp_folder):
    yield mj.Ground.settle(tmp_folder)


def test_grow(ground, tmp_csv_files):
    num_files = len(tmp_csv_files)
    tree = mj.Birch.plant(ground, 'my_birch_tree')
    for file in tmp_csv_files:
        s = mj.Segment(key='csv_for_test')
        tree.grow(file, s)

    assert len(list(tree.leaves())) == num_files
    assert tree.total_weeds() == 0


def test_read(ground, dfs):
    num_dfs = len(dfs)
    df = dfs[0].copy().convert_dtypes()
    tree = mj.Birch.plant(ground, 'my_birch_tree')
    zulu = mj.Zulu()
    tree.feed(key='df_for_test', df=df.copy(), zulu=zulu)
    # for df, z in zip(dfs, zulus):
    #     tree.feed(key='df_for_test', df=df.copy(), zulu=z)

    assert len(list(tree.leaves())) == 1
    assert tree.total_weeds() == 0

    leaf = list(tree.leaves())[0]
    dfl = leaf.feel()
    dfl = dfl.set_index('zulu', drop=True).convert_dtypes()
    dfl.index = pd.to_datetime(dfl.index)
    pdt.assert_frame_equal(df, dfl)

    # leaves = list(tree.leaves())
    # file_names = [x.file().stub() for x in leaves]
    # # data = zip(file_names, )
    # it = list(zip(file_names, dfs, leaves))
    # it.sort()
    # for _, df, leaf in it:
    #     dfl = leaf.feel()
    #     dfl = dfl.set_index('zulu', drop=True)
    #     dfl.index = pd.to_datetime(dfl.index)
    #     assert df == dfl


def test_read_multiple(ground, dfs):
    num_dfs = len(dfs)
    dfs = [x.convert_dtypes() for x in dfs]
    dfs_copy = [x.copy() for x in dfs]
    tree = mj.Birch.plant(ground, 'my_birch_tree')
    zulus = mj.Zulu.range(n=num_dfs)
    leaves = []
    for df, z in zip(dfs, zulus):
        leaves.append(tree.feed(key='df_for_test', df=df, zulu=z))

    assert len(list(tree.leaves())) == num_dfs
    assert tree.total_weeds() == 0

    for df, leaf in zip(dfs_copy, leaves):
        dfl = leaf.feel()
        dfl = dfl.set_index('zulu', drop=True).convert_dtypes()
        dfl.index = pd.to_datetime(dfl.index)
        pdt.assert_frame_equal(df, dfl)

    # Use tree leaves to get the leaves manually, then sort before comparing
    leaves = list(tree.leaves())
    segment = [str(x.segment()) for x in leaves]
    tup = list(zip(segment, leaves))
    tup.sort()
    leaves = [y for x, y in tup]
    for df, leaf in zip(dfs_copy, leaves):
        dfl = leaf.feel()
        dfl = dfl.set_index('zulu', drop=True).convert_dtypes()
        dfl.index = pd.to_datetime(dfl.index)
        pdt.assert_frame_equal(df, dfl)


def test_grow_invalid_extension(ground, tmp_files):
    tree = mj.Birch.plant(ground, 'my_birch_tree')
    for file in tmp_files:
        s = mj.Segment(key='invalid_for_test')
        with pytest.raises(mj.TreeError):
            tree.grow(file, s)

    assert len(list(tree.leaves())) == 0
    assert tree.total_weeds() == 0
