# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import copy

from collections import MutableMapping


class ApiModel(dict, MutableMapping):
    '''A thin wrapper on dict to store API doc metadata'''
    def __init__(self, *args, **kwargs):
        self.__apidoc__ = {}
        self.__parent__ = None
        super(ApiModel, self).__init__(*args, **kwargs)

    @property
    def resolved(self):
        '''
        Resolve real fields before submitting them to upstream restful marshal
        '''
        # Duplicate fields
        resolved = copy.deepcopy(self)

        # Recursively copy parent fields if necessary
        if self.__parent__:
            resolved.update(self.__parent__.resolved)

        # Handle discriminator
        candidates = [f for f in resolved.values() if getattr(f, 'discriminator', None)]
        # Ensure the is only one discriminator
        if len(candidates) > 1:
            raise ValueError('There can only be one discriminator by schema')
        # Ensure discriminator always output the model name
        elif len(candidates) == 1:
            candidates[0].default = self.__apidoc__['name']

        return resolved

    @property
    def ancestors(self):
        '''
        Return the ancestors tree
        '''
        return self.__parent__.tree

    @property
    def tree(self):
        '''
        Return the inheritance tree
        '''
        tree = [self.__apidoc__['name']]
        return self.ancestors + tree if self.__parent__ else tree

    @property
    def name(self):
        return self.__apidoc__['name']

    def get_parent(self, name):
        if self.name == name:
            return self
        elif self.__parent__:
            return self.__parent__.get_parent(name)
        else:
            raise ValueError('Parent ' + name + ' not found')
