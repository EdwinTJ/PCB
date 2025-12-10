"""
CreateSearchablePDF.py

Create searchable PDFs by:
1. Rendering silkscreen image from GTO file
2. Extracting text coordinates from GTO file
3. Overlaying invisible searchable text on top of image
4. Saving as searchable PDF

This allows:
- Visual: Full-color PCB image with components
- Searchable: Ctrl+F to find "R1", "U2", etc.
- Printable: High-quality print output
"""

import json
from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class TextCoordinate:
    """Text position on PDF"""
    text: str
    x: float  # mm
    y: float  # mm
    font_size: float


class SearchablePDFCreator:
    """
    Create searchable PDFs with embedded text layer.
    
    Process:
    1. Start with silkscreen image (PNG/SVG from GTO rendering)
    2. Load text coordinates from parsed GTO data
    3. Create PDF with image + invisible text overlay
    4. Result: Visually matches actual PCB + searchable text
    """
    
    def __init__(self, image_file: str, json_coordinates: str, verbose: bool = True):
        """
        Initialize PDF creator.
        
        Args:
            image_file: Path to rendered silkscreen image (PNG/SVG)
            json_coordinates: Path to JSON file with text coordinates
            verbose: Print status messages
        """
        self.image_file = image_file
        self.json_coordinates = json_coordinates
        self.verbose = verbose
        self.text_coords: List[TextCoordinate] = []
        
    def load_coordinates(self) -> bool:
        """Load text coordinates from JSON file"""
        try:
            with open(self.json_coordinates, 'r') as f:
                data = json.load(f)
            
            for item in data.get('designators', []):
                coord = TextCoordinate(
                    text=item['designator'],
                    x=item['x_mm'],
                    y=item['y_mm'],
                    font_size=item.get('size_mm', 2.0)
                )
                self.text_coords.append(coord)
            
            if self.verbose:
                print(f"✓ Loaded {len(self.text_coords)} text coordinates")
            
            return True
            
        except Exception as e:
            print(f"Error loading coordinates: {e}")
            return False
    
    def create_pdf_with_reportlab(self, output_file: str) -> bool:
        """
        Create searchable PDF using ReportLab library.
        
        Args:
            output_file: Output PDF filename
            
        Returns:
            True if successful
        """
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.units import mm
            from PIL import Image
            
            if self.verbose:
                print(f"Creating searchable PDF: {output_file}")
            
            # Load image to get dimensions
            img = Image.open(self.image_file)
            img_width_px, img_height_px = img.size
            
            # Create PDF (assuming 300 DPI for conversion)
            dpi = 300
            pdf_width = img_width_px / dpi * 25.4  # Convert pixels to mm
            pdf_height = img_height_px / dpi * 25.4
            
            if self.verbose:
                print(f"  Image size: {img_width_px} × {img_height_px} px")
                print(f"  PDF size: {pdf_width:.1f} × {pdf_height:.1f} mm")
            
            # Create canvas
            c = canvas.Canvas(output_file, pagesize=(pdf_width*mm, pdf_height*mm))
            
            # Draw background image
            c.drawImage(self.image_file, 0, 0, 
                       width=pdf_width*mm, height=pdf_height*mm)
            
            # Add invisible text layer for searchability
            # Use white text with transparency = 0 (invisible)
            c.setFillAlpha(0)  # Make text invisible
            c.setFont("Helvetica", 8)
            
            for coord in self.text_coords:
                # Convert coordinates to PDF coordinates (from bottom-left origin)
                x_pdf = coord.x * mm
                y_pdf = (pdf_height - coord.y) * mm
                
                # Draw text at coordinate
                c.drawString(x_pdf, y_pdf, coord.text)
            
            c.save()
            
            if self.verbose:
                print(f"✓ Created searchable PDF: {output_file}")
                print(f"  Searchable designators: {len(self.text_coords)}")
            
            return True
            
        except ImportError:
            print("Error: reportlab not installed")
            print("Install with: pip install reportlab pillow")
            return False
        except Exception as e:
            print(f"Error creating PDF: {e}")
            return False
    
    def create_pdf_with_pypdf(self, base_pdf: str, output_file: str) -> bool:
        """
        Create searchable PDF by combining image PDF with text overlay.
        Requires base PDF to exist.
        
        Args:
            base_pdf: Base PDF with silkscreen image
            output_file: Output searchable PDF
            
        Returns:
            True if successful
        """
        try:
            from pypdf import PdfWriter, PdfReader
            from io import BytesIO
            
            # This approach requires a two-step process:
            # 1. Create image PDF
            # 2. Overlay text PDF on top
            
            print("PyPDF overlay method requires additional setup")
            print("Recommended: Use ReportLab method (simpler, single-step)")
            
            return False
            
        except ImportError:
            print("pypdf not available")
            return False


class SimpleSearchablePDFCreator:
    """
    Simplified version that creates searchable PDF from scratch.
    
    Uses ReportLab to:
    1. Load rendered silkscreen image
    2. Add invisible searchable text layer
    3. Save as PDF
    """
    
    @staticmethod
    def create_from_image_and_json(image_file: str, 
                                   json_file: str,
                                   output_file: str,
                                   verbose: bool = True) -> bool:
        """
        Create searchable PDF from image + coordinate JSON.
        
        Args:
            image_file: Rendered silkscreen image (PNG)
            json_file: Coordinates JSON file (from GerberSilkscreenParser)
            output_file: Output PDF file
            verbose: Print status
            
        Returns:
            True if successful
        """
        creator = SearchablePDFCreator(image_file, json_file, verbose)
        
        if not creator.load_coordinates():
            return False
        
        return creator.create_pdf_with_reportlab(output_file)


# ============================================================================
# WORKFLOW EXAMPLE
# ============================================================================

def example_workflow():
    """
    Example workflow showing how all the pieces fit together.
    
    Step 1: Parse GTO file for text coordinates
    Step 2: Render GTO file to image
    Step 3: Create searchable PDF combining both
    """
    
    print("\n" + "="*70)
    print("SEARCHABLE PDF CREATION WORKFLOW")
    print("="*70 + "\n")
    
    # Files
    gto_file = 'Panel 436-5002_R.GTO'
    image_file = 'silkscreen.png'
    json_file = 'designators.json'
    pdf_file = 'pcb_searchable.pdf'
    
    print("Step 1: Parse GTO silkscreen file")
    print(f"  Input: {gto_file}")
    print(f"  Output: {json_file}")
    
    # from GerberSilkscreenParser import GTO_Parser
    # parser = GTO_Parser(gto_file, verbose=True)
    # parser.parse()
    # parser.export_to_json(json_file)
    
    print("\nStep 2: Render GTO to image")
    print(f"  Input: {gto_file}")
    print(f"  Output: {image_file}")
    
    # from RenderGerber import GerberRenderer
    # renderer = GerberRenderer(gto_file, verbose=True)
    # renderer.load()
    # renderer.render_to_png(image_file)
    
    print("\nStep 3: Create searchable PDF")
    print(f"  Inputs: {image_file} + {json_file}")
    print(f"  Output: {pdf_file}")
    
    creator = SimpleSearchablePDFCreator()
    # success = creator.create_from_image_and_json(image_file, json_file, pdf_file)
    
    print("\nResult:")
    print(f"  ✓ Searchable PDF: {pdf_file}")
    print(f"  - Contains rendered silkscreen image")
    print(f"  - Has invisible searchable text layer")
    print(f"  - Search with Ctrl+F for any designator (R1, U2, etc.)")


# ============================================================================
# TEST / MAIN
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("SEARCHABLE PDF CREATOR - TEST")
    print("="*70 + "\n")
    
    print("This script creates searchable PDFs from:")
    print("  1. Rendered silkscreen image (PNG)")
    print("  2. Text coordinates (JSON)\n")
    
    print("Required files:")
    print("  - silkscreen.png (from RenderGerber.py)")
    print("  - designators.json (from GerberSilkscreenParser.py)\n")
    
    print("To use:")
    print("  1. Run GerberSilkscreenParser.py to get designators.json")
    print("  2. Run RenderGerber.py to get silkscreen.png")
    print("  3. Run this script to create PDF\n")
    
    # Check for test files
    if Path('silkscreen.png').exists() and Path('designators.json').exists():
        print("Found required files! Creating PDF...\n")
        
        creator = SimpleSearchablePDFCreator()
        success = creator.create_from_image_and_json(
            'silkscreen.png',
            'designators.json',
            'output_searchable.pdf',
            verbose=True
        )
        
        if success:
            print("\n✓ SUCCESS! Created searchable PDF")
        else:
            print("\n✗ Failed to create PDF")
    else:
        print("Waiting for:")
        if not Path('silkscreen.png').exists():
            print("  ✗ silkscreen.png (run RenderGerber.py)")
        if not Path('designators.json').exists():
            print("  ✗ designators.json (run GerberSilkscreenParser.py)")
        
        print("\nOnce you have the GTO file, follow the workflow:")
        example_workflow()