import os
import sys
import time
import socket
import subprocess
import select
import warnings
from typing import List
import json

try:
    import requests
    from pythonping import ping
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    from rich.live import Live
except ImportError as e:
    print(f"Error: One or more required libraries are missing: {e.name}")
    print(f"Please install the missing libraries with: pip install requests pythonping rich")
    sys.exit(1)

try:
    import msvcrt
    def getch() -> str:
        """Reads a single key press on Windows."""
        return msvcrt.getch().decode('utf-8', errors='ignore')
except ImportError:
    import tty, termios
    def getch() -> str:
        """Reads a single key press on Unix-like systems."""
        fd = sys.stdin.fileno()
        old_settings = None
        try:
            old_settings = termios.tcgetattr(fd)
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        except (termios.error, AttributeError):
            ch = sys.stdin.read(1)
        finally:
            if old_settings:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

console = Console()

VERSION = "1.0.0"

CONFIG_FILE = "config.json"

def load_settings() -> str:
    """Loads the ping mode from the config file."""
    try:
        with open(CONFIG_FILE, 'r') as f:
            settings = json.load(f)
            return settings.get("ping_mode", "Smart")
    except (FileNotFoundError, json.JSONDecodeError):
        return "Smart"

def save_settings() -> None:
    """Saves the current ping mode to the config file."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump({"ping_mode": ping_mode}, f, indent=4)

warnings.filterwarnings("ignore", category=SyntaxWarning)
ping_mode = load_settings()
os.system(f"title SryPing - {VERSION} by shellXploit")

def get_title_panel() -> Panel:
    """Returns the application title as a rich Panel."""
    title_text = Text.from_markup(f"""[magenta]  
  (\_/)
  ( •_•)
  / >🍙  [bold red]Sry-Ping[/bold red] v{VERSION}[/magenta]""")
    return Panel(title_text, border_style="magenta", expand=False)

def show_menu() -> None:
    """Displays the main menu."""
    console.clear()
    console.print(get_title_panel())
    menu_text = Text.from_markup("\nPlease select an option:\n\n"
                     "  [yellow]1)[/yellow] Start Ping\n"
                     "  [yellow]2)[/yellow] Settings\n"
                     "  [yellow]q)[/yellow] Quit")
    console.print(Panel(menu_text, title="Main Menu", border_style="cyan"))

def show_settings() -> None:
    """Displays the settings menu and allows mode changes."""
    global ping_mode
    while True:
        console.clear()
        settings_text = Text.from_markup(
            f"Current Ping Mode: [bold green]{ping_mode}[/bold green]\n\n"
            "  [yellow]1)[/yellow] Toggle Mode (Smart/Extended)\n\n"
            "  [yellow]b)[/yellow] Back to Main Menu\n"
        )
        console.print(Panel(settings_text, title="Settings", border_style="cyan"))

        choice = getch().lower()

        if choice == '1':
            ping_mode = "Extended" if ping_mode == "Smart" else "Smart"
            save_settings()
        elif choice == 'b':
            break

def get_ip_info(ip_address: str) -> dict:
    """Retrieves IP and ASN information from an API."""
    info = {"asn": "N/A", "org": "N/A"}
    try:
        response = requests.get(f"http://ip-api.com/json/{ip_address}?fields=org,as")
        response.raise_for_status()
        data = response.json()
        info["asn"] = data.get("as", "N/A")
        info["org"] = data.get("org", "N/A")
    except Exception as e:
        console.print(f"\n[bold red]Could not retrieve ASN/Org info: {e}[/bold red]")
    return info

def start_icmp_ping() -> None:
    """Handles the ICMP pinging process."""
    console.clear()
    host = console.input("[bold yellow]Enter the host to ping: [/bold yellow]")

    try:
        ip_address = socket.gethostbyname(host)
    except socket.gaierror as e:
        console.print(f"[bold red]Error: Invalid hostname - {e}[/bold red]")
        time.sleep(3)
        return
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred: {e}[/bold red]")
        time.sleep(3)
        return

    with console.status("[bold green]Retrieving host information...[/bold green]"):
        ip_info = get_ip_info(ip_address)

    info_table = Table(show_header=False, box=None, padding=(0, 1))
    info_table.add_column()
    info_table.add_column()
    info_table.add_row("[bold white]Host:[/bold white]", host, "[bold white]IP:[/bold white]", ip_address)
    info_table.add_row("[bold white]ASN:[/bold white]", ip_info['asn'], "[bold white]Organization:[/bold white]", ip_info['org'])
    info_table.add_row("[bold white]Method:[/bold white]", "ICMP Echo", "[bold white]Mode:[/bold white]", f"[bold]{ping_mode}[/bold]")

    console.clear()
    console.print(Panel(info_table, title="Ping Information", border_style="green"))
    console.print("\n[cyan]Pinging... Press any key to stop.[/cyan]")

    latencies: List[float] = []
    pings_sent = 0
    pings_failed = 0
    extended_ping_count = 0

    def generate_output() -> Panel:
        """Generates the rich Panel for live display."""
        stats_table = Table(show_header=True, header_style="bold magenta", box=None)
        stats_table.add_column("Statistic", justify="right")
        stats_table.add_column("Value", justify="left")
        stats_table.add_row("Sent", str(pings_sent))
        stats_table.add_row("Failed", f"{pings_failed} ([red]{(pings_failed/pings_sent*100):.1f}%[/red])" if pings_sent > 0 else "0")
        if latencies:
            stats_table.add_row("Latency (ms)", "")
            stats_table.add_row("  └─ Current", f"{latencies[-1]:.2f}")
            stats_table.add_row("  └─ Min", f"{min(latencies):.2f}")
            stats_table.add_row("  └─ Max", f"{max(latencies):.2f}")
            stats_table.add_row("  └─ Avg", f"{(sum(latencies)/len(latencies)):.2f}")
        return Panel(stats_table, title="Live Statistics", border_style="yellow", expand=False)

    with Live(generate_output(), console=console, screen=False, refresh_per_second=4, vertical_overflow="visible") as live:
        try:
            while True:
                result = ping(host, timeout=1, count=1)
                pings_sent += 1

                if ping_mode == "Extended":
                    extended_ping_count += 1
                    if extended_ping_count > 10:
                        console.clear()
                        console.print(Panel(info_table, title="Ping Information", border_style="green"))
                        console.print("\n[cyan]Pinging... Press any key to stop.[/cyan]")
                        extended_ping_count = 1


                if result.success:
                    latency = result.rtt_avg_ms
                    latencies.append(latency)
                    if ping_mode == "Extended":
                        console.print(f"[green]Ping successful, latency: {latency:.2f} ms[/green]")
                else:
                    pings_failed += 1
                    if ping_mode == "Extended":
                        console.print(f"[red]Ping failed (Timeout)[/red]")

                live.update(generate_output())

                if msvcrt.kbhit() if 'msvcrt' in sys.modules else sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                    break
                time.sleep(1)
        except Exception as e:
            console.print(f"\n[bold red]Error during ping: {e}[/bold red]")

def start_tcp_ping() -> None:
    """Handles the TCP pinging process by attempting to connect to a port."""
    console.clear()
    host = console.input("[bold yellow]Enter the host for TCP ping: [/bold yellow]")
    port_str = console.input("[bold yellow]Enter the port number (e.g., 80, 443): [/bold yellow]")

    try:
        port = int(port_str)
        if not 0 < port < 65536:
            raise ValueError("Port out of range.")
    except ValueError:
        console.print(f"[bold red]Error: Invalid port number.[/bold red]")
        time.sleep(3)
        return

    try:
        ip_address = socket.gethostbyname(host)
    except socket.gaierror as e:
        console.print(f"[bold red]Error: Invalid hostname - {e}[/bold red]")
        time.sleep(3)
        return

    with console.status("[bold green]Retrieving host information...[/bold green]"):
        ip_info = get_ip_info(ip_address)

    info_table = Table(show_header=False, box=None, padding=(0, 1))
    info_table.add_column()
    info_table.add_column()
    info_table.add_row("[bold white]Host:[/bold white]", host, "[bold white]IP:[/bold white]", ip_address)
    info_table.add_row("[bold white]ASN:[/bold white]", ip_info['asn'], "[bold white]Organization:[/bold white]", ip_info['org'])
    info_table.add_row("[bold white]Method:[/bold white]", "TCP Connect", "[bold white]Mode:[/bold white]", f"[bold]{ping_mode}[/bold]")

    console.clear()
    console.print(Panel(info_table, title="Ping Information", border_style="green"))
    console.print("\n[cyan]Pinging... Press any key to stop.[/cyan]")

    latencies: List[float] = []
    pings_sent = 0
    pings_failed = 0
    extended_ping_count = 0

    def generate_output() -> Panel:
        """Generates the rich Panel for live display."""
        stats_table = Table(show_header=True, header_style="bold magenta", box=None)
        stats_table.add_column("Statistic", justify="right")
        stats_table.add_column("Value", justify="left")
        stats_table.add_row("Sent", str(pings_sent))
        stats_table.add_row("Failed", f"{pings_failed} ([red]{(pings_failed/pings_sent*100):.1f}%[/red])" if pings_sent > 0 else "0")
        if latencies:
            stats_table.add_row("Latency (ms)", "")
            stats_table.add_row("  └─ Current", f"{latencies[-1]:.2f}")
            stats_table.add_row("  └─ Min", f"{min(latencies):.2f}")
            stats_table.add_row("  └─ Max", f"{max(latencies):.2f}")
            stats_table.add_row("  └─ Avg", f"{(sum(latencies)/len(latencies)):.2f}")
        return Panel(stats_table, title="Live Statistics", border_style="yellow", expand=False)

    with Live(generate_output(), console=console, screen=False, refresh_per_second=4, vertical_overflow="visible") as live:
        try:
            while True:
                pings_sent += 1
                latency = -1
                error_message = ""

                start_time = time.perf_counter()
                try:
                    with socket.create_connection((ip_address, port), timeout=2):
                        end_time = time.perf_counter()
                        latency = (end_time - start_time) * 1000
                        latencies.append(latency)
                except Exception as e:
                    pings_failed += 1
                    error_message = f"failed ({type(e).__name__})"

                if ping_mode == "Extended":
                    if latency != -1:
                        console.print(f"[green]Connection to port {port} successful, latency: {latency:.2f} ms[/green]")
                    else:
                        console.print(f"[red]Connection to port {port} {error_message}[/red]")

                live.update(generate_output())

                if msvcrt.kbhit() if 'msvcrt' in sys.modules else sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                    break
                time.sleep(1)
        except Exception as e:
            console.print(f"\n[bold red]Error during TCP ping: {e}[/bold red]")

def select_ping_method() -> None:
    """Displays a menu to select the ping method."""
    while True:
        console.clear()
        ping_menu_text = Text.from_markup(
            "Select a ping method:\n\n"
            "  [yellow]1)[/yellow] ICMP Ping (Standard)\n"
            "  [yellow]2)[/yellow] TCP Ping (Port Check)\n\n"
            "  [yellow]b)[/yellow] Back to Main Menu\n"
        )
        console.print(Panel(ping_menu_text, title="Ping Method", border_style="cyan"))
        choice = getch().lower()

        if choice == '1':
            start_icmp_ping()
            break
        elif choice == '2':
            start_tcp_ping()
            break
        elif choice == 'b':
            break

def main() -> None:
    """Main program loop."""
    while True:
        show_menu()
        choice = getch().lower()
        if choice == '1':
            select_ping_method()
        elif choice == '2':
            show_settings()
        elif choice == 'q':
            console.print(f"\n[bold green]Goodbye![/bold green]")
            time.sleep(1)
            break
        else:
            console.print(f"[bold red]Invalid choice. Please try again.[/bold red]")
            time.sleep(1)

if __name__ == "__main__":
    main()