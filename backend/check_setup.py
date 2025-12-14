import sys
import os

print(f"Python Executable: {sys.executable}")
print(f"Format: {sys.version}")

try:
    import langchain_groq
    print(f"SUCCESS: langchain_groq found at {langchain_groq.__file__}")
except ImportError as e:
    print(f"FAILURE: {e}")

try:
    from langchain_groq import ChatGroq
    print("SUCCESS: ChatGroq imported successfully")
except ImportError as e:
    print(f"FAILURE importing ChatGroq: {e}")
