# -*- coding:utf-8 -*-
from schematics.types import BaseType
from schematics.exceptions import ValidationError
from schematics.models import Model

class One2Many(BaseType):

    def __init__(self, parent_model, child_model, **kwargs):
        self.child_model = child_model

        super(One2Many, self).__init__(**kwargs)

    def to_native(self, value):
        return 'to_native {}'.format(value)

    def to_primitive(self, value):
        return 'to_primitive {}'.format(value)

if __name__ == '__main__':

    class Test(Model):
        test = One2Many()

    test = Test()
    test.test= 10

    print(test)



