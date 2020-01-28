import logging

from mjooln.file.path import Path


logger = logging.getLogger(__name__)


# Use psutil to check available volumes (ie partitions).
# On windows, use all=True to find disk drives. Mac is same as linux
# Possibly add check on what file system it is.
# Must be registered somehow, and the stored locations/trees must have a valid volume (obviously)
# Volume class should also have disk space (used and free)
# Location/Environment/Tree is where the app is running. It should have memory stuff in it
# Need a separate trick for network drive?
# In test class, check the volumes/folders stored in "absolute". Also check access rights. Handle read and write.

# TODO: Move mountpoint etc here? Then inherit folder from volume, etc?
# TODO: FInd the order of path, volume, folder and file.
#
# class Volume(Path):
#
#     @classmethod
#     def elf(cls, volume):
#         if isinstance(volume, Volume):
#             return volume
#         else:
#             return cls(volume)
#
#     def __new__(cls, path_str):
#         # TODO: Add handling of network drive. Check if exists instead.
#         instance = super(Volume, cls).__new__(cls, path_str)
#         if not instance.is_volume():
#             raise VolumeError(f'Path \'{instance}\' is not a volume. '
#                               f'Allowed volumes are: {cls.mountpoints()}')
#         return instance
#
#
# class VolumeError(Exception):
#     pass

#
# if __name__ == '__main__':
#     v = Volume('\\')
#     print(v)
#     print(v.list())