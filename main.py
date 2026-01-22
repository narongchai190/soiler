#!/usr/bin/env python3
"""
S.O.I.L.E.R. - Soil Optimization & Intelligent Land Expert Recommender
Main Entry Point - Multi-Agent AI System for Precision Agriculture

This script demonstrates the full 6-agent pipeline with professional console output.
"""

# CRITICAL: Bootstrap UTF-8 encoding FIRST before any other imports
import sys
sys.path.insert(0, ".")
from core.encoding_bootstrap import bootstrap_utf8
bootstrap_utf8()

import time
from typing import Any, Dict

# Try to import Rich for beautiful console output, fallback to basic printing
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.text import Text
    from rich.box import DOUBLE, ROUNDED, HEAVY
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("[!] Rich library not found. Using standard output.")
    print("    Install with: pip install rich\n")

from core.orchestrator import SoilerOrchestrator


class SoilerConsole:
    """High-tech console interface for S.O.I.L.E.R. system."""

    BANNER = r"""
   ███████╗ ██████╗ ██╗██╗     ███████╗██████╗
   ██╔════╝██╔═══██╗██║██║     ██╔════╝██╔══██╗
   ███████╗██║   ██║██║██║     █████╗  ██████╔╝
   ╚════██║██║   ██║██║██║     ██╔══╝  ██╔══██╗
   ███████║╚██████╔╝██║███████╗███████╗██║  ██║
   ╚══════╝ ╚═════╝ ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝
    """

    AGENTS = [
        ("SoilAnalyst", "🧪", "Soil Analysis & Series Identification"),
        ("CropExpert", "🌾", "Crop Planning & Yield Optimization"),
        ("EnvironmentExpert", "🌤️", "Weather & Climate Analysis"),
        ("FertilizerAdvisor", "🧬", "Nutrient & Fertilizer Planning"),
        ("MarketAnalyst", "📊", "Economic Analysis & ROI"),
        ("ChiefReporter", "📋", "Executive Report Generation"),
    ]

    def __init__(self):
        if RICH_AVAILABLE:
            # Force terminal mode and UTF-8 to avoid Windows legacy console encoding issues
            self.console = Console(force_terminal=True, legacy_windows=False)
        else:
            self.console = None

    def print(self, *args, **kwargs):
        """Print with Rich if available, else standard print."""
        if RICH_AVAILABLE:
            self.console.print(*args, **kwargs)
        else:
            # Strip Rich markup for standard print
            text = " ".join(str(a) for a in args)
            print(text)

    def clear(self):
        """Clear the console."""
        if RICH_AVAILABLE:
            self.console.clear()

    def print_banner(self):
        """Display the S.O.I.L.E.R. banner."""
        if RICH_AVAILABLE:
            self.console.print(Panel(
                Text(self.BANNER, style="bold green", justify="center"),
                title="[bold cyan]Soil Optimization & Intelligent Land Expert Recommender[/]",
                subtitle="[dim]Multi-Agent AI System v1.0[/]",
                box=DOUBLE,
                border_style="green"
            ))
        else:
            print("=" * 60)
            print(self.BANNER)
            print("  Soil Optimization & Intelligent Land Expert Recommender")
            print("           Multi-Agent AI System v1.0")
            print("=" * 60)

    def print_boot_sequence(self):
        """Display system boot sequence with agent initialization."""
        if RICH_AVAILABLE:
            self.console.print("\n[bold yellow]⚡ SYSTEM BOOT SEQUENCE[/]\n")

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=self.console
            ) as progress:
                boot_task = progress.add_task("[cyan]Initializing S.O.I.L.E.R. Core...", total=100)

                # Core initialization
                for i in range(40):
                    time.sleep(0.02)
                    progress.update(boot_task, advance=2.5)

                progress.update(boot_task, description="[cyan]Loading Knowledge Base...")
                for i in range(20):
                    time.sleep(0.02)
                    progress.update(boot_task, advance=1.5)

                progress.update(boot_task, description="[cyan]Calibrating AI Agents...")
                for i in range(20):
                    time.sleep(0.02)
                    progress.update(boot_task, advance=1.5)

            self.console.print()

            # Agent initialization
            for agent_name, emoji, description in self.AGENTS:
                self.console.print(f"  {emoji} [bold green]✓[/] [cyan]{agent_name}[/] [dim]- {description}[/]")
                time.sleep(0.15)

            self.console.print("\n[bold green]✅ ALL SYSTEMS ONLINE[/]\n")
            time.sleep(0.5)
        else:
            print("\n⚡ SYSTEM BOOT SEQUENCE\n")
            print("Initializing S.O.I.L.E.R. Core...")
            time.sleep(0.3)
            print("Loading Knowledge Base...")
            time.sleep(0.3)
            print("Calibrating AI Agents...")
            time.sleep(0.3)

            for agent_name, emoji, description in self.AGENTS:
                print(f"  {emoji} ✓ {agent_name} - {description}")
                time.sleep(0.1)

            print("\n✅ ALL SYSTEMS ONLINE\n")

    def print_scenario(self, scenario: Dict[str, Any]):
        """Display the analysis scenario."""
        if RICH_AVAILABLE:
            table = Table(title="📍 Analysis Scenario", box=ROUNDED, border_style="blue")
            table.add_column("Parameter", style="cyan", no_wrap=True)
            table.add_column("Value", style="green")

            table.add_row("👤 Farmer", scenario.get("farmer", "N/A"))
            table.add_row("📍 Location", scenario.get("location", "N/A"))
            table.add_row("🌾 Crop", scenario.get("crop", "N/A"))
            table.add_row("📐 Field Size", f"{scenario.get('field_size_rai', 0)} rai ({scenario.get('field_size_rai', 0) * 0.16:.2f} ha)")
            table.add_row("🧪 pH", str(scenario.get("ph", "N/A")))
            table.add_row("🧪 Nitrogen (N)", f"{scenario.get('nitrogen', 0)} mg/kg")
            table.add_row("🧪 Phosphorus (P)", f"{scenario.get('phosphorus', 0)} mg/kg")
            table.add_row("🧪 Potassium (K)", f"{scenario.get('potassium', 0)} mg/kg")
            table.add_row("💰 Budget", f"{scenario.get('budget_thb', 0):,} THB")

            self.console.print(table)
            self.console.print()
        else:
            print("\n📍 Analysis Scenario")
            print("=" * 40)
            print(f"  👤 Farmer: {scenario.get('farmer', 'N/A')}")
            print(f"  📍 Location: {scenario.get('location', 'N/A')}")
            print(f"  🌾 Crop: {scenario.get('crop', 'N/A')}")
            print(f"  📐 Field Size: {scenario.get('field_size_rai', 0)} rai")
            print(f"  🧪 pH: {scenario.get('ph', 'N/A')}")
            print(f"  🧪 N-P-K: {scenario.get('nitrogen', 0)}-{scenario.get('phosphorus', 0)}-{scenario.get('potassium', 0)} mg/kg")
            print(f"  💰 Budget: {scenario.get('budget_thb', 0):,} THB")
            print("=" * 40 + "\n")

    def print_thought_chain(self, observations: list):
        """Display the agent thought chain."""
        if RICH_AVAILABLE:
            self.console.print(Panel(
                "[bold cyan]🔗 AGENT THOUGHT CHAIN[/]",
                box=HEAVY,
                border_style="cyan"
            ))

            for i, obs in enumerate(observations, 1):
                agent = obs.get("agent", "Unknown")
                observation = obs.get("observation", "No observation")

                # Find emoji for agent
                emoji = "🤖"
                for name, e, _ in self.AGENTS:
                    if name == agent:
                        emoji = e
                        break

                # Create panel for each agent's observation
                self.console.print(Panel(
                    f"[white]{observation}[/]",
                    title=f"[bold]{emoji} Agent {i}: {agent}[/]",
                    border_style="dim cyan",
                    box=ROUNDED
                ))
                time.sleep(0.1)
        else:
            print("\n🔗 AGENT THOUGHT CHAIN")
            print("=" * 60)
            for i, obs in enumerate(observations, 1):
                agent = obs.get("agent", "Unknown")
                observation = obs.get("observation", "No observation")
                print(f"\n[Agent {i}: {agent}]")
                print(f"  {observation}")
            print("=" * 60)

    def print_executive_report(self, report: Dict[str, Any]):
        """Display the final executive report."""
        if not report:
            self.print("[red]Error: No report generated[/]")
            return

        metadata = report.get("report_metadata", {})
        summary = report.get("executive_summary", {})
        dashboard = report.get("dashboard", {})
        action_plan = report.get("action_plan", [])
        fertilizer = report.get("sections", {}).get("fertilizer_recommendations", {})

        if RICH_AVAILABLE:
            # Report Header
            self.console.print("\n")
            self.console.print(Panel(
                f"[bold white]S.O.I.L.E.R. EXECUTIVE REPORT[/]\n\n"
                f"[dim]Report ID: {metadata.get('report_id', 'N/A')}[/]\n"
                f"[dim]Generated: {metadata.get('generated_at', 'N/A')[:19]}[/]",
                box=DOUBLE,
                border_style="gold1",
                title="[bold yellow]📊 FINAL OUTPUT[/]"
            ))

            # Executive Summary Panel
            assessment = summary.get("overall_assessment", "N/A")
            score = summary.get("overall_score", 0)

            # Color based on assessment
            if "FAVORABLE" in assessment.upper():
                color = "green"
            elif "MODERATE" in assessment.upper():
                color = "yellow"
            else:
                color = "red"

            self.console.print(Panel(
                f"[bold {color}]{assessment}[/] (Score: {score:.1f}/100)\n\n"
                f"[white]{summary.get('bottom_line', 'Analysis complete.')}[/]",
                title="[bold]📋 Executive Summary[/]",
                border_style=color
            ))

            # Key Metrics Table
            metrics_table = Table(title="📈 Key Metrics Dashboard", box=ROUNDED, border_style="blue")
            metrics_table.add_column("Metric", style="cyan")
            metrics_table.add_column("Value", style="green", justify="right")
            metrics_table.add_column("Status", justify="center")

            soil_health = dashboard.get("soil_health", {})
            metrics_table.add_row(
                "🏥 Soil Health",
                f"{soil_health.get('score', 0)}/100",
                self._status_badge(soil_health.get('status', 'N/A'))
            )

            yield_target = dashboard.get("yield_target", {})
            metrics_table.add_row(
                "🌾 Target Yield",
                f"{yield_target.get('value', 0):,.0f} kg/rai",
                "📊"
            )

            investment = dashboard.get("investment", {})
            metrics_table.add_row(
                "💰 Total Investment",
                f"{investment.get('total_cost', 0):,.0f} THB",
                "💵"
            )

            returns = dashboard.get("returns", {})
            roi = returns.get('roi_percent', 0)
            roi_color = "green" if roi > 50 else ("yellow" if roi > 0 else "red")
            metrics_table.add_row(
                "📈 Expected ROI",
                f"{roi:.1f}%",
                f"[{roi_color}]{'▲' if roi > 0 else '▼'}[/]"
            )

            metrics_table.add_row(
                "💵 Expected Profit",
                f"{returns.get('expected_profit', 0):,.0f} THB",
                "✨"
            )

            metrics_table.add_row(
                "⚠️ Risk Level",
                dashboard.get('risk_level', 'N/A').upper(),
                self._risk_badge(dashboard.get('risk_level', 'N/A'))
            )

            self.console.print(metrics_table)

            # Fertilizer Schedule Table
            schedule = fertilizer.get("schedule", [])
            if schedule:
                fert_table = Table(title="🧬 Fertilizer Application Schedule", box=ROUNDED, border_style="green")
                fert_table.add_column("#", style="dim", width=3)
                fert_table.add_column("Product", style="cyan")
                fert_table.add_column("Formula", style="magenta")
                fert_table.add_column("Rate", justify="right")
                fert_table.add_column("Timing", style="yellow")
                fert_table.add_column("Stage", style="dim")

                for i, app in enumerate(schedule, 1):
                    fert_table.add_row(
                        str(i),
                        app.get("product", "N/A"),
                        app.get("formula", "N/A"),
                        f"{app.get('rate_kg_per_rai', 0):.1f} kg/rai",
                        app.get("timing", "N/A")[:30],
                        app.get("stage", "N/A")
                    )

                fert_table.add_row(
                    "", "[bold]TOTAL COST[/]", "", "",
                    f"[bold green]{fertilizer.get('total_cost_thb', 0):,.0f} THB[/]", ""
                )

                self.console.print(fert_table)

            # Action Plan Table
            if action_plan:
                action_table = Table(title="📝 Priority Action Plan", box=ROUNDED, border_style="yellow")
                action_table.add_column("Priority", style="bold", width=8, justify="center")
                action_table.add_column("Urgency", width=10, justify="center")
                action_table.add_column("Action", style="white")
                action_table.add_column("Category", style="dim")

                for action in action_plan[:8]:  # Top 8 actions
                    urgency = action.get("urgency", "MEDIUM")
                    urgency_style = "red" if urgency == "CRITICAL" else ("yellow" if urgency == "HIGH" else "green")

                    action_table.add_row(
                        f"#{action.get('priority', '-')}",
                        f"[{urgency_style}]{urgency}[/]",
                        action.get("action", "N/A")[:50],
                        action.get("category", "N/A")
                    )

                self.console.print(action_table)

            # Final Status
            self.console.print(Panel(
                "[bold green]✅ ANALYSIS COMPLETE[/]\n\n"
                f"[dim]Session: {report.get('orchestrator_metadata', {}).get('session_id', 'N/A')}[/]\n"
                f"[dim]Agents Executed: {report.get('orchestrator_metadata', {}).get('agents_executed', 0)}[/]\n"
                f"[dim]Observations: {report.get('orchestrator_metadata', {}).get('observations_collected', 0)}[/]",
                box=DOUBLE,
                border_style="green"
            ))

        else:
            # Fallback plain text output
            print("\n" + "=" * 70)
            print("📊 S.O.I.L.E.R. EXECUTIVE REPORT")
            print("=" * 70)
            print(f"Report ID: {metadata.get('report_id', 'N/A')}")
            print(f"Generated: {metadata.get('generated_at', 'N/A')[:19]}")

            print("\n📋 EXECUTIVE SUMMARY")
            print("-" * 40)
            print(f"Assessment: {summary.get('overall_assessment', 'N/A')} ({summary.get('overall_score', 0):.1f}/100)")
            print(f"Bottom Line: {summary.get('bottom_line', 'N/A')}")

            print("\n📈 KEY METRICS")
            print("-" * 40)
            print(f"  Soil Health: {dashboard.get('soil_health', {}).get('score', 0)}/100")
            print(f"  Target Yield: {dashboard.get('yield_target', {}).get('value', 0):,.0f} kg/rai")
            print(f"  Total Investment: {dashboard.get('investment', {}).get('total_cost', 0):,.0f} THB")
            print(f"  Expected ROI: {dashboard.get('returns', {}).get('roi_percent', 0):.1f}%")
            print(f"  Expected Profit: {dashboard.get('returns', {}).get('expected_profit', 0):,.0f} THB")

            print("\n🧬 FERTILIZER SCHEDULE")
            print("-" * 40)
            for i, app in enumerate(fertilizer.get("schedule", []), 1):
                print(f"  {i}. {app.get('product', 'N/A')} ({app.get('formula', 'N/A')}) - {app.get('rate_kg_per_rai', 0)} kg/rai")

            print(f"\n  Total Cost: {fertilizer.get('total_cost_thb', 0):,.0f} THB")

            print("\n" + "=" * 70)
            print("✅ ANALYSIS COMPLETE")
            print("=" * 70)

    def _status_badge(self, status: str) -> str:
        """Return a colored status badge."""
        status_lower = status.lower()
        if status_lower in ["excellent", "good"]:
            return f"[green]✓ {status}[/]"
        elif status_lower in ["fair", "moderate"]:
            return f"[yellow]○ {status}[/]"
        else:
            return f"[red]✗ {status}[/]"

    def _risk_badge(self, risk: str) -> str:
        """Return a colored risk badge."""
        risk_lower = risk.lower()
        if risk_lower == "low":
            return "[green]🟢[/]"
        elif risk_lower == "medium":
            return "[yellow]🟡[/]"
        else:
            return "[red]🔴[/]"


def main():
    """Main entry point for S.O.I.L.E.R. demonstration."""

    # Initialize console
    console = SoilerConsole()

    # Clear and show banner
    console.clear()
    console.print_banner()

    time.sleep(0.5)

    # Boot sequence
    console.print_boot_sequence()

    # =========================================================================
    # SCENARIO: Mr. Somchai's Corn Field
    # =========================================================================
    scenario = {
        "farmer": "Mr. Somchai",
        "location": "Long District, Phrae Province",
        "crop": "Corn",
        "field_size_rai": 15,
        "ph": 6.2,
        "nitrogen": 20,
        "phosphorus": 12,
        "potassium": 110,
        "budget_thb": 15000,
        "texture": "sandy clay loam",
        "irrigation_available": True
    }

    # Display scenario
    console.print_scenario(scenario)

    if RICH_AVAILABLE:
        console.console.print("[bold yellow]🚀 INITIATING MULTI-AGENT ANALYSIS PIPELINE...[/]\n")
    else:
        print("🚀 INITIATING MULTI-AGENT ANALYSIS PIPELINE...\n")

    time.sleep(0.5)

    # =========================================================================
    # RUN ANALYSIS
    # =========================================================================
    try:
        # Initialize orchestrator with verbose=False to suppress internal output
        # We'll handle our own display
        orchestrator = SoilerOrchestrator(verbose=False)

        if RICH_AVAILABLE:
            with console.console.status("[bold green]Processing through 6-agent pipeline..."):
                # Run analysis
                report = orchestrator.analyze(
                    location=scenario["location"],
                    crop=scenario["crop"],
                    ph=scenario["ph"],
                    nitrogen=scenario["nitrogen"],
                    phosphorus=scenario["phosphorus"],
                    potassium=scenario["potassium"],
                    field_size_rai=scenario["field_size_rai"],
                    texture=scenario["texture"],
                    budget_thb=scenario["budget_thb"],
                    irrigation_available=scenario["irrigation_available"]
                )
        else:
            print("Processing through 6-agent pipeline...")
            report = orchestrator.analyze(
                location=scenario["location"],
                crop=scenario["crop"],
                ph=scenario["ph"],
                nitrogen=scenario["nitrogen"],
                phosphorus=scenario["phosphorus"],
                potassium=scenario["potassium"],
                field_size_rai=scenario["field_size_rai"],
                texture=scenario["texture"],
                budget_thb=scenario["budget_thb"],
                irrigation_available=scenario["irrigation_available"]
            )

        # Get observations from orchestrator
        observations = orchestrator.get_observations()

        # Display thought chain
        console.print_thought_chain(observations)

        # Display final report
        console.print_executive_report(report)

        # Success message
        if RICH_AVAILABLE:
            console.console.print("\n[bold green]🌱 S.O.I.L.E.R. Analysis Complete![/]")
            console.console.print(f"[dim]Full report object returned with {len(str(report))} characters of data.[/]\n")
        else:
            print("\n🌱 S.O.I.L.E.R. Analysis Complete!")
            print(f"Full report object returned with {len(str(report))} characters of data.\n")

        return report

    except Exception as e:
        if RICH_AVAILABLE:
            console.console.print(f"\n[bold red]❌ ERROR: {str(e)}[/]")
            console.console.print_exception()
        else:
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
        return None


def run_interactive():
    """Run interactive mode allowing custom scenarios."""
    console = SoilerConsole()
    console.print_banner()

    if RICH_AVAILABLE:
        console.console.print("\n[bold cyan]🔧 INTERACTIVE MODE[/]\n")
        console.console.print("Enter soil analysis parameters:\n")

        # Get inputs
        location = console.console.input("[cyan]Location[/] (default: Phrae Province): ") or "Phrae Province"
        crop = console.console.input("[cyan]Crop[/] (Riceberry Rice/Corn): ") or "Riceberry Rice"
        field_size = float(console.console.input("[cyan]Field Size (rai)[/]: ") or "5")
        ph = float(console.console.input("[cyan]pH[/]: ") or "6.0")
        nitrogen = float(console.console.input("[cyan]Nitrogen (mg/kg)[/]: ") or "30")
        phosphorus = float(console.console.input("[cyan]Phosphorus (mg/kg)[/]: ") or "20")
        potassium = float(console.console.input("[cyan]Potassium (mg/kg)[/]: ") or "100")
        budget = float(console.console.input("[cyan]Budget (THB)[/]: ") or "5000")

    else:
        print("\n🔧 INTERACTIVE MODE\n")
        print("Enter soil analysis parameters:\n")

        location = input("Location (default: Phrae Province): ") or "Phrae Province"
        crop = input("Crop (Riceberry Rice/Corn): ") or "Riceberry Rice"
        field_size = float(input("Field Size (rai): ") or "5")
        ph = float(input("pH: ") or "6.0")
        nitrogen = float(input("Nitrogen (mg/kg): ") or "30")
        phosphorus = float(input("Phosphorus (mg/kg): ") or "20")
        potassium = float(input("Potassium (mg/kg): ") or "100")
        budget = float(input("Budget (THB): ") or "5000")

    # Run analysis
    orchestrator = SoilerOrchestrator(verbose=True)
    report = orchestrator.analyze(
        location=location,
        crop=crop,
        ph=ph,
        nitrogen=nitrogen,
        phosphorus=phosphorus,
        potassium=potassium,
        field_size_rai=field_size,
        budget_thb=budget
    )

    console.print_executive_report(report)
    return report


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="S.O.I.L.E.R. - Multi-Agent AI System for Precision Agriculture"
    )
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Run in interactive mode with custom inputs"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress verbose output"
    )

    args = parser.parse_args()

    if args.interactive:
        run_interactive()
    else:
        main()
