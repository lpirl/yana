from pkgutil import walk_packages
from inspect import getmembers, isclass

def load_classes(path, base_class=object):
  classes = set()
  for module_loader, module_name, _ in walk_packages(path):
      module = module_loader.find_module(module_name).load_module(module_name)
      for cls_name, cls in getmembers(module):
          if not isclass(cls):
              continue
          if not issubclass(cls, base_class):
              continue
          if cls_name.startswith("Abstract"):
              continue
          exec('from %s import %s' % (module_name, cls_name))
          exec('classes.add(%s)' % cls_name)
  return classes
