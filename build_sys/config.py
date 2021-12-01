import json
import os.path

def ensure_config_key(config, key, description, default_gen, value_constructor):
  '''returns True if the config was updated.'''
  if value_constructor is None:
    value_constructor = lambda x: x
  if key not in config:
    if description is not None:
      print('{}: {}'.format(key, description))
    default_value = default_gen() if default_gen else None
    if default_value is None:
      val = input('{}? '.format(key))
      if not val:
        raise Exception('Config value for {} not set.'.format(key))
      config[key] = value_constructor(val)
    else:
      val = input('{} [{}]? '.format(key, default_value))
      if not val:
        val = default_value
      config[key] = value_constructor(val)
    return True
  return False

def defualt_files(default_fns):
  def closure():
    for default_fn in default_fns:
      if os.path.exists(default_fn):
        return default_fn
    return None
  return closure

def construct_staging_dirs(user_input):
  return {'dev': user_input}

class DynamicConfig:
  def __init__(self):
    self.required_keys = {
      'staging_dirs': ('The director(y|ies) to which finalized files are copied.', None, construct_staging_dirs),
      'browserify_bin': ('A path to the browserify binary.', defualt_files([
        'npm_libs/node_modules/.bin/browserify',
        '/usr/bin/browserify',
        '/usr/local/bin/browserify',
      ]), None),
      'uglifyjs_bin': ('A path to the uglifyjs binary.', defualt_files([
        'npm_libs/node_modules/.bin/uglifyjs',
        '/usr/bin/uglifyjs',
        '/usr/local/bin/uglifyjs',
      ]), None),
    }
    self.config_fn = 'local_config.json'
    self.config = {}
    if os.path.exists(self.config_fn):
      with open(self.config_fn) as f:
        self.config = json.load(f)
  def _save(self):
    with open(self.config_fn, 'w') as f:
      json.dump(self.config, f, indent='  ', sort_keys=True)
  def __getitem__(self, key):
    if key in self.config:
      return self.config[key]
    if key in self.required_keys:
      if ensure_config_key(self.config, key, *self.required_keys[key]):
        self._save()
    raise KeyError(key)
  def __contains__(self, key):
    if key in self.config:
      return True
    if key in self.required_keys:
      if ensure_config_key(self.config, key, *self.required_keys[key]):
        self._save()
    return False

def local_config():
  return DynamicConfig()
