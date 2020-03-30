import pytest
import numpy as np
import mjooln as mj
import pandas as pd
import pandas.testing as pdt


@pytest.fixture()
def ground(tmp_folder):
    yield mj.Ground.settle(tmp_folder)


def test_grow(ground, dfs):
    num_files = len(dfs)
    tree = mj.Oak.plant(ground, 'my_oak_tree')
    for df in dfs:
        tree.feed(key='h5_for_test', df=df, zulu=mj.Zulu(df.index[0]))

    assert len(list(tree.leaves())) == num_files
    assert tree.total_weeds() == 0


def test_read(ground, dfs):
    num_dfs = len(dfs)
    df = dfs[0].copy()
    tree = mj.Oak.plant(ground, 'my_birch_tree')
    zulu = mj.Zulu()
    tree.feed(key='df_for_test', df=df.copy(), zulu=zulu)

    assert len(list(tree.leaves())) == 1
    assert tree.total_weeds() == 0

    leaf = list(tree.leaves())[0]
    dfl = leaf.feel()
    pdt.assert_frame_equal(df, dfl)


def test_read_multiple(ground, dfs):
    num_dfs = len(dfs)
    dfs_copy = [x.copy() for x in dfs]
    tree = mj.Oak.plant(ground, 'my_oak_tree')
    zulus = mj.Zulu.range(n=num_dfs)
    leaves = []
    for df, z in zip(dfs, zulus):
        leaves.append(tree.feed(key='df_for_test', df=df, zulu=z))

    assert len(list(tree.leaves())) == num_dfs
    assert tree.total_weeds() == 0

    for df, leaf in zip(dfs_copy, leaves):
        dfl = leaf.feel()
        pdt.assert_frame_equal(df, dfl)

    # Use tree leaves to get the leaves manually, then sort before comparing
    leaves = list(tree.leaves())
    segment = [str(x.segment()) for x in leaves]
    tup = list(zip(segment, leaves))
    tup.sort()
    leaves = [y for x, y in tup]
    for df, leaf in zip(dfs_copy, leaves):
        dfl = leaf.feel()
        pdt.assert_frame_equal(df, dfl)


def test_append_multiple(ground, dfs):
    num_dfs = len(dfs)
    dfs_copy = pd.concat(dfs)
    tree = mj.Oak.plant(ground, 'my_oak_tree')
    zulu = dfs[0].index.min()
    segment = mj.Segment(key='df_for_test', zulu=zulu)
    for df in dfs:
        tree.feed(df=df, **segment.dic(), append=True)

    leaves = list(tree.leaves())
    assert len(leaves) == 1
    assert tree.total_weeds() == 0

    leaf = leaves[0]
    dfl = leaf.feel()
    pdt.assert_frame_equal(dfs_copy, dfl)


def test_grow_invalid_extension(ground, tmp_files):
    tree = mj.Oak.plant(ground, 'my_oak_tree')
    for file in tmp_files:
        s = mj.Segment(key='invalid_for_test')
        with pytest.raises(mj.TreeError):
            tree.grow(file, s)

    assert len(list(tree.leaves())) == 0
    assert tree.total_weeds() == 0
