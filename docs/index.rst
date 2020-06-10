.. mjooln documentation master file, created by
   sphinx-quickstart on Wed May 13 22:09:56 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Introduction
============
File tree structure with convenience classes for file read/write/move/copy,
encryption, UTC timestamps, UUID etc.

:class:`.Atom` is a triplet identifier consists of a timestamp, key and UUID.

:class:`.File` wraps absolute file paths and has a range of convenience
functions

:class:`.Tree` is a folder with predefined and adjustable folder structure,
and strict file naming based on :class:`.Atom`. The class also has preset and
adjustable compression/encryption of all files in the tree


Installation
============
::

   pip install mjooln

Quick start
===========
All classes can be imported from base module::

   import mjooln as mj

   z = mj.Zulu(2020, 5, 12)
   z.iso()
      '2020-05-12T00:00:00+00:00'

   print(mj.Folder.home())
      /Users/zaphod

Create a tree and add some files::

   folder = mj.Folder.home()
   tree_name = 'oak'
   tree = Tree.plant(folder, tree_name, is_compressed=True)



Class list
==========

``mjooln.atom``

:class:`.Identity`
:class:`.Key`
:class:`.Zulu`
:class:`.Atom`

``mjooln.core``

:class:`.Crypt`
:class:`.Dic`
:class:`.Doc`
:class:`.JSON`

``mjooln.tree``

:class:`.Root`
:class:`.Tree`
:class:`.Leaf`



.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
