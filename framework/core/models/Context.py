class Context(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __setattr__(self, name, value):
        if name in dict.__dict__.keys():
            return super().__setattr__(name, value)
        self[name] = value
        return value

    def __getattribute__(self, name):
        if name in dict.__dict__.keys():
            return super().__getattribute__(name)
        elif name in self.keys():
            return self[name]
        else:
            raise AttributeError
