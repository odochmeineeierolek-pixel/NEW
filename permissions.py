"""Kyto Permission Center: harte Regeln, nur der Benutzer darf Modi ändern."""
import json, time
from dataclasses import dataclass
from pathlib import Path
from .config import home_dir

DEFAULTS = {
    "trading.live": ("ask", "confirm_each_transaction"),
    "mining": ("allow", "allow_with_safety_limits"),
    "plugins.install": ("allow", "allow_after_validation"),
    "files.approved": ("allow", "allow_within_approved_directories"),
}

@dataclass
class Decision:
    decision: str
    reason: str

def inside(path, dirs):
    if ".." in str(path): return False
    n = str(path).replace("\\", "/").rstrip("/").lower()
    return any(n == d.replace("\\", "/").rstrip("/").lower() or n.startswith(d.replace("\\", "/").rstrip("/").lower() + "/") for d in dirs)

def decide(action, stored, c=None):
    c = c or {}
    if stored == "deny": return Decision("deny", "Vom Benutzer gesperrt")
    if action == "trading.live":
        if c.get("paper"): return Decision("allow", "Paper-Trading")
        if not c.get("dataFresh"): return Decision("deny", "Kursdaten fehlen oder sind veraltet")
        if not c.get("limitsOk"): return Decision("deny", "Risikolimit überschritten")
        return Decision("ask", "Bestätigung pro Auftrag erforderlich")
    if action == "mining":
        if not c.get("approvedHardware"): return Decision("deny", "Hardware nicht freigegeben")
        if not c.get("tempOk"): return Decision("deny", "Temperatur-/Leistungslimit verletzt")
        return Decision(stored, "Mit Sicherheitslimits")
    if action == "plugins.install":
        if not c.get("validated"): return Decision("deny", "Sicherheitsprüfung nicht bestanden")
        if c.get("criticalPerms"): return Decision("ask", "Kritische Rechte brauchen separate Freigabe")
        return Decision(stored, "Prüfung bestanden")
    if action == "files.approved":
        if not c.get("path") or not inside(c["path"], c.get("approvedDirs", [])):
            return Decision("deny", "Außerhalb freigegebener Ordner")
        if c.get("destructive"): return Decision("ask", "Destruktive Aktion braucht Bestätigung")
        return Decision(stored, "In freigegebenem Ordner")
    return Decision("ask", "Unbekannte Aktion")

class PermissionStore:
    def __init__(self):
        self.file = home_dir() / "permissions.json"
        self.log = home_dir() / "audit.log"
        self.data = {k: {"mode": m, "rule": r} for k, (m, r) in DEFAULTS.items()}
        try:
            saved = json.loads(self.file.read_text(encoding="utf-8"))
            for k, v in saved.items():
                if k in self.data and v.get("mode") in ("allow", "ask", "deny"): self.data[k]["mode"] = v["mode"]
        except Exception:
            pass
        self._save()
    def _save(self):
        self.file.write_text(json.dumps(self.data, indent=1), encoding="utf-8")
    def audit(self, module, action, result):
        with open(self.log, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | {module} | {action} | {result}\n")
    def set_mode(self, action, mode, actor="user"):
        if actor != "user":
            self.audit(actor, "perm.set:" + action, "blockiert"); return False, "Nur der Benutzer darf Berechtigungen ändern"
        if action not in self.data or mode not in ("allow", "ask", "deny"): return False, "Ungültig"
        if action == "trading.live" and mode == "allow": return False, "Live-Trading kann nicht pauschal erlaubt werden"
        self.data[action]["mode"] = mode; self._save(); self.audit("user", "perm.set:" + action, mode)
        return True, ""
    def check(self, module, action, ctx=None):
        r = decide(action, self.data.get(action, {"mode": "ask"})["mode"], ctx)
        self.audit(module, action, f"{r.decision}: {r.reason}")
        return r
