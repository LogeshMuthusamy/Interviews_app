import sys
print(f"Python {sys.version}")
try:
    import streamlit
    print("streamlit: OK")
except ImportError as e:
    print(f"streamlit: MISSING ({e})")

try:
    import speech_recognition
    print("speech_recognition: OK")
except ImportError as e:
    print(f"speech_recognition: MISSING ({e})")

try:
    import numpy
    print("numpy: OK")
except ImportError as e:
    print(f"numpy: MISSING ({e})")

try:
    import plotly
    print("plotly: OK")
except ImportError as e:
    print(f"plotly: MISSING ({e})")

try:
    import sentence_transformers
    print("sentence_transformers: OK")
except ImportError as e:
    print(f"sentence_transformers: MISSING ({e})")
