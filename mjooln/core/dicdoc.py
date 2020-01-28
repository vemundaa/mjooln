import json
import simplejson

from mjooln import Zulu, Segment


class JSON:

    @classmethod
    def dumps(cls, dictionary, human=True, sort_keys=False, indent=4 * ' '):
        if human:
            return simplejson.dumps(dictionary, sort_keys=sort_keys, indent=indent)
        else:
            return json.dumps(dictionary)

    @classmethod
    def loads(cls, json_string):
        return simplejson.loads(json_string)


class Dic:

    IGNORE_STARTSWITH = '__'

    def add_dic(self, dic):
        for key, item in dic.items():
            if not key.startswith(self.IGNORE_STARTSWITH):
                self.__setattr__(key, item)

    def dic(self):
        dic = vars(self).copy()
        pop_keys = [x for x in dic if x.startswith(self.IGNORE_STARTSWITH)]
        for key in pop_keys:
            dic.pop(key)
        return dic

    def dev_print(self):
        text = '--' + f'  [{type(self).__name__}]  '
        text += (80-len(text)) * '-'
        print(text)
        for key, item in self.dic().items():
            print(f'{key}: {item} [{type(item).__name__}]')
        print(80*'-')

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
                dic[key] = cls._to_strings(item.dic())
            elif isinstance(item, dict):
                dic[key] = cls._to_strings(item)
            elif isinstance(item, Dic):
                dic[key] = cls._to_strings(item.dic())
        return dic


class Doc(Dic):

    def add_doc(self, doc):
        dic = JSON.loads(doc)
        dic = self._from_strings(dic)
        self.add_dic(dic)

    def doc(self):
        dic = self.dic()
        dic = self._to_strings(dic)
        return JSON.dumps(dic)


class SampleDictable(Dic):

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
        }


if __name__ == '__main__':
    dic = SampleDictable()
    dic.dev_print()

    doc = SampleDoc()
    doc.dev_print()
    print(doc.doc())
    dd = Doc()
    dd.add_dic(doc.doc())
    dd.dev_print()

