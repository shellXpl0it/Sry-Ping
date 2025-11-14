import os
import sys
import time
import socket
import subprocess
import select
import warnings
from typing import List
import json

# Dependency Check
try:
    import requests
    from pythonping import ping
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    from rich.live import Live
except ImportError as e:
    print(f"Fehler: Eine oder mehrere erforderliche Bibliotheken fehlen: {e.name}")
    print(f"Bitte installieren Sie die fehlenden Bibliotheken mit: pip install requests pythonping rich")
    sys.exit(1)

try:
    # Windows
    import msvcrt
    def getch() -> str:
        """Reads a single key press on Windows."""
        return msvcrt.getch().decode('utf-8', errors='ignore')
except ImportError:
    # Unix-basiert (Linux, macOS)
    import tty, termios
    def getch() -> str:
        """Reads a single key press on Unix-like systems."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

# --- Rich Console Initialization ---
console = Console()

# --- Constants ---
VERSION = "2.0.0"

# --- Settings Persistence ---
CONFIG_FILE = "config.json"

def load_settings() -> str:
    """Loads the ping mode from the config file."""
    try:
        with open(CONFIG_FILE, 'r') as f:
            settings = json.load(f)
            return settings.get("ping_mode", "Smart")
    except (FileNotFoundError, json.JSONDecodeError):
        return "Smart"  # Return default value if file not found or invalid

def save_settings() -> None:
    """Saves the current ping mode to the config file."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump({"ping_mode": ping_mode}, f, indent=4)

# Set Vars
warnings.filterwarnings("ignore", category=SyntaxWarning)  # Ignore syntax warnings
ping_mode = load_settings()  # Load settings on startup
author = "Arctis"
os.system(f"title SryPing - {VERSION} by {author}")

def get_title_panel() -> Panel:
    """Returns the application title as a rich Panel."""
    title_text = Text(f"""[magenta]  
  (\_/)
  ( •_•)
  / >🍙  [bold red]Sry Ping[/bold red] v{VERSION}[/magenta]""")
    return Panel(title_text, border_style="magenta", expand=False)

def show_menu() -> None:
    """Displays the main menu."""
    console.clear()
    console.print(get_title_panel())
    menu_text = Text.from_markup("\nBitte eine Option auswählen:\n\n"
                     "  [yellow]1)[/yellow] Hilfe\n"
                     "  [yellow]2)[/yellow] Ping starten\n"
                     "  [yellow]3)[/yellow] Einstellungen\n"
                     "  [yellow]q)[/yellow] Beenden")
    console.print(Panel(menu_text, title="Hauptmenü", border_style="cyan"))

def show_help() -> None:
    """Displays the help screen."""
    console.clear()
    help_text = Text.from_markup(
        "[yellow]1) [white]Hilfe anzeigen:[/white] Zeigt diesen Hilfebildschirm an.\n"
        "[yellow]2) [white]Ping starten:[/white] Startet den Ping-Vorgang, um die Latenz und Informationen zum Host zu überprüfen.\n"
        "[yellow]3) [white]Einstellungen:[/white] Ändern des Ping-Modus (Smart/Extended).\n"
        "[yellow]q) [white]Beenden:[/white] Verlässt die SryPing-Anwendung.\n\n"
        "[bold yellow]Anwendung:[/bold yellow]\n"
        "1. Eine Option aus dem Hauptmenü auswählen.\n"
        "2. Das Tool pingt den Host kontinuierlich an.\n"
        "3. Drücken Sie während des Pingens eine beliebige Taste, um zu stoppen und zum Menü zurückzukehren."
    )
    console.print(Panel(help_text, title="Hilfe", border_style="cyan", padding=(1, 2)))
    console.print("\n[white]Drücke eine beliebige Taste, um zum Hauptmenü zurückzukehren...[/white]", end="", flush=True)
    getch()

def show_settings() -> None:
    """Displays the settings menu and allows mode changes."""
    global ping_mode
    while True:
        console.clear()
        settings_text = Text.from_markup(
            f"Aktueller Ping-Modus: [bold green]{ping_mode}[/bold green]\n\n"
            "  [yellow]1)[/yellow] Modus umschalten (Smart/Extended)\n\n"
            "  [yellow]b)[/yellow] Zurück zum Hauptmenü\n"
        )
        console.print(Panel(settings_text, title="Einstellungen", border_style="cyan"))

        choice = getch().lower()

        if choice == '1': # Toggle between Smart and Extended
            ping_mode = "Extended" if ping_mode == "Smart" else "Smart"
            save_settings()
        elif choice == 'b': # Back to Main Menu
            break

def get_ip_info(ip_address: str) -> dict:
    """Retrieves IP and ASN information from an API."""
    info = {"asn": "N/A", "org": "N/A"}
    try:
        # Using the ip-api.com service for reliable ASN lookup
        response = requests.get(f"http://ip-api.com/json/{ip_address}?fields=org,as")
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        info["asn"] = data.get("as", "N/A")
        info["org"] = data.get("org", "N/A")
    except Exception as e:
        console.print(f"\n[bold red]Konnte ASN/Org-Info nicht abrufen: {e}[/bold red]")
    return info

def start_ping() -> None:
    """Handles the entire pinging process, from input to live display."""
    console.clear()
    console.print(Panel("[cyan]Ping starten[/cyan]", border_style="cyan"))
    host = console.input("[bold yellow]Geben Sie den zu pingenden Host ein: [/bold yellow]")

    try:
        ip_address = socket.gethostbyname(host)
    except socket.gaierror as e:
        console.print(f"[bold red]Fehler: Ungültiger Hostname - {e}[/bold red]")
        time.sleep(3)
        return
    except Exception as e:
        console.print(f"[bold red]Ein unerwarteter Fehler ist aufgetreten: {e}[/bold red]")
        time.sleep(3)
        return

    with console.status("[bold green]Rufe Host-Informationen ab...[/bold green]"):
        ip_info = get_ip_info(ip_address)

    info_table = Table(show_header=False, box=None, padding=(0, 1))
    info_table.add_column()
    info_table.add_column()
    info_table.add_row("[bold white]Host:[/bold white]", host, "[bold white]IP:[/bold white]", ip_address)
    info_table.add_row("[bold white]ASN:[/bold white]", ip_info['asn'], "[bold white]Organisation:[/bold white]", ip_info['org'])
    info_table.add_row("[bold white]Methode:[/bold white]", "ICMP Echo", "[bold white]Port:[/bold white]", "N/A")

    console.clear()
    console.print(Panel(info_table, title="Ping Informationen", border_style="green"))
    console.print("\n[cyan]Pinging... Drücken Sie eine beliebige Taste, um zu stoppen.[/cyan]")

    latencies: List[float] = []
    pings_sent = 0
    pings_failed = 0
    extended_ping_count = 0 # Zähler für den Extended-Modus

    def generate_output() -> Panel:
        """Generates the rich Panel for live display."""
        stats_table = Table(show_header=True, header_style="bold magenta", box=None)
        stats_table.add_column("Statistik", justify="right")
        stats_table.add_column("Wert", justify="left")
        stats_table.add_row("Gesendet", str(pings_sent))
        stats_table.add_row("Fehlgeschlagen", f"{pings_failed} ([red]{(pings_failed/pings_sent*100):.1f}%[/red])" if pings_sent > 0 else "0")
        if latencies:
            stats_table.add_row("Latenz (ms)", "")
            stats_table.add_row("  └─ Aktuell", f"{latencies[-1]:.2f}")
            stats_table.add_row("  └─ Min", f"{min(latencies):.2f}")
            stats_table.add_row("  └─ Max", f"{max(latencies):.2f}")
            stats_table.add_row("  └─ Avg", f"{(sum(latencies)/len(latencies)):.2f}")
        return Panel(stats_table, title="Live Statistik", border_style="yellow", expand=False)

    with Live(generate_output(), console=console, screen=False, refresh_per_second=4, vertical_overflow="visible") as live:
        try:
            while True:
                result = ping(host, timeout=1, count=1)
                pings_sent += 1

                # Logik zum Zurücksetzen des Bildschirms im Extended-Modus
                if ping_mode == "Extended":
                    extended_ping_count += 1
                    if extended_ping_count > 10:
                        console.clear()
                        console.print(Panel(info_table, title="Ping Informationen", border_style="green"))
                        console.print("\n[cyan]Pinging... Drücken Sie eine beliebige Taste, um zu stoppen.[/cyan]")
                        extended_ping_count = 1 # Zähler zurücksetzen


                if result.success:
                    latency = result.rtt_avg_ms
                    latencies.append(latency)
                    if ping_mode == "Extended":
                        console.print(f"[green]Ping erfolgreich, Latenz: {latency:.2f} ms[/green]")
                else:
                    pings_failed += 1
                    if ping_mode == "Extended":
                        console.print(f"[red]Ping fehlgeschlagen (Timeout)[/red]")

                live.update(generate_output())

                if msvcrt.kbhit() if 'msvcrt' in sys.modules else sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                    break
                time.sleep(1)
        except Exception as e:
            console.print(f"\n[bold red]Fehler während des Pings: {e}[/bold red]")

def main() -> None:
    """Main program loop."""
    while True:
        show_menu()
        choice = getch().lower()
        if choice == '1':
            show_help()
        elif choice == '2':
            start_ping()
        elif choice == '3':
            show_settings()
        elif choice == 'q':
            console.print(f"\n[bold green]Auf Wiedersehen![/bold green]")
            time.sleep(1)
            break
        else:
            console.print(f"[bold red]Ungültige Auswahl. Bitte erneut versuchen.[/bold red]")
            time.sleep(1)

if __name__ == "__main__":
    main()