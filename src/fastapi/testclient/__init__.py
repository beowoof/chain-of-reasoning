import asyncio
from dataclasses import dataclass
from typing import Any, Dict

from .. import UploadFile, HTTPException

@dataclass
class Response:
    status_code: int
    _json: Any
    def json(self) -> Any:
        return self._json

class TestClient:
    def __init__(self, app):
        self.app = app
        # Ensure startup is executed
        app._run_startup()
    def post(self, path: str, json: Dict[str, Any] | None = None, files=None, data=None):
        func = self.app.routes[path]
        kwargs = {}
        if json is not None:
            import inspect
            params = inspect.signature(func).parameters
            if len(params) == 1:
                (name, param), = params.items()
                ann = param.annotation
                try:
                    from pydantic import BaseModel  # type: ignore
                    if isinstance(ann, type) and issubclass(ann, BaseModel):
                        kwargs[name] = ann(**json)
                    else:
                        kwargs.update(json)
                except Exception:
                    kwargs.update(json)
            else:
                kwargs.update(json)
        if files is not None:
            # Assume single file upload
            fileinfo = next(iter(files.values()))
            filename, fileobj, _content_type = fileinfo
            upload = UploadFile(filename, fileobj)
            kwargs["file"] = upload
        if data is not None:
            kwargs.update(data)
        try:
            if asyncio.iscoroutinefunction(func):
                result = asyncio.run(func(**kwargs))
            else:
                result = func(**kwargs)
            status = 200
            body = result
        except HTTPException as e:
            status = e.status_code
            body = {"detail": e.detail}
        return Response(status, body)
