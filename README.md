# Sry-Ping

A modern, feature-rich, cross-platform ping utility built with Python and the Rich library. Sry-Ping provides a visually appealing and informative way to check host latency and gather network information.

![Sry-Ping Demo](https://cdn.discordapp.com/attachments/1439272416093143061/1439272579272675328/image.png?ex=6919ea8b&is=6918990b&hm=3805a8b529617feaf2006c74e3cdd26cd16796ad5094c1ff853ea9505a36b5a4&)

## ✨ Features

*   **Live Statistics:** View real-time ping statistics including current, min, max, and average latency, plus packet loss percentage.
*   **Host Information:** Automatically resolves the IP address and retrieves ASN (Autonomous System Number) and organization details for the target host.
*   **Two Display Modes:**
    *   **Smart Mode:** A clean, live-updating panel showing key statistics.
    *   **Extended Mode:** A verbose, scrolling output showing the result of each individual ping, similar to the traditional `ping` command.
*   **Cross-Platform:** Works on both Windows and Unix-like systems (Linux, macOS).
*   **User-Friendly Interface:** A simple, menu-driven TUI for easy navigation and operation.
*   **Configuration Persistence:** Your chosen ping mode is saved and loaded automatically between sessions.

## 📦 Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/shellxpl0it/sry-ping.git
    cd sry-ping
    ```

2.  **Install the required Python libraries:**
    The script will prompt you if dependencies are missing, but you can install them ahead of time.
    ```bash
    pip install requests pythonping rich
    ```

## 🚀 Usage

Run the script from your terminal:
```bash
python sry.py
```

You will be greeted with the main menu:

*   **Start Ping:** Prompts you to enter a hostname (e.g., `google.com` or `8.8.8.8`) and begins the pinging process.
*   **Settings:** Allows you to toggle between `Smart` and `Extended` ping modes.
*   **Help:** Displays a help screen with usage instructions.
*   **Quit:** Exits the application.

While pinging, you can **press any key to stop** and return to the main menu.

## ⚙️ Configuration

The application saves your preferred ping mode (`Smart` or `Extended`) in a `config.json` file in the same directory. You can edit this file directly or change the mode via the in-app settings menu.

---

## 📜 License

**Copyright (c) 2025 shellXploit**
**Proprietary License — Private Use Only**

**Grant of Limited License**
You (the Licensor) grant the Licensee a non-exclusive, non-transferable, revocable, personal license to use the Licensed Material solely for private, non-commercial, personal purposes on devices owned or controlled by the Licensee.

**Prohibited Uses**
The Licensee may not, under any circumstances:

*   Modify, adapt, translate, or create derivative works of the Licensed Material.
*   Distribute, publish, upload, share, sell, sublicense, rent, lease, or otherwise make the Licensed Material available to third parties.
*   Remove, alter, or obscure any copyright, trademark, or other proprietary notices included with the Licensed Material.
*   Use the Licensed Material for any commercial purpose, including offering it as part of a service or product for which a fee is charged.

**Ownership**
All title, ownership rights, and intellectual property rights in the Licensed Material remain with the Licensor. No rights are granted except as expressly set forth in this License.

**Termination**
This License is effective until terminated. The Licensor may terminate this License immediately if the Licensee breaches any term. Upon termination, the Licensee must cease all use of, and permanently delete or destroy, all copies of the Licensed Material in their possession or control and certify compliance on request.

**No Warranty**
The Licensed Material is provided "AS IS" without warranty of any kind. The Licensor disclaims all warranties, express or implied, including merchantability, fitness for a particular purpose, and non-infringement.

**Limitation of Liability**
To the maximum extent permitted by law, the Licensor is not liable for any indirect, incidental, consequential, special, punitive, or exemplary damages arising from the use or inability to use the Licensed Material.