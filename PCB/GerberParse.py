"""
GerberParse.py

Module for parsing Gerber files (specifically GKO - keepout layer files) 
and extracting dimensional data such as board boundaries and coordinate information.

This module extracts:
- Board dimensions (min/max X and Y coordinates)
- All coordinate points from the Gerber file
- Aperture information
- Layer information
"""

import re
from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class GerberCoordinate:
    """Represents a single coordinate point from Gerber data"""
    x: float
    y: float
    command: str  # D01 (draw), D02 (move), D03 (flash)
    
    def __repr__(self):
        return f"({self.x:.3f}, {self.y:.3f}) [{self.command}]"


@dataclass
class BoardDimensions:
    """Represents the overall board dimensions extracted from Gerber"""
    min_x: float
    max_x: float
    min_y: float
    max_y: float
    width: float
    height: float
    
    def __repr__(self):
        return (f"Board Dimensions:\n"
                f"  X: {self.min_x:.3f} to {self.max_x:.3f} (width: {self.width:.3f})\n"
                f"  Y: {self.min_y:.3f} to {self.max_y:.3f} (height: {self.height:.3f})")


class GerberParser:
    """
    Parser for Gerber files (.GKO, .GTO, .GBR, etc.)
    
    Gerber format uses imperial (inches) or metric (mm) coordinates.
    This parser handles the coordinate extraction and unit conversion.
    """
    
    def __init__(self, filename: str, verbose: bool = False):
        """
        Initialize the Gerber parser.
        
        Args:
            filename: Path to the Gerber file
            verbose: If True, print debug information
        """
        self.filename = filename
        self.verbose = verbose
        self.coordinates: List[GerberCoordinate] = []
        self.board_dimensions: Optional[BoardDimensions] = None
        self.unit = 'INCH'  # Default unit
        self.format_x = 2
        self.format_y = 2
        self.current_x = 0.0
        self.current_y = 0.0
        
    def parse(self) -> bool:
        """
        Parse the Gerber file and extract dimensional data.
        
        Returns:
            True if parsing was successful, False otherwise
        """
        try:
            with open(self.filename, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            if self.verbose:
                print(f"Parsing {self.filename}...")
                print(f"Total lines: {len(lines)}")
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line:
                    continue
                    
                # Extract unit information
                if line.startswith('%MOIN'):
                    self.unit = 'INCH'
                    if self.verbose:
                        print(f"Line {line_num}: Unit set to INCH")
                elif line.startswith('%MOMM'):
                    self.unit = 'MM'
                    if self.verbose:
                        print(f"Line {line_num}: Unit set to MM")
                
                # Extract format specification
                if line.startswith('%FSLAX'):
                    match = re.match(r'%FSLAX(\d)(\d)Y(\d)(\d)', line)
                    if match:
                        self.format_x = int(match.group(2))
                        self.format_y = int(match.group(4))
                        if self.verbose:
                            print(f"Line {line_num}: Format X={self.format_x}, Y={self.format_y}")
                
                # Extract coordinates
                self._extract_coordinates(line)
            
            # Calculate board dimensions
            if self.coordinates:
                self._calculate_dimensions()
                return True
            else:
                if self.verbose:
                    print("Warning: No coordinates found in file")
                return False
                
        except Exception as e:
            print(f"Error parsing {self.filename}: {e}")
            return False
    
    def _extract_coordinates(self, line: str):
        """
        Extract coordinate data from a Gerber line.
        
        Gerber coordinate format: Xxxxxd Yyyyyd D##
        where d## is the command (D01=draw, D02=move, D03=flash)
        """
        # Match coordinate patterns: X followed by digits, Y followed by digits, D command
        pattern = r'X(\d+)Y(\d+)D(\d+)'
        matches = re.findall(pattern, line)
        
        for x_str, y_str, command in matches:
            # Convert from Gerber format (integers with implicit decimals)
            x = self._convert_coordinate(x_str, self.format_x)
            y = self._convert_coordinate(y_str, self.format_y)
            
            # Convert to mm if in inches
            if self.unit == 'INCH':
                x *= 25.4  # 1 inch = 25.4 mm
                y *= 25.4
            
            # Store command type
            cmd_map = {'01': 'DRAW', '02': 'MOVE', '03': 'FLASH'}
            cmd = cmd_map.get(command, f'D{command}')
            
            coord = GerberCoordinate(x=x, y=y, command=cmd)
            self.coordinates.append(coord)
            
            if self.verbose and len(self.coordinates) % 10 == 0:
                print(f"  Extracted {len(self.coordinates)} coordinates...")
    
    def _convert_coordinate(self, coord_str: str, decimals: int) -> float:
        """
        Convert Gerber coordinate string to float value.
        
        Gerber uses integer representation with implicit decimal places.
        For example, with 2.5 format, "12345" = 123.45
        
        Args:
            coord_str: String of digits
            decimals: Number of decimal places
            
        Returns:
            Float value
        """
        if len(coord_str) == 0:
            return 0.0
        
        # Pad with leading zeros if necessary
        coord_int = int(coord_str)
        divisor = 10 ** decimals
        return coord_int / divisor
    
    def _calculate_dimensions(self):
        """Calculate the overall board dimensions from extracted coordinates"""
        if not self.coordinates:
            return
        
        x_values = [c.x for c in self.coordinates]
        y_values = [c.y for c in self.coordinates]
        
        min_x = min(x_values)
        max_x = max(x_values)
        min_y = min(y_values)
        max_y = max(y_values)
        
        width = max_x - min_x
        height = max_y - min_y
        
        self.board_dimensions = BoardDimensions(
            min_x=min_x,
            max_x=max_x,
            min_y=min_y,
            max_y=max_y,
            width=width,
            height=height
        )
        
        if self.verbose:
            print(f"\nBoard Dimensions Calculated:")
            print(self.board_dimensions)
    
    def get_dimensions(self) -> Optional[BoardDimensions]:
        """Get the calculated board dimensions"""
        return self.board_dimensions
    
    def get_coordinates(self) -> List[GerberCoordinate]:
        """Get all extracted coordinates"""
        return self.coordinates
    
    def get_boundary_points(self) -> List[Tuple[float, float]]:
        """Get outline/boundary points (simplified)"""
        if not self.coordinates:
            return []
        
        # Return unique points sorted by X then Y
        unique_points = list(set((c.x, c.y) for c in self.coordinates))
        return sorted(unique_points)
    
    def print_summary(self):
        """Print a summary of parsed data"""
        print("\n" + "="*60)
        print(f"GERBER FILE PARSE SUMMARY: {self.filename}")
        print("="*60)
        print(f"Unit: {self.unit}")
        print(f"Total Coordinates Extracted: {len(self.coordinates)}")
        if self.board_dimensions:
            print(self.board_dimensions)
        print("="*60 + "\n")


def parse_gerber_file(filename: str, verbose: bool = False) -> Optional[BoardDimensions]:
    """
    Convenience function to quickly parse a Gerber file and get dimensions.
    
    Args:
        filename: Path to Gerber file
        verbose: Print debug info
        
    Returns:
        BoardDimensions object or None if parsing failed
    """
    parser = GerberParser(filename, verbose=verbose)
    if parser.parse():
        parser.print_summary()
        return parser.get_dimensions()
    return None


# ============================================================================
# TEST / MAIN EXECUTION
# ============================================================================
if __name__ == '__main__':
    """
    Test the GerberParser with the GKO file
    """
    print("\n" + "="*60)
    print("GERBER PARSER TEST")
    print("="*60 + "\n")
    
    # Parse the GKO file
    test_file = 'Panel 436-5002_R.GKO'
    parser = GerberParser(test_file, verbose=True)
    
    if parser.parse():
        # Print summary
        parser.print_summary()
        
        # Show some sample coordinates
        print("Sample Coordinates (first 10):")
        for i, coord in enumerate(parser.get_coordinates()[:10]):
            print(f"  {i+1}. {coord}")
        
        # Show boundary points
        boundary = parser.get_boundary_points()
        print(f"\nUnique Boundary Points: {len(boundary)}")
        if boundary:
            print("First 5 boundary points:")
            for point in boundary[:5]:
                print(f"  {point}")
        
        # Get dimensions for reuse
        dims = parser.get_dimensions()
        if dims:
            print(f"\nDimensions ready for use in main PCB.py:")
            print(f"  board_min_x = {dims.min_x:.3f}")
            print(f"  board_max_x = {dims.max_x:.3f}")
            print(f"  board_min_y = {dims.min_y:.3f}")
            print(f"  board_max_y = {dims.max_y:.3f}")
            print(f"  board_width = {dims.width:.3f}")
            print(f"  board_height = {dims.height:.3f}")
    else:
        print("Failed to parse Gerber file")