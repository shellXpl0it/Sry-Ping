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

VERSION = "1.0.1"

CONFIG_FILE = "config.json"


ping_mode: str = "Smart"
saved_pings: List[dict] = []

def load_settings() -> None:
    """Loads the ping mode and saved pings from the config file."""
    global ping_mode, saved_pings
    try:
        with open(CONFIG_FILE, 'r') as f:
            settings = json.load(f)
            ping_mode = settings.get("ping_mode", "Smart")
            saved_pings = settings.get("saved_pings", [])
    except (FileNotFoundError, json.JSONDecodeError):
        ping_mode = "Smart"
        saved_pings = []
    save_settings()

def save_settings() -> None:
    """Saves the current ping mode and saved pings to the config file."""
    settings = {"ping_mode": ping_mode, "saved_pings": saved_pings}
    with open(CONFIG_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

warnings.filterwarnings("ignore", category=SyntaxWarning)
load_settings()
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
                     "  [yellow]3)[/yellow] Saved Pings\n"
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

def manage_saved_pings() -> None:
    """Manages saved ping configurations."""
    global saved_pings
    while True:
        console.clear()
        console.print(Panel(Text("Manage your saved ping configurations.", justify="center"), title="Saved Pings", border_style="cyan"))

        if not saved_pings:
            console.print("\n[italic yellow]No saved pings yet.[/italic yellow]\n")
        else:
            saved_pings_table = Table(show_header=True, header_style="bold green")
            saved_pings_table.add_column("#", style="dim")
            saved_pings_table.add_column("Name")
            saved_pings_table.add_column("Host")
            saved_pings_table.add_column("Method")
            saved_pings_table.add_column("Port", justify="right")

            for i, p in enumerate(saved_pings):
                port_display = str(p.get("port", "N/A")) if p["method"] == "TCP" else "N/A"
                saved_pings_table.add_row(str(i + 1), p["name"], p["host"], p["method"], port_display)
            console.print(saved_pings_table)

        menu_text = Text.from_markup(
            "\n  [yellow]1)[/yellow] Create New Saved Ping\n"
            "  [yellow]2)[/yellow] Edit Saved Ping\n"
            "  [yellow]3)[/yellow] Delete Saved Ping\n"
            "  [yellow]b)[/yellow] Back to Main Menu\n"
        )
        console.print(Panel(menu_text, title="Options", border_style="magenta"))

        choice = getch().lower()

        if choice == '1':
            create_new_saved_ping()
        elif choice == '2':
            if not saved_pings:
                console.print("[bold red]No saved pings to edit.[/bold red]")
                time.sleep(1)
                continue
            console.print("\n[bold yellow]Enter the number of the ping to edit:[/bold yellow]", end="")
            try:
                ping_index = int(getch()) - 1
                if 0 <= ping_index < len(saved_pings):
                    edit_saved_ping(ping_index)
                else:
                    console.print("\n[bold red]Invalid number.[/bold red]", end="")
                    time.sleep(1)
            except ValueError:
                console.print("\n[bold red]Invalid input. Please enter a number.[/bold red]", end="")
                time.sleep(1)
        elif choice == '3':
            if not saved_pings:
                console.print("[bold red]No saved pings to delete.[/bold red]")
                time.sleep(1)
                continue
            console.print("\n[bold yellow]Enter the number of the ping to delete:[/bold yellow]", end="")
            try:
                ping_index = int(getch()) - 1
                if 0 <= ping_index < len(saved_pings):
                    del saved_pings[ping_index]
                    save_settings()
                    console.print("\n[bold green]Ping deleted successfully![/bold green]")
                    time.sleep(1)
                else:
                    console.print("\n[bold red]Invalid number.[/bold red]", end="")
                    time.sleep(1)
            except ValueError:
                console.print("\n[bold red]Invalid input. Please enter a number.[/bold red]", end="")
                time.sleep(1)
        elif choice == 'b':
            break
        else:
            console.print("[bold red]Invalid choice. Please try again.[/bold red]")
            time.sleep(1)

def create_new_saved_ping() -> None:
    """Prompts user for details to create a new saved ping."""
    global saved_pings
    console.clear()
    console.print(Panel(Text("Create New Saved Ping", justify="center"), title="New Ping", border_style="green"))

    name = console.input("[bold yellow]Enter a name for this ping: [/bold yellow]").strip()
    if not name:
        console.print("[bold red]Name cannot be empty.[/bold red]")
        time.sleep(1)
        return

    host = console.input("[bold yellow]Enter the host (e.g., google.com or 8.8.8.8): [/bold yellow]").strip()
    if not host:
        console.print("[bold red]Host cannot be empty.[/bold red]")
        time.sleep(1)
        return

    method_choice = console.input("[bold yellow]Select method (1 for ICMP, 2 for TCP): [/bold yellow]").strip()
    method = ""
    port = None

    if method_choice == '1':
        method = "ICMP"
    elif method_choice == '2':
        method = "TCP"
        port_str = console.input("[bold yellow]Enter the port number (e.g., 80, 443): [/bold yellow]").strip()
        try:
            port = int(port_str)
            if not 0 < port < 65536:
                raise ValueError("Port out of range.")
        except ValueError:
            console.print(f"[bold red]Error: Invalid port number. Ping not saved.[/bold red]")
            time.sleep(2)
            return
    else:
        console.print("[bold red]Invalid method choice. Ping not saved.[/bold red]")
        time.sleep(1)
        return

    new_ping = {"name": name, "host": host, "method": method}
    if port:
        new_ping["port"] = port

    saved_pings.append(new_ping)
    save_settings()
    console.print("[bold green]Ping saved successfully![/bold green]")
    time.sleep(1)

def edit_saved_ping(index: int) -> None:
    """Prompts user to edit an existing saved ping."""
    global saved_pings
    ping_to_edit = saved_pings[index]
    console.clear()
    console.print(Panel(Text(f"Editing: {ping_to_edit['name']}", justify="center"), title="Edit Ping", border_style="yellow"))

    new_name = console.input(f"[bold yellow]Enter new name (current: {ping_to_edit['name']}): [/bold yellow]").strip()
    if new_name:
        ping_to_edit['name'] = new_name

    new_host = console.input(f"[bold yellow]Enter new host (current: {ping_to_edit['host']}): [/bold yellow]").strip()
    if new_host:
        ping_to_edit['host'] = new_host


    console.print(f"[bold yellow]Current method: {ping_to_edit['method']}[/bold yellow]")
    method_choice = console.input("[bold yellow]Change method? (1 for ICMP, 2 for TCP, leave blank to keep current): [/bold yellow]").strip()

    if method_choice == '1':
        ping_to_edit['method'] = "ICMP"
        ping_to_edit.pop('port', None)
    elif method_choice == '2':
        ping_to_edit['method'] = "TCP"
        current_port = ping_to_edit.get('port', 'N/A')
        port_str = console.input(f"[bold yellow]Enter new port (current: {current_port}): [/bold yellow]").strip()
        if port_str:
            try:
                new_port = int(port_str)
                if not 0 < new_port < 65536:
                    raise ValueError("Port out of range.")
                ping_to_edit['port'] = new_port
            except ValueError:
                console.print(f"[bold red]Error: Invalid port number. Port not updated.[/bold red]")
                time.sleep(2)
    elif method_choice != '':
        console.print("[bold red]Invalid method choice. Method not updated.[/bold red]")
        time.sleep(1)

    save_settings()
    console.print("[bold green]Ping updated successfully![/bold green]")
    time.sleep(1)

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

def _start_ping_session(host: str, ip_address: str, method: str, ping_function: callable) -> None:
    """Handles the generic pinging process, UI, and statistics."""
    with console.status("[bold green]Retrieving host information...[/bold green]"):
        ip_info = get_ip_info(ip_address)

    info_table = Table(show_header=False, box=None, padding=(0, 1))
    info_table.add_column()
    info_table.add_column()
    info_table.add_row("[bold white]Host:[/bold white]", host, "[bold white]IP:[/bold white]", ip_address)
    info_table.add_row("[bold white]ASN:[/bold white]", ip_info['asn'], "[bold white]Organization:[/bold white]", ip_info['org'])
    info_table.add_row("[bold white]Method:[/bold white]", method, "[bold white]Mode:[/bold white]", f"[bold]{ping_mode}[/bold]")

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
                latency, success, message = ping_function()

                if success:
                    latencies.append(latency)
                else:
                    pings_failed += 1

                if ping_mode == "Extended":
                    console.print(message)
                    extended_ping_count += 1
                    if extended_ping_count > 10:
                        console.clear()
                        console.print(Panel(info_table, title="Ping Information", border_style="green"))
                        console.print("\n[cyan]Pinging... Press any key to stop.[/cyan]")
                        extended_ping_count = 1

                live.update(generate_output())

                if 'msvcrt' in sys.modules:
                    if msvcrt.kbhit():
                        break
                elif sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                    break
                time.sleep(1)
        except Exception as e:
            console.print(f"\n[bold red]Error during ping: {e}[/bold red]")


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

    def icmp_ping_executor():
        result = ping(host, timeout=1, count=1)
        if result.success:
            latency = result.rtt_avg_ms
            message = f"[green]Ping successful, latency: {latency:.2f} ms[/green]"
            return latency, True, message
        else:
            message = f"[red]Ping failed (Timeout)[/red]"
            return -1, False, message

    _start_ping_session(host, ip_address, "ICMP Echo", icmp_ping_executor)

def select_and_start_saved_ping() -> None:
    """Displays saved pings and prompts user to start one."""
    console.clear()
    console.print(Panel(Text("Select a saved ping to start.", justify="center"), title="Start Saved Ping", border_style="cyan"))

    if not saved_pings:
        console.print("\n[italic yellow]No saved pings yet. Create one from the 'Saved Pings' menu.[/italic yellow]\n")
        console.print("[cyan]Returning to menu in 3 seconds...[/cyan]")
        time.sleep(3)
        return

    saved_pings_table = Table(show_header=True, header_style="bold green")
    saved_pings_table.add_column("#", style="dim")
    saved_pings_table.add_column("Name")
    saved_pings_table.add_column("Host")
    saved_pings_table.add_column("Method")
    saved_pings_table.add_column("Port", justify="right")

    for i, p in enumerate(saved_pings):
        port_display = str(p.get("port", "N/A")) if p["method"] == "TCP" else "N/A"
        saved_pings_table.add_row(str(i + 1), p["name"], p["host"], p["method"], port_display)
    console.print(saved_pings_table)

    console.print("\n[bold yellow]Enter the number of the ping to start (or 'b' to go back):[/bold yellow]", end="")
    try:
        choice = getch().lower()
        if choice == 'b':
            return
        ping_index = int(choice) - 1
        if 0 <= ping_index < len(saved_pings):
            start_saved_ping(saved_pings[ping_index])
    except (ValueError, IndexError):
        console.print("\n[bold red]Invalid selection.[/bold red]")
        time.sleep(1)

def start_saved_ping(ping_config: dict) -> None:
    """Starts a ping session using a saved ping configuration."""
    host = ping_config["host"]
    method = ping_config["method"]
    port = ping_config.get("port")

    try:
        ip_address = socket.gethostbyname(host)
    except socket.gaierror as e:
        console.print(f"[bold red]Error: Invalid hostname for saved ping '{ping_config['name']}' - {e}[/bold red]")
        time.sleep(3)
        return
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred for saved ping '{ping_config['name']}': {e}[/bold red]")
        time.sleep(3)
        return

    if method == "ICMP":
        def icmp_ping_executor():
            result = ping(host, timeout=1, count=1)
            if result.success:
                latency = result.rtt_avg_ms
                message = f"[green]Ping successful, latency: {latency:.2f} ms[/green]"
                return latency, True, message
            else:
                message = f"[red]Ping failed (Timeout)[/red]"
                return -1, False, message
        _start_ping_session(host, ip_address, "ICMP Echo", icmp_ping_executor)
    elif method == "TCP":
        if port is None:
            console.print(f"[bold red]Error: TCP ping '{ping_config['name']}' is missing a port number.[/bold red]")
            time.sleep(3)
            return

        def tcp_ping_executor():
            start_time = time.perf_counter()
            try:
                with socket.create_connection((ip_address, port), timeout=2):
                    end_time = time.perf_counter()
                    latency = (end_time - start_time) * 1000
                    message = f"[green]Connection to port {port} successful, latency: {latency:.2f} ms[/green]"
                    return latency, True, message
            except Exception as e:
                error_message = f"failed ({type(e).__name__})"
                message = f"[red]Connection to port {port} {error_message}[/red]"
                return -1, False, message
        _start_ping_session(host, ip_address, f"TCP Connect (Port {port})", tcp_ping_executor)
    else:
        console.print(f"[bold red]Error: Unknown ping method '{method}' for saved ping '{ping_config['name']}'.[/bold red]")
        time.sleep(3)

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

    def tcp_ping_executor():
        start_time = time.perf_counter()
        try:
            with socket.create_connection((ip_address, port), timeout=2):
                end_time = time.perf_counter()
                latency = (end_time - start_time) * 1000
                message = f"[green]Connection to port {port} successful, latency: {latency:.2f} ms[/green]"
                return latency, True, message
        except Exception as e:
            error_message = f"failed ({type(e).__name__})"
            message = f"[red]Connection to port {port} {error_message}[/red]"
            return -1, False, message
    
    _start_ping_session(host, ip_address, f"TCP Connect (Port {port})", tcp_ping_executor)

def select_ping_method() -> None:
    """Displays a menu to select the ping method."""
    while True:
        console.clear()
        ping_menu_text = Text.from_markup(
            "Select a ping method:\n\n"
            "  [yellow]1)[/yellow] ICMP Ping (Standard)\n"
            "  [yellow]2)[/yellow] TCP Ping (Port Check)\n"
            "  [yellow]3)[/yellow] From Saved Pings\n\n"
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
        elif choice == '3':
            select_and_start_saved_ping()
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
        elif choice == '3':
            manage_saved_pings()
        elif choice == 'q':
            console.print(f"\n[bold green]Goodbye![/bold green]")
            time.sleep(1)
            break
        else:
            console.print(f"[bold red]Invalid choice. Please try again.[/bold red]")
            time.sleep(1)

if __name__ == "__main__":
    main()