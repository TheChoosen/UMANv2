from jinja2 import Environment, FileSystemLoader
import traceback, sys

env = Environment(loader=FileSystemLoader(r'w:\UMANAPI\templates'))
try:
    t = env.get_template('RepubliqueduKwebec/index.html')
    out = t.render()
    print('---RENDER-OK---')
    print(out[:400])
except Exception:
    traceback.print_exc()
    sys.exit(1)
