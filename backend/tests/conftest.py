import os
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

# Configuração fictícia exclusiva para testes.
# O adapter operacional privado não é carregado durante a suíte pública.
os.environ.setdefault("AUTH_DB_PATH", "/tmp/oncology-demo-test-auth.db")
os.environ.setdefault("SESSION_HOURS", "8")
os.environ.setdefault("APP_SECURE_COOKIES", "false")
os.environ.setdefault("DATA_ADAPTER", "")
