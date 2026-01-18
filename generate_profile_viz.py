#!/usr/bin/env python3
"""
Generate profile-specific visualizations using SVG rectangles instead of Unicode
This ensures proper rendering in GitHub profile READMEs
"""

import json
import os
from datetime import datetime
from typing import List, Tuple


class ProfileBarChart:
    """Generate bar charts using SVG rectangles for consistent rendering"""

    def __init__(self, width=260, height=250):
        self.width = width
        self.height = height
        self.padding = 20
        self.line_height = 35
        self.bar_width = 130  # Width of the bar area

    def generate_chart(self, title: str, data: List[Tuple[str, float]], unit: str, color: str, max_scale: float) -> str:
        """Generate horizontal bar chart SVG using rectangles"""
        num_items = min(len(data), 5)
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

        display_data = data[-5:]
        y_offset = self.padding + 50

        for label, value in display_data:
            # Calculate bar fill percentage
            fill_percent = (value / max_scale) * 100 if max_scale > 0 else 0
            filled_width = (fill_percent / 100) * self.bar_width

            # Format value
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

    <!-- Bar background -->
    <rect x="{self.padding + 110}" y="{y_offset - 12}" width="{self.bar_width}" height="16"
          fill="#1a1a1a" rx="2"/>

    <!-- Bar filled portion -->
    <rect x="{self.padding + 110}" y="{y_offset - 12}" width="{filled_width:.1f}" height="16"
          fill="{color}" rx="2"/>

'''
            y_offset += self.line_height

        # Add stats
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
        return None


def format_date(date_str):
    """Format ISO date to short format (MM/DD)"""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%m/%d')
    except:
        return date_str[:5]


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


def extract_sleep_performance(sleep_data):
    """Extract sleep performance with dates"""
    if not sleep_data or 'records' not in sleep_data:
        return []
    records = sorted(sleep_data['records'], key=lambda x: x.get('created_at', ''))
    data = []
    for record in records:
        score = record.get('score', {})
        date_str = format_date(record.get('created_at', ''))
        performance = score.get('sleep_performance_percentage', 0)
        data.append((date_str, performance))
    return data


def main():
    print("Generating profile visualizations with SVG rectangles...")

    # Load data
    recovery_data = load_json_data('recovery.json')
    cycles_data = load_json_data('cycles.json')
    sleep_data = load_json_data('sleep.json')

    # Extract data
    recovery_list = extract_recovery_data(recovery_data)
    strain_list = extract_strain_data(cycles_data)
    sleep_perf_list = extract_sleep_performance(sleep_data)

    # Create chart generator
    chart = ProfileBarChart(width=260, height=250)

    # Recovery
    if recovery_list:
        svg = chart.generate_chart("Recovery", recovery_list, "", "#06d6a0", 100)
        with open('recovery_compact.svg', 'w') as f:
            f.write(svg)
        print("  ✓ recovery_compact.svg")

    # Strain
    if strain_list:
        svg = chart.generate_chart("Strain", strain_list, "", "#ff6b6b", 21)
        with open('strain_compact.svg', 'w') as f:
            f.write(svg)
        print("  ✓ strain_compact.svg")

    # Sleep Performance
    if sleep_perf_list:
        svg = chart.generate_chart("Sleep Quality", sleep_perf_list, "%", "#4cc9f0", 100)
        with open('sleep_performance_compact.svg', 'w') as f:
            f.write(svg)
        print("  ✓ sleep_performance_compact.svg")

    print("\nProfile visualizations complete!")


if __name__ == '__main__':
    main()
