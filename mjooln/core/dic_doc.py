import json
import simplejson

from mjooln.core.zulu import Zulu
from mjooln.segment.segment import Segment


class JSON:
    """Dict to/from JSON string, with optional human readable"""

    @classmethod
    def dumps(cls, dictionary, human=True, sort_keys=False, indent=4 * ' '):
        """Convert from dict to JSON string

        :param dictionary: Input dictionary
        :type dictionary: dict
        :param human: Human readable flag
        :param sort_keys: Sort key flag
        :param indent: Indent to use (human readable only)
        """
        if human:
            return simplejson.dumps(dictionary, sort_keys=sort_keys, indent=indent)
        else:
            return json.dumps(dictionary)

    @classmethod
    def loads(cls, json_string):
        """Convert JSON string to dictionary"""
        return simplejson.loads(json_string)


class Dic:
    """Enables child class to mirror attributes and dictionaries

    Certain classes are converted to/from strings when using JSON conversion"""

    IGNORE_STARTSWITH = '_'

    @classmethod
    def default(cls):
        return cls().dic()

    def _add_item(self, key, item):
        if not key.startswith(self.IGNORE_STARTSWITH):
            self.__setattr__(key, item)

    def _add_dic(self, dic):
        for key, item in dic.items():
            self._add_item(key, item)

    def add(self, dic):
        self._add_dic(dic)

    def dic(self):
        dic = vars(self).copy()
        pop_keys = [x for x in dic if x.startswith(self.IGNORE_STARTSWITH)]
        for key in pop_keys:
            dic.pop(key)
        return dic

    def add_only_existing(self, dic):
        dic_to_add = {}
        for key in dic:
            if hasattr(self, key):
                dic_to_add[key] = dic[key]
        self._add_dic(dic_to_add)

        for key, item in dic.items():
            if not key.startswith(self.IGNORE_STARTSWITH):
                if hasattr(self, key):
                    self.__setattr__(key, item)

    def force_equal(self, dic):
        self._add_dic(dic)
        for key in self.dic():
            if key not in dic:
                self.__delattr__(key)

    def dev_print(self):
        text = '--' + f'  [[ {type(self).__name__} ]]  '
        text += (80-len(text)) * '-'
        print(text)
        self._dev_print(self.dic(), level=0)
        print(80*'-')

    def _dev_print(self, dic, level=0):
        for key, item in dic.items():
            if isinstance(item, dict):
                self._dev_print(item, level=level+1)
            else:
                print(level*'  ' + f'{key}: [{type(item).__name__}] {item} ')

    @classmethod
    def _from_strings(cls, dic):
        for key, item in dic.items():
            if isinstance(item, str):
                dic[key] = Zulu.string_elf(item)
            elif isinstance(item, dict):
                dic[key] = cls._from_strings(item)
                if Segment.check(dic[key]):
                    dic[key] = Segment(**dic[key])
            elif isinstance(item, Dic):
                dic[key] = cls._from_strings(item.dic())
        return dic

    @classmethod
    def _to_strings(cls, dic):
        for key, item in dic.items():
            if isinstance(item, Zulu):
                dic[key] = item.to_iso_string()
            elif isinstance(item, Segment):
                dic[key] = cls._to_strings(vars(item))
            elif isinstance(item, dict):
                dic[key] = cls._to_strings(item)
            elif isinstance(item, Dic):
                dic[key] = cls._to_strings(item.dic())
        return dic


class DocError(Exception):
    pass


class Doc(Dic):
    """Enables child classes to mirror attributes and JSON strings"""

    def _add_doc(self, doc):
        dic = JSON.loads(doc)
        dic = self._from_strings(dic)
        self._add_dic(dic)

    def add(self, dic_or_doc):
        if not dic_or_doc:
            return
        if isinstance(dic_or_doc, dict):
            Dic._add_dic(self, dic_or_doc)
        elif isinstance(dic_or_doc, str):
            self._add_doc(dic_or_doc)
        else:
            raise DocError(f'Input object is neither dic nor doc: {type(dic_or_doc)}')

    def doc(self):
        dic = self.dic()
        dic = self._to_strings(dic)
        return JSON.dumps(dic)


class SampleDic(Dic):

    def __init__(self):
        self._hide = 'test'
        self.date = Zulu()
        self.text = 'Hello there'
        self.number = float(0.3)
        self.d = {
            'date': Zulu(),
            'cont': 'yo',
        }


class SampleDoc(Doc):

    def __init__(self):
        self.date = Zulu()
        self.text = 'Hello there'
        self.number = float(0.3)
        self.d = {
            'date': Zulu(),
            'cont': 'yo',
            'sub': {
                'hello': 'fefe',
                'there': 5,
            }
        }


if __name__ == '__main__':
    dic = SampleDic()
    dic.dev_print()
    print(80*'#')
    doc = SampleDoc()
    doc.dev_print()
    print(80*'#')
    dd = Doc()
    dd.add(doc.doc())
    dd.dev_print()

