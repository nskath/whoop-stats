#!/usr/bin/env python3
"""
Whoop Visualization Generator - ASCII Art Style
Creates terminal-style SVG graphs for sleep, recovery, and strain data
"""

import json
import os
from datetime import datetime
from typing import List, Tuple


class ASCIIGraph:
    """Generate ASCII-style SVG graphs for Whoop data"""

    def __init__(self, width=800, height=250, padding=50):
        self.width = width
        self.height = height
        self.padding = padding
        self.bottom_padding = 70  # Extra space for date labels
        self.graph_width = width - (2 * padding)
        self.graph_height = height - padding - self.bottom_padding

    def create_svg_header(self, title):
        """Create SVG header with ASCII art styling"""
        return f'''<svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg">
    <!-- Background -->
    <rect width="{self.width}" height="{self.height}" fill="#0a0e14"/>

    <!-- Border -->
    <rect x="2" y="2" width="{self.width-4}" height="{self.height-4}" fill="none" stroke="#33ff00" stroke-width="2"/>

    <!-- Title -->
    <text x="{self.padding}" y="30" font-family="'Courier New', 'Courier', monospace" font-size="18" font-weight="bold" fill="#33ff00">
        ┌─ {title.upper()} ─┐
    </text>
'''

    def create_ascii_line(self, data_points: List[Tuple[float, float]], dates: List[str], color="#33ff00"):
        """Create ASCII-style line chart"""
        if not data_points:
            return ""

        svg = ''

        # Draw connecting lines between points
        for i in range(len(data_points) - 1):
            x1, y1 = data_points[i]
            x2, y2 = data_points[i + 1]
            svg += f'''
    <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="3" stroke-linecap="round"/>'''

        # Draw data points as squares (ASCII block style)
        for i, (x, y) in enumerate(data_points):
            svg += f'''
    <rect x="{x-4}" y="{y-4}" width="8" height="8" fill="{color}" stroke="#0a0e14" stroke-width="1"/>'''

        # Add date labels
        for i, (x, _) in enumerate(data_points):
            if i % max(1, len(data_points) // 6) == 0 or i == len(data_points) - 1:  # Show ~6 labels
                date_str = dates[i]
                svg += f'''
    <text x="{x}" y="{self.height - self.bottom_padding + 25}" font-family="'Courier New', 'Courier', monospace"
          font-size="10" fill="#33ff00" text-anchor="middle" transform="rotate(-45, {x}, {self.height - self.bottom_padding + 25})">
        {date_str}
    </text>'''

        return svg

    def create_ascii_grid(self, y_max, y_min):
        """Create ASCII-style grid"""
        grid = ''
        num_lines = 5

        for i in range(num_lines):
            y = self.padding + (self.graph_height * i / (num_lines - 1))
            value = y_max - (y_max - y_min) * (i / (num_lines - 1))

            # Horizontal grid line (dashed ASCII style)
            grid += f'''
    <line x1="{self.padding}" y1="{y}" x2="{self.width - self.padding}" y2="{y}"
          stroke="#1a5f1a" stroke-width="1" stroke-dasharray="5,5" opacity="0.5"/>'''

            # Y-axis label
            grid += f'''
    <text x="{self.padding - 10}" y="{y + 4}" font-family="'Courier New', 'Courier', monospace"
          font-size="12" fill="#33ff00" text-anchor="end">{value:.1f}</text>'''

        # Draw axis lines
        grid += f'''
    <!-- Y-axis -->
    <line x1="{self.padding}" y1="{self.padding}" x2="{self.padding}" y2="{self.height - self.bottom_padding}"
          stroke="#33ff00" stroke-width="2"/>
    <!-- X-axis -->
    <line x1="{self.padding}" y1="{self.height - self.bottom_padding}" x2="{self.width - self.padding}" y2="{self.height - self.bottom_padding}"
          stroke="#33ff00" stroke-width="2"/>'''

        return grid

    def normalize_data(self, values: List[float]) -> List[Tuple[float, float]]:
        """Normalize data points to graph coordinates"""
        if not values:
            return []

        max_val = max(values)
        min_val = min(values)
        val_range = max_val - min_val if max_val != min_val else 1

        points = []
        for i, value in enumerate(values):
            x = self.padding + (i * self.graph_width / max(len(values) - 1, 1))
            # Normalize to 0-1 range, then scale to graph height
            normalized = (value - min_val) / val_range if val_range > 0 else 0.5
            y = self.height - self.bottom_padding - (normalized * self.graph_height)
            points.append((x, y))

        return points

    def generate_graph(self, title: str, values: List[float], dates: List[str], color="#33ff00") -> str:
        """Generate complete ASCII-style SVG graph"""
        svg = self.create_svg_header(title)

        if values and dates:
            y_max = max(values)
            y_min = min(values)
            svg += self.create_ascii_grid(y_max, y_min)
            points = self.normalize_data(values)
            svg += self.create_ascii_line(points, dates, color)

            # Add stats in corner
            avg = sum(values) / len(values)
            svg += f'''
    <text x="{self.width - self.padding}" y="30" font-family="'Courier New', 'Courier', monospace"
          font-size="12" fill="#33ff00" text-anchor="end">
        AVG: {avg:.1f} │ MAX: {y_max:.1f} │ MIN: {y_min:.1f}
    </text>'''

        svg += '\n</svg>'
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
    """Extract sleep duration, performance, and dates from sleep data"""
    if not sleep_data or 'records' not in sleep_data:
        return [], [], []

    records = sorted(sleep_data['records'], key=lambda x: x.get('created_at', ''))

    durations = []
    performances = []
    dates = []

    for record in records:
        score = record.get('score', {})

        # Sleep duration in milliseconds, convert to hours
        duration_ms = score.get('stage_summary', {}).get('total_in_bed_time_milli', 0)
        durations.append(duration_ms / (1000 * 60 * 60))

        # Sleep performance percentage
        performance = score.get('sleep_performance_percentage', 0)
        performances.append(performance)

        # Date
        date_str = record.get('created_at', '')
        dates.append(format_date(date_str))

    return durations, performances, dates


def extract_recovery_data(recovery_data):
    """Extract recovery scores and dates"""
    if not recovery_data or 'records' not in recovery_data:
        return [], []

    records = sorted(recovery_data['records'], key=lambda x: x.get('created_at', ''))

    scores = []
    dates = []

    for record in records:
        score = record.get('score', {})
        recovery_score = score.get('recovery_score', 0)
        scores.append(recovery_score)

        date_str = record.get('created_at', '')
        dates.append(format_date(date_str))

    return scores, dates


def extract_strain_data(cycles_data):
    """Extract strain scores and dates from cycles"""
    if not cycles_data or 'records' not in cycles_data:
        return [], []

    records = sorted(cycles_data['records'], key=lambda x: x.get('created_at', ''))

    scores = []
    dates = []

    for record in records:
        score = record.get('score', {})
        strain = score.get('strain', 0)
        scores.append(strain)

        date_str = record.get('created_at', '')
        dates.append(format_date(date_str))

    return scores, dates


def main():
    """Generate all visualizations"""
    print("=" * 60)
    print("Whoop ASCII Art Visualization Generator")
    print("=" * 60)
    print()

    # Load data
    sleep_data = load_json_data('sleep.json')
    recovery_data = load_json_data('recovery.json')
    cycles_data = load_json_data('cycles.json')

    # Extract metrics with dates
    sleep_durations, sleep_performances, sleep_dates = extract_sleep_data(sleep_data)
    recovery_scores, recovery_dates = extract_recovery_data(recovery_data)
    strain_scores, strain_dates = extract_strain_data(cycles_data)

    # Generate graphs with ASCII art style
    graph = ASCIIGraph(width=800, height=250)

    # Sleep duration graph (green terminal style)
    if sleep_durations:
        print("Generating sleep duration graph...")
        sleep_svg = graph.generate_graph("Sleep Duration (hours)", sleep_durations, sleep_dates, "#33ff00")
        with open('sleep_duration.svg', 'w') as f:
            f.write(sleep_svg)
        print(f"  ✓ sleep_duration.svg (avg: {sum(sleep_durations)/len(sleep_durations):.1f}h)")

    # Recovery score graph (cyan terminal style)
    if recovery_scores:
        print("Generating recovery score graph...")
        recovery_svg = graph.generate_graph("Recovery Score", recovery_scores, recovery_dates, "#00ffff")
        with open('recovery_score.svg', 'w') as f:
            f.write(recovery_svg)
        print(f"  ✓ recovery_score.svg (avg: {sum(recovery_scores)/len(recovery_scores):.0f})")

    # Strain score graph (yellow terminal style)
    if strain_scores:
        print("Generating strain score graph...")
        strain_svg = graph.generate_graph("Strain Score", strain_scores, strain_dates, "#ffff00")
        with open('strain_score.svg', 'w') as f:
            f.write(strain_svg)
        print(f"  ✓ strain_score.svg (avg: {sum(strain_scores)/len(strain_scores):.1f})")

    # Sleep performance graph (magenta terminal style)
    if sleep_performances:
        print("Generating sleep performance graph...")
        perf_svg = graph.generate_graph("Sleep Performance (%)", sleep_performances, sleep_dates, "#ff00ff")
        with open('sleep_performance.svg', 'w') as f:
            f.write(perf_svg)
        print(f"  ✓ sleep_performance.svg (avg: {sum(sleep_performances)/len(sleep_performances):.0f}%)")

    print("\n" + "=" * 60)
    print("ASCII art visualization generation complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
