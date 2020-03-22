import json
import simplejson

from mjooln.core.zulu import Zulu
from mjooln.core.segment import Segment


# TODO: Add custom class handling, including reserved words
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

    PRIVATE_STARTSWITH = '_'

    @classmethod
    def default(cls):
        return cls().dic()

    def _add_item(self, key, item, ignore_private=True):
        # Add item and ignore private items if ignore_private is set to True
        if not ignore_private or not key.startswith(self.PRIVATE_STARTSWITH):
            self.__setattr__(key, item)

    def _add_dic(self, dic, ignore_private=True):
        for key, item in dic.items():
            self._add_item(key, item, ignore_private=ignore_private)

    def add(self, dic, ignore_private=True):
        self._add_dic(dic, ignore_private=ignore_private)

    def dic(self, ignore_private=True):
        dic = vars(self).copy()
        if ignore_private:
            pop_keys = [x for x in dic if x.startswith(self.PRIVATE_STARTSWITH)]
            for key in pop_keys:
                dic.pop(key)
        return dic

    def add_only_existing(self, dic, ignore_private=True):
        dic_to_add = {}
        for key in dic:
            if hasattr(self, key):
                dic_to_add[key] = dic[key]
        self._add_dic(dic_to_add, ignore_private=ignore_private)
        #
        # for key, item in dic.items():
        #     if not key.startswith(self.PRIVATE_STARTSWITH):
        #         if hasattr(self, key):
        #             self.__setattr__(key, item)

    def force_equal(self, dic, ignore_private=True):
        self._add_dic(dic, ignore_private=ignore_private)
        for key in self.dic(ignore_private=ignore_private):
            if key not in dic:
                self.__delattr__(key)

    def dev_print(self, ignore_private=True, indent=4*' ', width=80):
        """Pretty print of class variables for development in terminal"""
        text = f'--{indent}[[ {type(self).__name__} ]]{indent}'
        text += (width-len(text)) * '-'
        print(text)
        self._dev_print(self.dic(ignore_private=ignore_private), level=0)
        print(width*'-')

    def _dev_print(self, dic, level=0, indent=4*' '):
        for key, item in dic.items():
            if isinstance(item, dict):
                self._dev_print(item, level=level+1)
            else:
                print(level*indent + f'{key}: [{type(item).__name__}] {item} ')

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

    @classmethod
    def dic_to_doc(cls, dic, human_readable=True):
        dic = cls._to_strings(dic)
        return JSON.dumps(dic, human=human_readable)

    @classmethod
    def doc_to_dic(cls, doc):
        dic = JSON.loads(doc)
        dic = cls._from_strings(dic)
        return dic

    def _add_doc(self, doc, ignore_private=True):
        dic = JSON.loads(doc)
        dic = self._from_strings(dic)
        self._add_dic(dic, ignore_private=ignore_private)

    def add(self, dic_or_doc, ignore_private=True):
        if not dic_or_doc:
            return
        if isinstance(dic_or_doc, dict):
            Dic._add_dic(self, dic_or_doc, ignore_private=ignore_private)
        elif isinstance(dic_or_doc, str):
            self._add_doc(dic_or_doc, ignore_private=ignore_private)
        else:
            raise DocError(f'Input object is neither dic nor doc: {type(dic_or_doc)}')

    def doc(self, ignore_private=True):
        dic = self.dic(ignore_private=ignore_private)
        dic = self._to_strings(dic)
        return JSON.dumps(dic)
