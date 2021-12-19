ALLOWED_HOSTS = ["*"]

# Modules in use, commented modules that you won't use
MODULES = [
    'authentication',
    'base',
    'booth',
    'census',
    'mixnet',
    'postproc',
    'store',
    'visualizer',
    'voting',
]

APIS = {
    'authentication': 'http://localhost:8081',
    'base': 'http://localhost:8081',
    'booth': 'http://localhost:8081',
    'census': 'http://localhost:8081',
    'mixnet': 'http://localhost:8081',
    'postproc': 'http://localhost:8081',
    'store': 'http://localhost:8081',
    'visualizer': 'http://localhost:8081',
    'voting': 'http://localhost:8081',
}

BASEURL = 'http://localhost:8081'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'alcazabadb',
        'USER': 'alcazaba',
        'PASSWORD': 'alcazaba',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# number of bits for the key, all auths should use the same number of bits
KEYBITS = 256
