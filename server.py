import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import uvicorn

if __name__ == '__main__':
    uvicorn.run("api.routes:app", host="0.0.0.0", port=8000, reload=True)