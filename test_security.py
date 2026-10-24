import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ["YAVIS_HOME"] = tempfile.mkdtemp()
from yavis.pin import PinService
from yavis.permissions import PermissionStore, decide
p = PinService()
assert p.must_change and p.verify("6894") == "ok" and p.verify("0000") == "wrong"
assert p.change("6894", "6894")[0] is False and p.change("6894", "4711")[0] is True
assert PinService().verify("4711") == "ok" and not PinService().must_change
q = PinService()
for _ in range(5): r = q.verify("1")
assert r == "locked" and q.verify("4711") == "locked"
s = PermissionStore()
assert s.data["trading.live"]["mode"] == "ask" and s.data["mining"]["mode"] == "allow"
assert s.set_mode("trading.live", "allow")[0] is False and s.set_mode("mining", "deny", actor="plugin")[0] is False
assert decide("trading.live", "allow", {"dataFresh": True, "limitsOk": True}).decision == "ask"
assert decide("trading.live", "ask", {}).decision == "deny"
assert decide("files.approved", "allow", {"path": "C:/x", "approvedDirs": ["D:/k"]}).decision == "deny"
assert decide("plugins.install", "allow", {}).decision == "deny"
assert s.set_mode("mining", "deny")[0] and s.check("mining", "mining", {"approvedHardware": True, "tempOk": True}).decision == "deny"
print("Sicherheitstests bestanden")
