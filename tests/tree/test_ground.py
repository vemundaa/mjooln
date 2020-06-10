import pytest
from mjooln import File, NotRootException
from mjooln.tree.ground import GroundProblem, Ground, NoGround
from mjooln.tree.root import Root
from mjooln.core.folder import Folder


def test_settle(tmp_folder):
    ground = Ground.settle(tmp_folder, 'test_ground')
    assert ground.list() == []
    assert len(ground.cave.list()) == 0
    ground = Ground(tmp_folder)
    assert ground.key == 'test_ground'

def test_not_ground(tmp_folder):
    ground = Ground.settle(tmp_folder, 'test_ground')
    folder = Folder(ground)
    g = folder.list('.*')[0]
    c = g.list()[0]
    cf = File(c.list('.*')[0])
    dic = cf.read()
    dic['ground_key'] = 'rubbish'
    cf.write(dic)
    with pytest.raises(NoGround):
        Ground(tmp_folder)
    cf.delete()
    with pytest.raises(NotRootException):
        Ground(tmp_folder)


def test_settle_twice(tmp_folder):
    Ground.settle(tmp_folder, 'test_ground')
    with pytest.raises(GroundProblem):
        Ground.settle(tmp_folder, 'test_ground_2')


def test_cave(tmp_folder, tmp_files):
    ground = Ground.settle(tmp_folder, 'test_ground')
    assert len(ground.list()) == len(tmp_files)
    for file in tmp_files:
        file.move(ground.cave)
    assert len(ground.list()) == 0
    assert len(ground.cave.list()) == len(tmp_files)


def test_roots(tmp_folder, tmp_files):
    ground = Ground.settle(tmp_folder, 'test_ground')
    r1 = Root.plant(ground, 'root_1')
    f1 = Folder.join(ground, 'folder_1')
    r2 = Root.plant(f1, 'root_2')
    f2 = Folder.join(f1, 'folder_2')
    r3 = Root.plant(f2, 'root_3')
    assert len(ground.list()) == 5
    for file in tmp_files:
        file.copy(f1).copy(f2)
        file.copy(r1.folder()).copy(r2.folder()).copy(r3.folder())
    roots = ground.roots()
    assert len(roots) == 3
