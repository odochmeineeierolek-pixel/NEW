"""Sperrfenster vor dem Start (Qt)."""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PySide6.QtCore import Qt
from .pin import PinService

def _dlg(title, text, echo=True):
    d = QDialog(); d.setWindowTitle(title); d.setMinimumWidth(340); lay = QVBoxLayout(d)
    h = QLabel("KYTO TASK"); h.setAlignment(Qt.AlignCenter); h.setStyleSheet("font-size:22px;letter-spacing:6px;color:#f4c430")
    lay.addWidget(h); lay.addWidget(QLabel(text))
    return d, lay

def run_lock() -> bool:
    pin = PinService()
    while True:
        d, lay = _dlg("Kyto Task – Sperre", "PIN eingeben:")
        e = QLineEdit(); e.setEchoMode(QLineEdit.Password); e.setAlignment(Qt.AlignCenter); lay.addWidget(e)
        msg = QLabel(""); msg.setStyleSheet("color:#e5383b"); lay.addWidget(msg)
        n = QLabel("Die PIN ist eine App-Sperre und ersetzt keine Windows-Kontosicherheit."); n.setWordWrap(True); n.setStyleSheet("color:#888;font-size:11px"); lay.addWidget(n)
        b = QPushButton("Entsperren"); lay.addWidget(b); b.setDefault(True)
        result = {}
        def go():
            r = pin.verify(e.text()); result["r"] = r
            if r == "ok": d.accept()
            elif r == "locked": msg.setText(f"Gesperrt für {pin.locked_seconds()} s")
            else: msg.setText("Falsche PIN"); e.clear()
        b.clicked.connect(go); e.returnPressed.connect(go)
        if not d.exec(): return False
        if result.get("r") == "ok": break
    while pin.must_change:
        d, lay = _dlg("PIN festlegen", "Die Standard-PIN muss geändert werden.\nNeue PIN (4–12 Ziffern):")
        a = QLineEdit(); a.setEchoMode(QLineEdit.Password); b2 = QLineEdit(); b2.setEchoMode(QLineEdit.Password); b2.setPlaceholderText("Wiederholen")
        lay.addWidget(a); lay.addWidget(b2); msg = QLabel(""); msg.setStyleSheet("color:#e5383b"); lay.addWidget(msg)
        ok = QPushButton("Speichern"); lay.addWidget(ok)
        def save():
            if a.text() != b2.text(): msg.setText("PINs stimmen nicht überein"); return
            good, err = pin.change("6894", a.text())
            msg.setText(err) if not good else d.accept()
        ok.clicked.connect(save)
        if not d.exec(): return False
    return True
