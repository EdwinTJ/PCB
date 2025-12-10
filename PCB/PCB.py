"""
PCB.py

Zoomed component view (crops to component area)
"""

import pandas as pd
import matplotlib.pyplot as plt
from GerberParse import GerberParser


def load_pcb_data(csv_file, gko_file):
    """Load both CSV (component placement) and GKO (board outline) data."""
    try:
        # Parse GKO file for board dimensions
        gerber_parser = GerberParser(gko_file, verbose=False)
        if not gerber_parser.parse():
            print(f"Warning: Could not parse {gko_file}")
            board_dims = None
        else:
            board_dims = gerber_parser.get_dimensions()
            print(f"✓ Loaded board dimensions from {gko_file}")
        
        # Parse CSV file for component data
        df = pd.read_csv(csv_file, skiprows=12, encoding='latin-1')
        df.columns = df.columns.str.strip().str.replace('"', '')
        
        # Clean coordinate columns
        df['Center-X(mm)'] = df['Center-X(mm)'].astype(str).str.replace('mm', '').astype(float)
        df['Center-Y(mm)'] = df['Center-Y(mm)'].astype(str).str.replace('mm', '').astype(float)
        
        print(f"✓ Loaded component data from {csv_file} ({len(df)} components)")
        
        return df, board_dims
        
    except Exception as e:
        print(f"Error loading data: {e}")
        return None, None


def get_component_bounds(df, margin_mm=5.0):
    """Get bounding box of components with margin for zoomed view."""
    x_vals = df['Center-X(mm)'].astype(float)
    y_vals = df['Center-Y(mm)'].astype(float)
    
    min_x = x_vals.min() - margin_mm
    max_x = x_vals.max() + margin_mm
    min_y = y_vals.min() - margin_mm
    max_y = y_vals.max() + margin_mm
    
    width = max_x - min_x
    height = max_y - min_y
    
    return min_x, max_x, min_y, max_y, width, height

def create_zoomed_layout(df, output_file='pcb_zoomed.pdf', component_margin=5.0):
    """
    Option 2: Zoomed component view (RECOMMENDED for readability).
    Crops to just the component area with margin, making everything larger and clearer.
    """
    if df is None:
        print("Error: Invalid data")
        return False
    
    try:
        min_x, max_x, min_y, max_y, width, height = get_component_bounds(df, component_margin)
        
        # Calculate figure size to maintain good aspect ratio
        fig_width = 12
        fig_height = fig_width * (height / width) if width > 0 else 12
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        
        # Plot components
        ax.scatter(df['Center-X(mm)'], df['Center-Y(mm)'], 
                  color='red', s=100, marker='o', label='Components', zorder=3, edgecolors='darkred', linewidth=1)
        
        # Add designator labels (larger font since we're zoomed)
        for idx, row in df.iterrows():
            ax.text(row['Center-X(mm)'] + 1.2, row['Center-Y(mm)'], 
                   row['Designator'], fontsize=8, ha='left', va='center', zorder=4, fontweight='bold')
        
        # Add a subtle background grid for reference
        ax.grid(True, linestyle=':', alpha=0.3, linewidth=0.5)
        
        # Set axis limits to component bounds
        ax.set_xlim(min_x, max_x)
        ax.set_ylim(min_y, max_y)
        
        # Formatting
        ax.set_title('PCB Layout - Zoomed Component View\nPanel 436-5002_R', 
                    fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('X Coordinate (mm)', fontsize=11)
        ax.set_ylabel('Y Coordinate (mm)', fontsize=11)
        ax.legend(loc='upper right', fontsize=10)
        ax.set_aspect('equal')
        
        # Add statistics box
        stats_text = f'Components: {len(df)}\nArea: {width:.1f} × {height:.1f} mm'
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
               fontsize=9, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, format='pdf')
        print(f"✓ Saved zoomed layout to {output_file}")
        print(f"  Component area: {width:.2f} × {height:.2f} mm")
        plt.close()
        
        return True
        
    except Exception as e:
        print(f"Error creating zoomed layout: {e}")
        return False


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("PCB LAYOUT VISUALIZATION - Panel 436-5002_R")
    print("="*70 + "\n")
    
    # Load data
    df, board_dims = load_pcb_data(
        csv_file='Panel 436-5002_R.csv',
        gko_file='Panel 436-5002_R.GKO'
    )
    
    if df is not None and board_dims is not None:
        print(f"\nBoard dimensions from GKO:")
        print(f"  Width:  {board_dims.width:.2f} mm")
        print(f"  Height: {board_dims.height:.2f} mm")
        
        min_x, max_x, min_y, max_y, comp_width, comp_height = get_component_bounds(df, margin_mm=5.0)
        print(f"\nComponent area:")
        print(f"  Width:  {comp_width:.2f} mm")
        print(f"  Height: {comp_height:.2f} mm")
        print(f"  Position: X={min_x:.2f}-{max_x:.2f}, Y={min_y:.2f}-{max_y:.2f}")
        print(f"\nCreating visualizations...\n")
        
        # Create view
        create_zoomed_layout(df, 'pcb_zoomed.pdf', component_margin=5.0)
        
        print("\n" + "="*70)
        print("SUCCESS!")
        print(" pcb_zoomed.pdf")
        print("="*70 + "\n")
    else:
        print("Failed to load data")