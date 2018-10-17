import json
import collections

REGISTERED_CLASS = {}

class MetaSerializable(type):

    def __call__(cls, *args, **kwargs):
        if cls.__name__ not in REGISTERED_CLASS:
            REGISTERED_CLASS[cls.__name__] = cls
        return super(MetaSerializable, cls).__call__(*args, **kwargs)


class JsonClassSerializable(json.JSONEncoder, metaclass=MetaSerializable):

    def default(self, obj):
        if isinstance(obj, collections.Set):
            return dict(_set_object=list(obj))
        if isinstance(obj, JsonClassSerializable):
            jclass = {}
            jclass["name"] = type(obj).__name__
            jclass["dict"] = obj.__dict__
            return dict(_class_object=jclass)
        else:
            return json.JSONEncoder.default(self, obj)

    def json_to_class(self, dct):
        if '_set_object' in dct:
            return set(dct['_set_object'])
        elif '_class_object' in dct:
            cclass = dct['_class_object']
            cclass_name = cclass["name"]
            if cclass_name not in REGISTERED_CLASS:
                raise RuntimeError(
                    "Class {} not registered in JSON Parser"
                    .format(cclass["name"])
                )
            instance = REGISTERED_CLASS[cclass_name]()
            instance.__dict__ = cclass["dict"]
            return instance
        return dct

    def encode_(self, file):
        with open(file, 'w') as outfile:
            json.dump(
                self.__dict__, outfile,
                cls=JsonClassSerializable,
                indent=4,
                sort_keys=True
            )

    def decode_(self, file):
        try:
            with open(file, 'r') as infile:
                self.__dict__ = json.load(
                    infile,
                    object_hook=self.json_to_class
                )
        except FileNotFoundError:
            print("Persistence load failed "
                  "'{}' do not exists".format(file)
                  )


class C(JsonClassSerializable):

    def __init__(self):
        self.mill = "s"


class B(JsonClassSerializable):

    def __init__(self):
        self.a = 1230
        self.c = C()


class A(JsonClassSerializable):

    def __init__(self):
        self.a = 1
        self.b = {1, 2}
        self.c = B()


A().encode_("test")
b = A()
b.decode_("test")
print(b.a)
# 1
print(b.b)
# {1, 2}
print(b.c.a)
# 1230
print(b.c.c.mill)
# s
