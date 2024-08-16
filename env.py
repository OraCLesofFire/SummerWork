#!/usr/bin/env python3

class Env:
    def __init__(self, **kwargs):
        self.env = {}
        self.update(kwargs)

    def update(self, kwargs):
        for (key, val) in kwargs.items():
            assert key not in self.env, "current env: {} key:{}".format(self.env, key)
            self.env[key] = val
            continue
        return

    def __call__(self, **kwargs):
        env = Env(**self.env)
        env.update(kwargs)
        return env

    def __getitem__(self, key):
        assert key in self.env, "current env: {} key:{}".format(self.env, key)
        return self.env[key]

    def __contains__(self, key):
        return key in self.env

    def keys(self):
        return list(self.env.keys())

    def vals(self):
        return list(self.env.values())


env = Env(x=True, y=False)
env = env(z=False)
res = env['x'] and not env['y'] and not env['z']
assert 'x' in env
assert 'q' not in env
# print(res)
