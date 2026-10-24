"""PIN-Sperre: scrypt-Hash, Versuchslimit, Zwangsänderung der Standard-PIN."""
import hashlib, hmac, json, os, time
from .config import home_dir

class PinService:
    def __init__(self):
        self.file = home_dir() / "pin.json"
        try: self.d = json.loads(self.file.read_text(encoding="utf-8"))
        except Exception: self.d = {}
        if "hash" not in self.d:
            self._store("6894"); self.d.update(mustChange=True, fails=0, lockUntil=0); self._save()
    def _hash(self, pin, salt): return hashlib.scrypt(pin.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)
    def _store(self, pin):
        salt = os.urandom(16); self.d.update(salt=salt.hex(), hash=self._hash(pin, salt).hex())
    def _save(self): self.file.write_text(json.dumps(self.d), encoding="utf-8")
    def _matches(self, pin): return hmac.compare_digest(self._hash(pin, bytes.fromhex(self.d["salt"])), bytes.fromhex(self.d["hash"]))
    @property
    def must_change(self): return bool(self.d.get("mustChange"))
    def locked_seconds(self): return max(0, int(self.d.get("lockUntil", 0) - time.time()))
    def verify(self, pin):
        if self.locked_seconds(): return "locked"
        if self._matches(pin): self.d["fails"] = 0; self._save(); return "ok"
        f = self.d.get("fails", 0) + 1; self.d["fails"] = f
        if f >= 5: self.d["lockUntil"] = time.time() + 30 * 2 ** min(f - 5, 6)
        self._save(); return "locked" if f >= 5 else "wrong"
    def change(self, old, new):
        if not (new.isdigit() and 4 <= len(new) <= 12): return False, "PIN: 4–12 Ziffern"
        if new == "6894": return False, "Standard-PIN nicht erlaubt"
        if not self._matches(old): return False, "Alte PIN falsch"
        self._store(new); self.d["mustChange"] = False; self._save(); return True, ""
