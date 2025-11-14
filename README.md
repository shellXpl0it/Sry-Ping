# SryPing - Erweiterte Ping-Anwendung

## Übersicht

SryPing ist ein vielseitiges und erweiterbares Ping-Dienstprogramm, das über die Standardfunktionen hinausgeht und erweiterte Funktionen für Netzwerkdiagnose und -überwachung bietet. Es wurde mit einer benutzerfreundlichen Oberfläche, Echtzeitstatistiken und anpassbaren Einstellungen entwickelt und ist sowohl für Anfänger als auch für erfahrene Netzwerkadministratoren geeignet.

## Funktionen

-   **Visuell ansprechende Oberfläche:** Verwendet die Rich-Bibliothek für eine farbenfrohe und informative Konsolenausgabe.
-   **Adaptive Ping-Modi:** Bietet "Smart"- und "Extended"-Modi, um den Detaillierungsgrad der Ping-Informationen zu steuern.
-   **Echtzeitstatistiken:** Zeigt Live-Ping-Statistiken an, einschließlich Latenz, Paketverlust und mehr.
-   **ASN- und Organisations-Lookup:** Ruft ASN- (Autonomous System Number) und Organisationsinformationen für die Ziel-IP-Adresse ab.
-   **Konfigurierbare Einstellungen:** Ermöglicht es Benutzern, Einstellungen wie den Ping-Modus zu ändern und diese für zukünftige Sitzungen zu speichern.
-   **Fehlerbehandlung:** Bietet eine robuste Fehlerbehandlung für häufige Probleme wie ungültige Hostnamen oder Netzwerkfehler.
-   **Unterbrechungsgesteuerter Betrieb:** Ermöglicht es Benutzern, den Ping-Prozess jederzeit durch Drücken einer beliebigen Taste zu stoppen.

## Installation

### Voraussetzungen

-   Python 3.6 oder höher
-   pip (Python Package Installer)

### Installationsschritte

1.  **Klonen Sie das Repository:**

    ```bash
    git clone https://github.com/Arctis/SryPing.git
    cd SryPing
    ```

2.  **Installieren Sie die erforderlichen Bibliotheken:**

    ```bash
    pip install requests pythonping rich
    ```

### Optionale Abhängigkeiten

-   `msvcrt` (nur Windows): Für die Eingabe ohne Echo. Wird automatisch verwendet, falls verfügbar.

## Verwendung

1.  **Führen Sie die Anwendung aus:**

    ```bash
    python sry.py
    ```

2.  **Hauptmenü:**

    -   Wählen Sie Optionen aus dem Hauptmenü, indem Sie die entsprechende Zahl oder den entsprechenden Buchstaben eingeben.
    -   Verwenden Sie die Option "Ping starten", um einen Host zu pingen und Live-Statistiken anzuzeigen.
    -   Verwenden Sie die Option "Einstellungen", um den Ping-Modus zu ändern.
    -   Verwenden Sie die Option "Hilfe", um Anwendungsdetails anzuzeigen.
    -   Verwenden Sie die Option "Beenden", um die Anwendung zu beenden.

## Konfiguration

Die Anwendung speichert die Einstellungen in einer `config.json`-Datei. Die folgenden Einstellungen können konfiguriert werden:

-   `ping_mode`: Legt den Ping-Modus auf "Smart" oder "Extended" fest.

## Erweiterte Ping-Modi

SryPing bietet zwei verschiedene Ping-Modi, um den Detaillierungsgrad der Ping-Informationen anzupassen:

-   **Smart-Modus:** In diesem Modus zeigt SryPing eine zusammengefasste Ansicht der Ping-Statistiken an, einschließlich der Anzahl der gesendeten und fehlgeschlagenen Pings sowie der minimalen, maximalen und durchschnittlichen Latenz.

-   **Extended-Modus:** Im Extended-Modus bietet SryPing detailliertere Informationen zu jedem Ping-Versuch. Zusätzlich zu den im Smart-Modus angezeigten Statistiken zeigt der Extended-Modus die Latenz für jeden einzelnen Ping an und gibt an, ob ein Ping fehlgeschlagen ist. Darüber hinaus löscht der Extended-Modus alle 10 Pings den Bildschirm, um die Ausgabe übersichtlich zu halten.

## Fehlerbehandlung

SryPing enthält eine umfassende Fehlerbehandlung, um einen reibungslosen Betrieb zu gewährleisten:

-   **Ungültige Hostnamen:** Wenn ein ungültiger Hostname angegeben wird, zeigt die Anwendung eine Fehlermeldung an und kehrt zum Hauptmenü zurück.
-   **Netzwerkfehler:** Bei Netzwerkfehlern wie Timeouts oder nicht erreichbaren Hosts zeigt die Anwendung eine Fehlermeldung an und setzt den Ping-Vorgang fort.
-   **ASN-Lookup-Fehler:** Wenn das Abrufen von ASN-Informationen fehlschlägt, zeigt die Anwendung eine Warnmeldung an und fährt mit dem Ping-Vorgang fort.

## Fehlerbehebung

-   **Probleme bei der Installation:** Stellen Sie sicher, dass alle erforderlichen Bibliotheken mit `pip` installiert sind.
-   **Ping-Probleme:** Überprüfen Sie die Netzwerkverbindung und stellen Sie sicher,dass der Zielhost erreichbar ist.
-   **Darstellungsprobleme:** Stellen Sie sicher, dass Ihr Terminal die 256-Farben-Unterstützung für die Rich-Bibliothek unterstützt.

## Mitwirkende

-   Arctis

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert.

## Danksagung

-   Die Rich-Bibliothek für die Erstellung einer ansprechenden Konsolenoberfläche.
-   Die Python-Ping-Bibliothek für die Vereinfachung von Ping-Operationen.
-   Der ip-api.com-Dienst für die Bereitstellung von ASN- und Organisationsinformationen.

## Logo

Das Logo wurde mit Hilfe von DALL-E erstellt.
