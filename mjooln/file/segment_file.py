from mjooln import Segment, File


class SegmentFile(File):

    def segment(self):
        return Segment(self.stub())