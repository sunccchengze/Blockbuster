import importlib.util, os, sys
def load_film(path):
    path = os.path.abspath(path); d = os.path.dirname(path)
    if d not in sys.path: sys.path.insert(0, d)
    spec = importlib.util.spec_from_file_location('film_' + str(abs(hash(path))), path); m = importlib.util.module_from_spec(spec)
    cwd = os.getcwd(); os.chdir(d)
    try: spec.loader.exec_module(m)
    finally: os.chdir(cwd)
    return m.FILM
