#!/usr/bin/env python3
"""
Whoop Visualization Generator - Minimal Bar Chart Style
Creates clean horizontal bar charts with emojis for Whoop data
"""

import json
import os
from datetime import datetime
from typing import List, Tuple


class BarChartSVG:
    """Generate minimal bar chart SVG graphs for Whoop data"""

    def __init__(self, width=800, height=300):
        self.width = width
        self.height = height
        self.padding = 20
        self.line_height = 35

    def create_bar(self, value, max_value, bar_width=400):
        """Create a Unicode block bar"""
        if max_value == 0:
            return "░" * 20

        # Number of blocks (out of 20)
        filled_blocks = int((value / max_value) * 20)
        partial = (value / max_value) * 20 - filled_blocks

        # Unicode block characters: full, 7/8, 3/4, 5/8, 1/2, 3/8, 1/4, 1/8, empty
        blocks = {
            0: '░',
            1: '▏',
            2: '▎',
            3: '▍',
            4: '▌',
            5: '▋',
            6: '▊',
            7: '▉',
            8: '█'
        }

        bar = '█' * filled_blocks

        # Add partial block
        if filled_blocks < 20 and partial > 0:
            partial_index = int(partial * 8)
            bar += blocks.get(partial_index, '░')
            bar += '░' * (19 - filled_blocks)
        else:
            bar += '░' * (20 - filled_blocks)

        return bar

    def generate_chart(self, title: str, data: List[Tuple[str, float]], unit: str, color: str, max_scale: float = None) -> str:
        """Generate horizontal bar chart SVG"""
        # Calculate height based on number of items
        num_items = min(len(data), 7)  # Show last 7 days
        chart_height = self.padding * 2 + 30 + (num_items * self.line_height) + 40

        svg = f'''<svg width="{self.width}" height="{chart_height}" xmlns="http://www.w3.org/2000/svg">
    <!-- Background -->
    <rect width="{self.width}" height="{chart_height}" fill="#0d1117" rx="6"/>

    <!-- Title -->
    <text x="{self.padding}" y="{self.padding + 20}" font-family="'SF Mono', 'Courier New', monospace"
          font-size="18" font-weight="bold" fill="#c9d1d9">
        {title}
    </text>

'''

        if not data:
            svg += '</svg>'
            return svg

        # Show last 7 items
        display_data = data[-7:]
        # Use provided max_scale for consistent scaling, or calculate from data
        max_value = max_scale if max_scale else max(item[1] for item in display_data) if display_data else 1

        y_offset = self.padding + 50

        for label, value in display_data:
            bar = self.create_bar(value, max_value)

            # Format value based on unit
            if unit == "hrs":
                value_str = f"{value:.1f}{unit}"
            elif unit == "%":
                value_str = f"{value:.0f}{unit}"
            else:
                value_str = f"{value:.1f}"

            svg += f'''    <!-- Data row -->
    <text x="{self.padding + 10}" y="{y_offset}" font-family="'SF Mono', 'Courier New', monospace"
          font-size="14" fill="#8b949e">
        {label}
    </text>
    <text x="{self.padding + 100}" y="{y_offset}" font-family="'SF Mono', 'Courier New', monospace"
          font-size="14" fill="{color}" font-weight="bold" text-anchor="end">
        {value_str}
    </text>
    <text x="{self.padding + 110}" y="{y_offset}" font-family="'SF Mono', 'Courier New', monospace"
          font-size="16" fill="{color}" letter-spacing="2">
        {bar}
    </text>

'''
            y_offset += self.line_height

        # Add stats at bottom
        avg_value = sum(item[1] for item in display_data) / len(display_data)
        if unit == "hrs":
            avg_str = f"Avg: {avg_value:.1f}{unit}"
        elif unit == "%":
            avg_str = f"Avg: {avg_value:.0f}{unit}"
        else:
            avg_str = f"Avg: {avg_value:.1f}"

        svg += f'''    <!-- Stats -->
    <text x="{self.width - self.padding - 10}" y="{chart_height - self.padding - 10}"
          font-family="'SF Mono', 'Courier New', monospace" font-size="12" fill="#58a6ff" text-anchor="end">
        {avg_str} • Last {len(display_data)} days
    </text>

</svg>'''

        return svg


def load_json_data(filename):
    """Load data from JSON file"""
    filepath = os.path.join('data', filename)
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: {filename} not found")
        return None


def format_date(date_str):
    """Format ISO date to short format (MM/DD)"""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%m/%d')
    except:
        return date_str[:5]


def extract_sleep_data(sleep_data):
    """Extract sleep duration and performance with dates"""
    if not sleep_data or 'records' not in sleep_data:
        return [], []

    records = sorted(sleep_data['records'], key=lambda x: x.get('created_at', ''))

    duration_data = []
    performance_data = []

    for record in records:
        score = record.get('score', {})
        date_str = format_date(record.get('created_at', ''))

        # Sleep duration in hours
        duration_ms = score.get('stage_summary', {}).get('total_in_bed_time_milli', 0)
        duration_hrs = duration_ms / (1000 * 60 * 60)
        duration_data.append((date_str, duration_hrs))

        # Sleep performance percentage
        performance = score.get('sleep_performance_percentage', 0)
        performance_data.append((date_str, performance))

    return duration_data, performance_data


def extract_recovery_data(recovery_data):
    """Extract recovery scores with dates"""
    if not recovery_data or 'records' not in recovery_data:
        return []

    records = sorted(recovery_data['records'], key=lambda x: x.get('created_at', ''))

    data = []
    for record in records:
        score = record.get('score', {})
        date_str = format_date(record.get('created_at', ''))
        recovery_score = score.get('recovery_score', 0)
        data.append((date_str, recovery_score))

    return data


def extract_strain_data(cycles_data):
    """Extract strain scores with dates"""
    if not cycles_data or 'records' not in cycles_data:
        return []

    records = sorted(cycles_data['records'], key=lambda x: x.get('created_at', ''))

    data = []
    for record in records:
        score = record.get('score', {})
        date_str = format_date(record.get('created_at', ''))
        strain = score.get('strain', 0)
        data.append((date_str, strain))

    return data


def main():
    """Generate all visualizations"""
    print("=" * 60)
    print("Whoop Bar Chart Visualization Generator")
    print("=" * 60)
    print()

    # Load data
    sleep_data = load_json_data('sleep.json')
    recovery_data = load_json_data('recovery.json')
    cycles_data = load_json_data('cycles.json')

    # Extract metrics
    sleep_duration_data, sleep_performance_data = extract_sleep_data(sleep_data)
    recovery_data_list = extract_recovery_data(recovery_data)
    strain_data_list = extract_strain_data(cycles_data)

    # Create chart generator
    chart = BarChartSVG()

    # Sleep duration chart
    if sleep_duration_data:
        print("Generating sleep duration chart...")
        svg = chart.generate_chart(
            "Sleep Duration",
            sleep_duration_data,
            "hrs",
            "#9d4edd"
        )
        with open('sleep_duration.svg', 'w') as f:
            f.write(svg)
        avg = sum(x[1] for x in sleep_duration_data[-7:]) / min(len(sleep_duration_data), 7)
        print(f"  ✓ sleep_duration.svg (avg: {avg:.1f}hrs)")

    # Recovery score chart
    if recovery_data_list:
        print("Generating recovery score chart...")
        svg = chart.generate_chart(
            "Recovery Score",
            recovery_data_list,
            "",
            "#06d6a0"
        )
        with open('recovery_score.svg', 'w') as f:
            f.write(svg)
        avg = sum(x[1] for x in recovery_data_list[-7:]) / min(len(recovery_data_list), 7)
        print(f"  ✓ recovery_score.svg (avg: {avg:.0f})")

    # Strain score chart
    if strain_data_list:
        print("Generating strain score chart...")
        svg = chart.generate_chart(
            "Strain Score",
            strain_data_list,
            "",
            "#ff6b6b"
        )
        with open('strain_score.svg', 'w') as f:
            f.write(svg)
        avg = sum(x[1] for x in strain_data_list[-7:]) / min(len(strain_data_list), 7)
        print(f"  ✓ strain_score.svg (avg: {avg:.1f})")

    # Sleep performance chart
    if sleep_performance_data:
        print("Generating sleep performance chart...")
        svg = chart.generate_chart(
            "Sleep Performance",
            sleep_performance_data,
            "%",
            "#4cc9f0"
        )
        with open('sleep_performance.svg', 'w') as f:
            f.write(svg)
        avg = sum(x[1] for x in sleep_performance_data[-7:]) / min(len(sleep_performance_data), 7)
        print(f"  ✓ sleep_performance.svg (avg: {avg:.0f}%)")

    print("\n" + "=" * 60)
    print("Bar chart visualization generation complete!")
    print("=" * 60)

    # Generate compact versions for profile README (side by side)
    print("\nGenerating compact versions for profile...")
    compact_chart = BarChartSVG(width=280, height=250)

    # Compact recovery score (scale 0-100)
    if recovery_data_list:
        svg = compact_chart.generate_chart(
            "Recovery",
            recovery_data_list[-5:],  # Last 5 days only
            "",
            "#06d6a0",
            max_scale=100  # Recovery is 0-100
        )
        with open('recovery_compact.svg', 'w') as f:
            f.write(svg)
        print("  ✓ recovery_compact.svg")

    # Compact strain score (scale 0-21)
    if strain_data_list:
        svg = compact_chart.generate_chart(
            "Strain",
            strain_data_list[-5:],
            "",
            "#ff6b6b",
            max_scale=21  # Strain is 0-21
        )
        with open('strain_compact.svg', 'w') as f:
            f.write(svg)
        print("  ✓ strain_compact.svg")

    # Compact sleep performance (scale 0-100%)
    if sleep_performance_data:
        svg = compact_chart.generate_chart(
            "Sleep Quality",
            sleep_performance_data[-5:],
            "%",
            "#4cc9f0",
            max_scale=100  # Performance is 0-100%
        )
        with open('sleep_performance_compact.svg', 'w') as f:
            f.write(svg)
        print("  ✓ sleep_performance_compact.svg")

    print("\n" + "=" * 60)
    print("All visualizations complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
