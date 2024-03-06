# THIS IS NEEDED FOR DJANGO

'''python needs to know this is a module'''

from pathlib import Path
import sys

__root = Path(__file__).parents[2]

sys.path.insert(0, str(__root)) 