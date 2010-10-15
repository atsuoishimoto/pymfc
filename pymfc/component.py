import sys, traceback
from pymfc.util import synchronized

_getComponent_default_omitted=object()

class _ComponentMap(object):
    def __init__(self):
        self._map = {}
    
    @synchronized
    def _add(self, type, name, componentClass):
        key = (type, name)
            
        if key in self._map:
            print (type, name), "is already registered"
        assert key not in self._map
        self._map[key] = componentClass
    

    def _getComponent(self, obj, name, default=_getComponent_default_omitted):
        ret = self._getComponentFactory(obj, name)
        if ret:
            return ret(obj)
        elif default is not _getComponent_default_omitted:
            return default
        else:
            raise RuntimeError, "No component '%s' for %s" % (name, type(obj))

    def _getComponentFactory(self, obj, name, default=_getComponent_default_omitted):
        ret = None
        typename = getattr(obj, '___PYMFC_OBJECT_TYPE_NAME___', None)
        if typename:
            ret = self._map.get((obj.___PYMFC_OBJECT_TYPE_NAME___, name), None)
            
            if ret is None:
                for cls in obj.__class__.__mro__[1:]:
                    typename = getattr(cls, '___PYMFC_OBJECT_TYPE_NAME___', None)
                    if typename is not None:
                        ret = self._map.get((typename, name), None)
                        if ret:
                            break
        if not ret:
            ret = self._map.get((None, name), None)

        if not ret and (default is not _getComponent_default_omitted):
            return default
            
        return ret
        

_map = _ComponentMap()

def OBJECT_TYPE(name):
    namespace = sys._getframe(1).f_locals
    namespace['___PYMFC_OBJECT_TYPE_NAME___'] = name

def IMPLEMENTS_COMPONENT(name, types=None):
    namespace = sys._getframe(1).f_locals
    assert '___PYMFC_COMPONENTS___' not in namespace
    namespace['___PYMFC_COMPONENTS___'] = (name, types)

class ComponentType(type):
    def __init__(cls, name, bases, dict):
        super(ComponentType, cls).__init__(name, bases, dict)
        if '___PYMFC_COMPONENTS___' in dict:
            name, types = dict['___PYMFC_COMPONENTS___']
            if types is not None:
                for type in types:
                    _map._add(type, name, cls)
            else:
                _map._add(types, name, cls)

class ComponentBase(object):
#    __slots__  = ('_parent', '_itemui')
    __slots__ = ('_obj',)
    __metaclass__ = ComponentType

    def __init__(self, obj):
        self._obj = obj

def getComponent(name, obj, default=_getComponent_default_omitted):
    return _map._getComponent(obj, name, default)

def getComponentFactory(name, obj, default=_getComponent_default_omitted):
    return _map._getComponentFactory(obj, name, default)

def getObjectType(obj):
    return obj.___PYMFC_OBJECT_TYPE_NAME___

def getComponentName(obj):
    return obj.___PYMFC_COMPONENTS___[0]

def isObjectType(obj, typenames):
    if isinstance(typenames, str):
        typenames = [typenames]
    for cls in obj.__class__.__mro__:
        t = getattr(cls, '___PYMFC_OBJECT_TYPE_NAME___', None)
        if t:
            if t in typenames:
                return True
    return False
