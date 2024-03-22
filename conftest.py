import os
import sys
from pathlib import Path

# sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(os.path.realpath(os.path.dirname(__file__)+"/src"))

print(sys.path)