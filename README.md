# jodel-runner
Automatisierter täglicher Run eines Python-Selenium-Skripts mit GitHub Actions.
# Daily Bot

Dieses Repository führt ein Python-Skript mithilfe von [GitHub Actions](https://docs.github.com/en/actions) automatisch jeden Tag zu einer festgelegten Uhrzeit aus.  
Das Skript verwendet [Selenium](https://www.selenium.dev/), um einen automatisierten Workflow im Browser (Headless Chrome) durchzuführen.

## Features
- Automatischer täglicher Start via GitHub Actions (Cron)
- Headless-Chrome-Unterstützung für CI/CD-Umgebungen
- Nutzung von GitHub Secrets zur sicheren Speicherung von Zugangsdaten
- Log-Export als Artefakt nach jedem Run

## Aufbau
- `script.py` – das Hauptskript mit Selenium
- `requirements.txt` – Abhängigkeiten
- `.github/workflows/run.yml` – Workflow-Definition für GitHub Actions

## Konfiguration
1. Repository klonen oder forken.  
2. In den Repo-Einstellungen unter **Settings → Secrets and variables → Actions** folgende Secrets anlegen:
   - `SJ_USERNAME` → Benutzername
   - `SJ_PASSWORD` → Passwort
3. Workflow manuell starten oder auf die geplante tägliche Ausführung warten.

## Zeitplan
Das Skript wird täglich um **01:00 UTC** ausgeführt (entspricht 02:00 Uhr im Winter bzw. 03:00 Uhr im Sommer in Berlin).
