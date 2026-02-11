#!/usr/bin/env python3
"""
S.O.I.L.E.R. Release Gate Runner
Executes strict P0/P1 checks for Production Readiness.
"""

import sys
import os

# Fix Windows console encoding for Unicode output
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass  # Older Python or non-tty
import yaml
import subprocess
import argparse
import time
import requests
import json
import socket
from pathlib import Path
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor

# Try to import Rich
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class GateRunner:
    def __init__(self, config_path: str, level: str):
        self.config_path = Path(config_path)
        self.level = level
        self.results = []
        # Use safe console options for Windows compatibility
        if RICH_AVAILABLE:
            self.console = Console(
                force_terminal=True,
                legacy_windows=False,  # Disable legacy Windows rendering
                no_color=sys.platform == "win32",  # Disable color on Windows
            )
        else:
            self.console = None
        self.failed = False

    def load_config(self) -> Dict[str, Any]:
        with open(self.config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def print_header(self):
        title = f"S.O.I.L.E.R. RELEASE GATE (Level: {self.level.upper()})"
        if RICH_AVAILABLE:
            self.console.print(Panel(
                f"[bold white]{title}[/]",
                subtitle="Strict Enforcement Mode",
                style="bold blue"
            ))
        else:
            print("=" * 60)
            print(title)
            print("=" * 60)

    def run_command(self, cmd: str, desc: str) -> Dict[str, Any]:
        """Run a shell command and return result."""
        print(f"Running: {desc}...")
        start_time = time.time()
        
        try:
            # Use shell=True for complex commands (e.g. pipes), but we generally avoid them
            # For cross-platform safety, we split arguments if single string
            result = subprocess.run(
                cmd,
                shell=True,
                check=False,
                start_new_session=False,
                capture_output=False  # Direct to stdout for transparency in CI
            )
            success = result.returncode == 0
        except Exception as e:
            print(f"Error executing command: {e}")
            success = False
        
        duration = time.time() - start_time
        return {
            "success": success,
            "duration": duration,
            "cmd": cmd
        }

    def check_streamlit_health(self) -> Dict[str, Any]:
        """
        Deterministic Streamlit Boot & Healthcheck.
        Does NOT rely on shell 'timeout' or '&'.
        """
        print("Booting Streamlit (Headless) for Healthcheck...")
        start_time = time.time()
        
        # 1. Find a free port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("", 0))
        port = sock.getsockname()[1]
        sock.close()
        
        # 2. Boot Streamlit
        env = os.environ.copy()
        env["HEADLESS"] = "true"
        
        cmd = [
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.headless", "true",
            "--server.port", str(port),
            "--browser.serverAddress", "localhost",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false"
        ]
        
        process = None
        success = False
        
        try:
            process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.DEVNULL, # Silence heavy logs
                stderr=subprocess.PIPE     # Capture errors if needed
            )
            
            # 3. Poll for health
            # Give it up to 20 seconds to boot
            for i in range(20):
                try:
                    url = f"http://localhost:{port}/_stcore/health"
                    resp = requests.get(url, timeout=2)
                    if resp.status_code == 200 and resp.text == "ok":
                        print(f"  ✅ Streamlit is HEALTHY at port {port}")
                        success = True
                        break
                except requests.RequestException:
                    pass
                
                if process.poll() is not None:
                     # Premature exit
                     success = False
                     break
                
                time.sleep(1)
                print(f"  ...waiting for boot ({i+1}/20s)...")
                
            if not success:
               print("  ❌ Streamlit failed to become healthy.")
               # Read stderr
               _, stderr = process.communicate(timeout=5)
               if stderr:
                   print(f"Stderrr: {stderr.decode('utf-8')}")

        except Exception as e:
            print(f"  ❌ Exception during boot: {e}")
            success = False
        finally:
            # 4. Terminate safely
            if process:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        
        return {
            "success": success,
            "duration": time.time() - start_time,
            "cmd": "internal:check_streamlit_health"
        }

    def execute(self):
        config = self.load_config()
        self.print_header()
        
        checks = []
        
        # Collect checks based on level
        if self.level in ["p0", "all"]:
            for c in config.get("p0_blockers", []):
                c["level"] = "P0"
                checks.append(c)
                
        if self.level in ["p1", "all"]:
            for c in config.get("p1_high_priority", []):
                c["level"] = "P1"
                checks.append(c)
        
        if not checks:
            print("No checks found for this level.")
            return

        # Execute checks
        for check in checks:
            cid = check["id"]
            desc = check["desc"]
            
            header = f"[{check['level']}] {desc}"
            if RICH_AVAILABLE:
                self.console.print(f"\n[bold cyan]> {header}[/]")
            else:
                print(f"\n> {header}")
            
            result = {}
            if check.get("check_type") == "internal_function":
                func_name = check.get("check_func")
                if func_name == "check_streamlit_health":
                    result = self.check_streamlit_health()
                else:
                    print(f"Unknown internal function: {func_name}")
                    result = {"success": False, "duration": 0}
            else:
                result = self.run_command(check["check_cmd"], desc)
            
            # Store result
            self.results.append({
                "id": cid,
                "desc": desc,
                "level": check["level"],
                "success": result["success"],
                "duration": result["duration"]
            })
            
            if not result["success"]:
                self.failed = True
                if RICH_AVAILABLE:
                    self.console.print(f"[bold red]❌ FAILED: {desc}[/]")
                else:
                    print(f"❌ FAILED: {desc}")
                
                # Strict mode: fail fast? No, run all checks to show full report
            else:
                if RICH_AVAILABLE:
                    self.console.print(f"[bold green]✅ PASSED ({result['duration']:.2f}s)[/]")
                else:
                    print(f"✅ PASSED ({result['duration']:.2f}s)")

    def report(self):
        # Generate JSON artifact
        json_path = Path("artifacts/gate_report.json")
        json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(json_path, "w") as f:
            json.dump({
                "results": self.results,
                "failed": self.failed,
                "generated_at": time.time()
            }, f, indent=2)

        # Generate Markdown Summary
        md_path = Path("artifacts/release_gate_summary.md")
        with open(md_path, "w", encoding="utf-8") as f:
            status_icon = "❌" if self.failed else "✅"
            f.write(f"# {status_icon} Release Gate Summary (Level: {self.level.upper()})\n\n")
            f.write("| Level | Check | Status | Duration |\n")
            f.write("|---|---|---|---|\n")
            for res in self.results:
                icon = "✅" if res["success"] else "❌"
                f.write(f"| {res['level']} | {res['desc']} | {icon} | {res['duration']:.2f}s |\n")
            
            if self.failed:
                f.write("\n\n**GATE FAILED** - Blocking build.\n")
            else:
                f.write("\n\n**GATE PASSED** - Ready for next stage.\n")

        # Print Table
        if RICH_AVAILABLE:
            table = Table(title="Gate Results", header_style="bold magenta")
            table.add_column("Level", style="white")
            table.add_column("Check", style="cyan")
            table.add_column("Status", justify="center")
            table.add_column("Duration", justify="right")
            
            for res in self.results:
                status = "[green]PASS[/]" if res["success"] else "[bold red]FAIL[/]"
                table.add_row(
                    res["level"],
                    res["desc"],
                    status,
                    f"{res['duration']:.2f}s"
                )
            self.console.print("\n")
            self.console.print(table)
        
        if self.failed:
            print("\n❌ GATE FAILED. Blocking build.")
            sys.exit(1)
        else:
            print("\n✅ GATE PASSED. Ready for next stage.")
            sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="Run Release Gate")
    parser.add_argument("--level", choices=["p0", "p1", "all"], default="all", help="Gate level to enforce")
    parser.add_argument("--config", default="gates/release_gate.yml", help="Path to gate config")
    args = parser.parse_args()
    
    runner = GateRunner(args.config, args.level)
    runner.execute()
    runner.report()

if __name__ == "__main__":
    main()
