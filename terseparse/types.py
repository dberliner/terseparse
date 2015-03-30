"""Namespace for all type objects"""
import re
import logging
from argparse import ArgumentTypeError

from .utils import classproperty


log = logging.getLogger('terseparse.types')

# Lists of items are separated by commas, semi-colons and/or whitespace
list_regex = re.compile(r'[^,;\s]+')


class Type(object):
    """ABC for type objects.
    Types are callable, taking a string and converting it
    to their given type. The call method should have no side effects.
    """
    
    def __call__(self, val):
        return self.convert(val)

    def __str__(self):
        """Implement this method to show a simple representation of the class"""
        return self.name

    def __or__(self, obj):
        return Or(self, obj)

    def fail(self, val_str, message):
        msg = "{!r} is an invalid <{}>. {}".format(val_str, self.name, message)
        raise ArgumentTypeError(msg)


class GreedyType(Type):
    """Mixin to indicate that a type will greedily consume arguments."""
    

class Keyword(Type):
    def __init__(self, key, *args):
        self.name = key
        self.key = key
        self.value = key if len(args) != 1 else args[0]
        self.description = "Keyword({!r})".format(key)

    def convert(self, val):
        if val == self.key:
            return self.value
        self.fail(val, "Must be {!r}".format(self.key))


class Str(Type):
    """Convert string to string
    Use this instad of str, to get a clean type name
    """
    def __init__(self):
        self.name = 'str'

    def convert(self, val):
        return str(val)


class Bool(Type):
    """Convert string to bool"""
    def __init__(self):
        self.name = 'bool'
        self.true_vals = ('true', 't', '1', 'yes')

    def __init__(self, val):
        return val.lower() in self.true_vals 


class Set(Type):
    def __init__(self, typ):
        self.name = 'set(<{}>)'.format(typ)
        self.description = self.name
        self.typ = typ

    def convert(self, val):
        seq = set()
        for k in list_regex.findall(val):
            try:
                seq.add(self.typ(k))
            except ArgumentTypeError as e:
                self.fail(val, self.description + '\n' + str(e))
        return seq


class List(Type):
    def __init__(self, typ):
        self.name = 'list(<{}>)'.format(typ)
        self.description = self.name
        self.typ = typ

    def convert(self, val):
        seq = list() 
        for k in list_regex.findall(val):
            try:
                seq.append(self.typ(k))
            except ArgumentTypeError as e:
                self.fail(val, self.description + '\n' + str(e))
        return seq
        

class Dict(Type):
    """Converts a string to a dictionary
    Support a comma, semi-colon or space separated list of key value pairs.
    Key-value pairs can be separated by either a colon or and equals sign.

    The following will all parse to {'a': 'b', 'c': 'd'}
    >>> 'a:b c:d'
    >>> 'a=b,c=d'
    >>> 'a:b, c=d'
    >>> 'a=b,,,c=d'

    Keys can be specified multiple times, the latest (farthest to right) key's
    value will overwrite previous values.
    """
    def __init__(self, validator_map):
        """Create a dictonary type from a dictionary of other types
        Args:
            validator_map -- a mapping from names to types
        Examples:
        >>> Dict({'a': int, 'b': int})('a:1,b:2')
        {'a': 1, 'b': 2}

        >>> Dict({'a': str, 'b': int})('a:asdf b=1234')
        {'a': 'asdf', 'b': 1234}
        """
        self.name = 'dict'
        self.validators = dict(validator_map)
        v_sorted = sorted(validator_map.iteritems(), key=lambda t: t[0])
        self.validator_descriptions = ['{}:<{}>'.format(k, v) for k, v in v_sorted]
        self.summary = ', '.join(self.validator_descriptions)
        self.description = '\nDict options: \n  '
        self.description += '\n  '.join(self.validator_descriptions)
        self.kv_regex = re.compile(r'[=:]+')

    def keys_to_set_type(self):
        kws = tuple(Keyword(k) for k in self.validators)
        return Set(Or(*kws))

    def convert(self, val):
        print(val)
        try:
            return self._convert(val)
        except (AssertionError, ValueError):
            self.fail(val, self.description)
        except ArgumentTypeError as e:
            self.fail(val, self.description + '\n' + str(e))

    def _convert(self, val):
        obj = {}
        for pair in list_regex.findall(val):
            k, v = self.kv_regex.split(pair)
            assert k in self.validators
            val = self.validators[k](v)
            if k in obj:
                log.warn('key: {!r} overwritten '
                         'new: {!r} old: {!r}'.format(k, val, obj[k]))
            obj[k] = val
        return obj


FILE_MODES = {
    'r': 'readable',
    'w': 'writable',
    'rw': 'readable and writeable'}


class File(Type):
    @classproperty
    def r(cls):
        return cls('r')

    @classproperty
    def rw(cls):
        return cls('rw')

    @classproperty
    def w(cls):
        return cls('w')
    
    def __init__(self, mode):
        self.name = 'file'
        self.mode = FILE_MODES[mode]
        self.description = 'file({})'.format(mode)

    def convert(self, val):
        try:
            return file(val, self.mode)
        except IOError:
            self.fail(val, 'Must be a {} file'.format(self.mode))


class Int(Type):
    @classproperty
    def u32(cls):
        obj = cls(0, 2**32)
        obj.name = 'u32'
        obj.description = 'unsigned 32-bit integer'
        return obj

    @classproperty
    def positive(cls):
        return cls(0)

    @classproperty
    def negative(cls):
        return cls(None, 0)

    def __init__(self, minval=None, maxval=None):
        """Create an Integer that satisfies the requirements minval <= val < maxval
        """
        self.name = 'int'
        self.minval = minval
        self.maxval = maxval
        self.domain = ''
        if minval is not None and maxval is not None:
            self.domain = '{} <= val < {}'.format(minval, maxval)
        elif minval is not None:
            self.domain = '{} <= val'.format(minval)
        elif maxval is not None:
            self.domain = 'val < {}'.format(maxval)
        self.description = 'int({})'.format(self.domain) if self.domain else 'int'
        self.error_message = "Must satisfy {}".format(self.domain)

    def convert(self, val_str):
        try:
            val = self._convert(val_str)
        except ValueError:
            self.fail(val_str, self.error_message)
        if (self.minval is not None and val < self.minval) or (
                self.maxval is not None and val >= self.maxval):
            self.fail(val_str, self.error_message)
        return val

    def _convert(self, val):
        try:
            val = int(val, 10)
        except ValueError:
            val = int(val, 16)
        return val


class Or(Type):
    '''Combine types in a shortcircuit fashion.
    The first type to match wins.
    If an Or is one of the types then its nested types are flattened.'''
    def __init__(self, *types):
        _types = []
        for typ in types:
            if isinstance(typ, Or):
                _types.extend(typ.types)
            else:
                _types.append(typ)

        self.name = '|'.join(map(str, _types))
        self.description = ' or '.join(t.description for t in _types)
        self.types = _types

    def convert(self, val):
        for t in self.types:
            try:
                return t(val)
            except ArgumentTypeError:
                pass
        self.fail(val, 'Must be {}'.format(self.description))