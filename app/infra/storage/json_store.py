from __future__ import annotations

import json
import os
import time
from tempfile import NamedTemporaryFile
from dataclasses import dataclass
from contextlib import contextmanager
from pathlib import Path
from threading import Lock
from typing import Any, Iterator, Dict, Optional


class JsonStoreError(RuntimeError):
    """Base error for JSON store failures."""


class JsonCorruptedError(JsonStoreError):
    """Raised when JSON exists but cannot be parsed."""


@dataclass(frozen=True)
class JsonStore:
    """
    JSON file store with:
      - atomic writes (temp file + os.replace)
      - best-effort cross-process lock using lock-file (NO fcntl)
      - in-process safety via threading.Lock
    """

    path: Path
    lock_timeout_s: float = 2.0
    lock_poll_interval_s: float = 0.05

    _mutex: Lock = Lock() # in-process mutex

    def __post_init__(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
    
    def read(self) -> Dict[str, Any]:
        """
        Reads JSON content.
        Raises JsonCorruptedError when file exists but JSON is invalid.
        """
        with self._mutex, self._lock_file():
            if not self.path.exists():
                return {}
            try:
                raw = self.path.read_text(encoding='utf-8')
                if not raw.strip():
                    return {}
                data = json.loads(raw)
                if isinstance(data, dict):
                    return data
                return {"_root": data}
            
            except json.JSONDecodeError as e:
                raise JsonCorruptedError(f"JSON file corrupted: {self.path}") from e
            
            except OSError as e:
                raise JsonStoreError(f"Failed to read JSON file: {self.path}") from e
    
    def write(self, data: Dict[str, Any]) -> None:
        """
        Atomically writes JSON to disk:
          - write to temp in same directory
          - fsync temp
          - os.replace(temp, target)
        """
        payload = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)
        
        with self._mutex, self._lock_file():
            try:
                tmp_dir = str(self.path.parent)
                with NamedTemporaryFile(
                    mode="w",
                    encoding="utf-8",
                    dir=tmp_dir,
                    delete=False,
                    prefix=f".{self.path.name}.",
                    suffix=".tmp",
                ) as tmp:
                    tmp_path = Path(tmp.name)
                    tmp.write(payload)
                    tmp.flush()
                    os.fsync(tmp.fileno())

                os.replace(str(tmp_path), str(self.path))

                self._fysync_dir(self.path.parent)

            except OSError as e:
                raise JsonStoreError(f"Failed to write JSON file: {self.path}") from e
            
            finally:
                try:
                    if 'tmp_path' in locals() and tmp_path.exists():
                        tmp_path.unlink(missing_ok=True)
                except OSError:
                    pass
    
    def update(self, fn) -> Dict[str, Any]:
        """
        Reads JSON, applies fn(data) to it, writes back the result.
        Returns the updated data.
        """
        with self._mutex, self._lock_file():
            current = self.read_unlocked()
            updated = fn(current)
            if not isinstance(updated, dict):
                raise TypeError("Update function must return a dict")
            self.write_unlocked(updated)
            return updated
    
    # --------- unlocked helpers ---------

    def read_unlocked(self) -> Dict[str, Any]:
        if not self.path.exists():
            return {}
        try:
            raw = self.path.read_text(encoding="utf-8")
            if not raw.strip():
                return {}
            data = json.loads(raw)
            return data if isinstance(data, dict) else {"_root": data}
        except json.JSONDecodeError as e:
            raise JsonCorruptedError(f"Corrupted JSON at {self.path}") from e
        except OSError as e:
            raise JsonStoreError(f"Failed reading {self.path}") from e

    def write_unlocked(self, data: Dict[str, Any]) -> None:
        payload = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)
        tmp_dir = str(self.path.parent)
        tmp_path: Optional[Path] = None
        try:
            with NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=tmp_dir,
                delete=False,
                prefix=f".{self.path.name}.",
                suffix=".tmp",
            ) as tmp:
                tmp_path = Path(tmp.name)
                tmp.write(payload)
                tmp.flush()
                os.fsync(tmp.fileno())
            os.replace(str(tmp_path), str(self.path))
            self._fsync_dir(self.path.parent)
        except OSError as e:
            raise JsonStoreError(f"Failed writing {self.path}") from e
        finally:
            try:
                if tmp_path and tmp_path.exists():
                    tmp_path.unlink(missing_ok=True)
            except OSError:
                pass

    # --------- lock implementation ---------
    @property
    def _lock_path(self) -> Path:
        return self.path.with_suffix(self.path.suffix + ".lock")
    
    @contextmanager
    def _lock_file(self) -> Iterator[None]:
        start = time.monotonic()
        fd: Optional[int] = None

        while True:
            try:
                # O_EXCL makes creation atomic: if exists -> FileExistsError
                fd = os.open(str(self._lock_path), os.O_CREAT | os.O_EXCL | os.O_RDWR)
                # record owner pid (debugging aid)
                os.write(fd, str(os.getpid()).encode("ascii", errors="ignore"))
                break
            except FileExistsError:
                if (time.monotonic() - start) >= self.lock_timeout_s:
                    raise JsonStoreError(
                        f"Could not acquire lock for {self.path} within {self.lock_timeout_s}s"
                    )
                time.sleep(self.lock_poll_interval_s)
        try:
            yield
        finally:
            try:
                if fd is not None:
                    os.close(fd)
            finally:
                try:
                    self._lock_path.unlink(missing_ok=True)
                except OSError:
                    pass

    @staticmethod
    def _fsync_dir(directory: Path) -> None:
        """
        Best-effort fsync the directory entry so the rename is durable on POSIX.
        On platforms where opening a directory fails, we simply skip.
        """
        try:
            dir_fd = os.open(str(directory), os.O_RDONLY)
        except OSError:
            return
        try:
            os.fsync(dir_fd)
        except OSError:
            pass
        finally:
            try:
                os.close(dir_fd)
            except OSError:
                pass