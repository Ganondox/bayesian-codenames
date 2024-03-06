"""
This is the basic code needed to navigate the codebase, because
Python doesn't do very good package/module managment. To get to
a parent of cross module, you need to add the root to sys.path
"""

from pathlib import Path
import sys

__root = Path(__file__).parent

sys.path.insert(0, str(__root)) 
sys.path.insert(0, str(__root.parents[0])) 