import tempfile
import subprocess
import os
def print_png(data, printer):
    """ (data, printer): Печатает png b(картинку) на указаном принтере"""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(data)
    try:
        subprocess.run(["lp","-d",printer,f.name],check=True,timeout=15)
    finally:
        os.remove(f.name)