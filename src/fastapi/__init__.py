import asyncio
from contextlib import asynccontextmanager

class HTTPException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

class UploadFile:
    def __init__(self, filename: str, file):
        self.filename = filename
        self._file = file
    async def read(self):
        return self._file.read()

class _Dep:
    def __init__(self, default=None):
        self.default = default

def File(default=None):
    return _Dep(default)

def Form(default=None):
    return _Dep(default)

class FastAPI:
    def __init__(self, lifespan=None):
        self.lifespan = lifespan
        self.routes = {}
        self._lifespan_cm = None
    def _run_startup(self):
        if self.lifespan and self._lifespan_cm is None:
            async def runner():
                self._lifespan_cm = self.lifespan(self)
                await self._lifespan_cm.__aenter__()
            asyncio.run(runner())
    def post(self, path: str):
        def decorator(func):
            self.routes[path] = func
            return func
        return decorator

# Provide asynccontextmanager in submodule
__all__ = [
    "FastAPI",
    "UploadFile",
    "File",
    "Form",
    "HTTPException",
    "asynccontextmanager",
]
