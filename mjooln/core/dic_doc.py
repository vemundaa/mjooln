import json
import simplejson

from mjooln.atom.zulu import Zulu, ZuluError
from mjooln.atom.atom import Atom

# TODO: Add YAML handling with pyyaml, yaml.dump(data, ff, allow_unicode=True)


# TODO: Add custom class handling, including reserved words
class JSON:
    """Dict to/from JSON string, with optional human readable"""

    @classmethod
    def dumps(cls, dic, human=True, sort_keys=False, indent=4 * ' '):
        """Convert from dict to JSON string

        :param dic: Input dictionary
        :type dic: dict
        :param human: Human readable flag
        :param sort_keys: Sort key flag (human readable only)
        :param indent: Indent to use (human readable only)
        """
        if human:
            return simplejson.dumps(dic, sort_keys=sort_keys, indent=indent)
        else:
            return json.dumps(dic)

    @classmethod
    def loads(cls, json_string):
        """ Parse JSON string to dictionary

        :param json_string: JSON string
        :return: dict
        """
        return simplejson.loads(json_string)


class Dic:
    """Enables child classes to mirror attributes and dictionaries

    Private variables start with underscore, and are ignored by default.

    .. note:: Meant for inheritance and not direct use
    """

    # TODO: Consider moving ignore_private to a private class attribute

    _PRIVATE_STARTSWITH = '_'

    def _add_item(self, key, item, ignore_private=True):
        # Add item and ignore private items if ignore_private is set to True
        if not ignore_private or not key.startswith(self._PRIVATE_STARTSWITH):
            self.__setattr__(key, item)

    def _add_dic(self, dic, ignore_private=True):
        for key, item in dic.items():
            self._add_item(key, item, ignore_private=ignore_private)

    def add(self, dic, ignore_private=True):
        """ Add dictionary to class as attributes

        :param dic: Dictionary to add
        :param ignore_private: Ignore private attributes flag
        :return: None
        """
        self._add_dic(dic, ignore_private=ignore_private)

    def dic(self, ignore_private=True):
        """ Return dictionary with a copy of attributes

        :param ignore_private: Ignore private attributes flag
        :return: dict
        """
        dic = vars(self).copy()
        if ignore_private:
            pop_keys = [x for x in dic if x.startswith(self._PRIVATE_STARTSWITH)]
            for key in pop_keys:
                dic.pop(key)
        return dic

    def add_only_existing(self, dic, ignore_private=True):
        """ Add dictionary keys and items as attributes if they already exist
        as attributes

        :param dic: Dictionary to add
        :param ignore_private: Ignore private attributes flag
        :return: None
        """
        dic_to_add = {}
        for key in dic:
            if hasattr(self, key):
                dic_to_add[key] = dic[key]
        self._add_dic(dic_to_add, ignore_private=ignore_private)

    def force_equal(self, dic, ignore_private=True):
        """ Add all dictionary keys and items as attributes in object, and
        delete existing attributes that are not keys in the input dictionary

        :param dic: Dictionary to add
        :param ignore_private: Ignore private attributes flag
        :return: None
        """
        self._add_dic(dic, ignore_private=ignore_private)
        for key in self.dic(ignore_private=ignore_private):
            if key not in dic:
                self.__delattr__(key)

    def dev_print(self, ignore_private=True, indent=4*' ', width=80):
        """ Pretty print of attributes in terminal meant for development
        purposes
        """
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
    def _parse_if_iso(cls, string):
        try:
            zulu = Zulu.parse_iso(string)
            return zulu
        except ValueError:
            pass
        except ZuluError:
            pass
        return string

    @classmethod
    def _from_strings(cls, dic):
        for key, item in dic.items():
            if isinstance(item, str):
                dic[key] = cls._parse_if_iso(item)
            elif isinstance(item, dict):
                dic[key] = cls._from_strings(item)
                if Atom.check(dic[key]):
                    dic[key] = Atom(**dic[key])
            elif isinstance(item, Dic):
                dic[key] = cls._from_strings(item.dic())
        return dic

    @classmethod
    def _to_strings(cls, dic):
        for key, item in dic.items():
            if isinstance(item, Zulu):
                dic[key] = item.iso()
            elif isinstance(item, Atom):
                dic[key] = cls._to_strings(vars(item))
            elif isinstance(item, dict):
                dic[key] = cls._to_strings(item)
            elif isinstance(item, Dic):
                dic[key] = cls._to_strings(item.dic())
        return dic


class DocError(Exception):
    pass


class Doc(Dic):
    """ Enables child classes to mirror attributes, dictionaries and JSON
    strings

    Special cases:

    - Zulu objects will be converted to an ISO 8601 string before a dictionary
      is converted to JSON
    - ISO 8601 strings that are time zone aware with UTC, will be converted to
      Zulu objects after JSON document has been converted to a dictionary
    - Elements that are dictionaries with key names corresponding to Atom
      (key, zulu, identity), will be recognized and converted back to an Atom
      object after JSON document has been converted to a dictionary
    """

    @classmethod
    def dic_to_doc(cls, dic, human_readable=True):
        """ Convert dictionary to JSON document

        :param dic: Input dictionary
        :param human_readable:
        :return: JSON document
        """
        dic = cls._to_strings(dic)
        return JSON.dumps(dic, human=human_readable)

    @classmethod
    def doc_to_dic(cls, doc):
        """ Convert JSON document to dictionary

        :param doc: Input JSON document
        :return: dict
        """
        dic = JSON.loads(doc)
        dic = cls._from_strings(dic)
        return dic

    def _add_doc(self, doc, ignore_private=True):
        dic = JSON.loads(doc)
        dic = self._from_strings(dic)
        self._add_dic(dic, ignore_private=ignore_private)

    def add(self, dic_or_doc, ignore_private=True):
        """ Add dictionary or JSON document as class attributes

        Existing attributes will be replaced with the new value. Attributes
        not contained in input dictionary or document will keep their value.

        :param dic_or_doc: dict or JSON document
        :param ignore_private: Ignore private attributes flag
        :return: None
        """
        if not dic_or_doc:
            return
        if isinstance(dic_or_doc, dict):
            Dic._add_dic(self, dic_or_doc, ignore_private=ignore_private)
        elif isinstance(dic_or_doc, str):
            self._add_doc(dic_or_doc, ignore_private=ignore_private)
        else:
            raise DocError(f'Input object is neither dic '
                           f'nor doc: {type(dic_or_doc)}')

    def doc(self, ignore_private=True):
        """ Copy class attributes into a JSON document

        :param ignore_private: Ignore private attributes flag
        :return: JSON document
        """
        dic = self.dic(ignore_private=ignore_private)
        dic = self._to_strings(dic)
        return JSON.dumps(dic)
