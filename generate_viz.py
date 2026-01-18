#!/usr/bin/env python3
"""
Whoop Visualization Generator
Creates SVG graphs for sleep, recovery, and strain data
"""

import json
import os
from datetime import datetime
from typing import List, Tuple


class SVGGraph:
    """Generate SVG graphs for Whoop data"""

    def __init__(self, width=800, height=200, padding=40):
        self.width = width
        self.height = height
        self.padding = padding
        self.graph_width = width - (2 * padding)
        self.graph_height = height - (2 * padding)

    def create_svg_header(self, title):
        """Create SVG header with styling"""
        return f'''<svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="gradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#00D9FF;stop-opacity:0.3" />
            <stop offset="100%" style="stop-color:#00D9FF;stop-opacity:0.05" />
        </linearGradient>
    </defs>

    <!-- Background -->
    <rect width="{self.width}" height="{self.height}" fill="#0D1117" rx="6"/>

    <!-- Title -->
    <text x="{self.padding}" y="{self.padding - 15}" font-family="'SF Mono', 'Monaco', monospace" font-size="16" font-weight="bold" fill="#C9D1D9">
        {title}
    </text>
'''

    def create_line_path(self, data_points: List[Tuple[float, float]], color="#00D9FF"):
        """Create a line path from data points"""
        if not data_points:
            return ""

        # Create path
        path = f'M {data_points[0][0]},{data_points[0][1]}'
        for x, y in data_points[1:]:
            path += f' L {x},{y}'

        return f'''
    <!-- Line -->
    <path d="{path}" stroke="{color}" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>

    <!-- Area under line -->
    <path d="{path} L {data_points[-1][0]},{self.height - self.padding} L {data_points[0][0]},{self.height - self.padding} Z"
          fill="url(#gradient)" opacity="0.3"/>
'''

    def create_grid(self, y_max):
        """Create grid lines and labels"""
        grid = ''
        num_lines = 4

        for i in range(num_lines + 1):
            y = self.padding + (self.graph_height * i / num_lines)
            value = y_max * (1 - i / num_lines)

            # Horizontal grid line
            grid += f'''
    <line x1="{self.padding}" y1="{y}" x2="{self.width - self.padding}" y2="{y}"
          stroke="#30363D" stroke-width="1" stroke-dasharray="4,4"/>
    <text x="{self.padding - 5}" y="{y + 4}" font-family="'SF Mono', 'Monaco', monospace"
          font-size="10" fill="#8B949E" text-anchor="end">{value:.0f}</text>
'''

        return grid

    def normalize_data(self, values: List[float]) -> List[Tuple[float, float]]:
        """Normalize data points to graph coordinates"""
        if not values:
            return []

        max_val = max(values) if max(values) > 0 else 1
        min_val = min(values)

        points = []
        for i, value in enumerate(values):
            x = self.padding + (i * self.graph_width / max(len(values) - 1, 1))
            # Normalize to 0-1 range, then scale to graph height
            normalized = (value - min_val) / (max_val - min_val) if max_val != min_val else 0.5
            y = self.height - self.padding - (normalized * self.graph_height)
            points.append((x, y))

        return points

    def generate_graph(self, title: str, values: List[float], color="#00D9FF") -> str:
        """Generate complete SVG graph"""
        svg = self.create_svg_header(title)

        if values:
            y_max = max(values) if values else 100
            svg += self.create_grid(y_max)
            points = self.normalize_data(values)
            svg += self.create_line_path(points, color)

            # Add data points
            for x, y in points:
                svg += f'''
    <circle cx="{x}" cy="{y}" r="3" fill="{color}" opacity="0.8"/>'''

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


def extract_sleep_data(sleep_data):
    """Extract sleep duration and performance from sleep data"""
    if not sleep_data or 'records' not in sleep_data:
        return [], []

    records = sorted(sleep_data['records'], key=lambda x: x.get('created_at', ''))

    durations = []  # in hours
    performances = []  # percentage

    for record in records:
        score = record.get('score', {})

        # Sleep duration in milliseconds, convert to hours
        duration_ms = score.get('stage_summary', {}).get('total_in_bed_time_milli', 0)
        durations.append(duration_ms / (1000 * 60 * 60))

        # Sleep performance percentage
        performance = score.get('sleep_performance_percentage', 0)
        performances.append(performance)

    return durations, performances


def extract_recovery_data(recovery_data):
    """Extract recovery scores"""
    if not recovery_data or 'records' not in recovery_data:
        return []

    records = sorted(recovery_data['records'], key=lambda x: x.get('created_at', ''))

    scores = []
    for record in records:
        score = record.get('score', {})
        recovery_score = score.get('recovery_score', 0)
        scores.append(recovery_score)

    return scores


def extract_strain_data(cycles_data):
    """Extract strain scores from cycles"""
    if not cycles_data or 'records' not in cycles_data:
        return []

    records = sorted(cycles_data['records'], key=lambda x: x.get('created_at', ''))

    scores = []
    for record in records:
        score = record.get('score', {})
        strain = score.get('strain', 0)
        scores.append(strain)

    return scores


def main():
    """Generate all visualizations"""
    print("=" * 60)
    print("Whoop Visualization Generator")
    print("=" * 60)
    print()

    # Load data
    sleep_data = load_json_data('sleep.json')
    recovery_data = load_json_data('recovery.json')
    cycles_data = load_json_data('cycles.json')

    # Extract metrics
    sleep_durations, sleep_performances = extract_sleep_data(sleep_data)
    recovery_scores = extract_recovery_data(recovery_data)
    strain_scores = extract_strain_data(cycles_data)

    # Generate graphs
    graph = SVGGraph(width=800, height=200)

    # Sleep duration graph
    if sleep_durations:
        print("Generating sleep duration graph...")
        sleep_svg = graph.generate_graph("Sleep Duration (hours)", sleep_durations, "#9D4EDD")
        with open('sleep_duration.svg', 'w') as f:
            f.write(sleep_svg)
        print(f"  ✓ sleep_duration.svg (avg: {sum(sleep_durations)/len(sleep_durations):.1f}h)")

    # Recovery score graph
    if recovery_scores:
        print("Generating recovery score graph...")
        recovery_svg = graph.generate_graph("Recovery Score", recovery_scores, "#06D6A0")
        with open('recovery_score.svg', 'w') as f:
            f.write(recovery_svg)
        print(f"  ✓ recovery_score.svg (avg: {sum(recovery_scores)/len(recovery_scores):.0f})")

    # Strain score graph
    if strain_scores:
        print("Generating strain score graph...")
        strain_svg = graph.generate_graph("Strain Score", strain_scores, "#FF6B6B")
        with open('strain_score.svg', 'w') as f:
            f.write(strain_svg)
        print(f"  ✓ strain_score.svg (avg: {sum(strain_scores)/len(strain_scores):.1f})")

    # Sleep performance graph
    if sleep_performances:
        print("Generating sleep performance graph...")
        perf_svg = graph.generate_graph("Sleep Performance (%)", sleep_performances, "#4CC9F0")
        with open('sleep_performance.svg', 'w') as f:
            f.write(perf_svg)
        print(f"  ✓ sleep_performance.svg (avg: {sum(sleep_performances)/len(sleep_performances):.0f}%)")

    print("\n" + "=" * 60)
    print("Visualization generation complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
