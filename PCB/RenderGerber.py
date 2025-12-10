"""
RenderGerber.py

Render Gerber GTO (silkscreen) files to:
- PNG images (for web, documents)
- SVG (for interactive web viewers)
- PDF (for printing, archival)

Uses the Gerbonara library for accurate rendering.

Installation:
    pip install gerbonara pillow reportlab numpy
"""

import os
from pathlib import Path
from typing import Optional, Tuple
import warnings
warnings.filterwarnings('ignore')


class GerberRenderer:
    """
    Render Gerber files to various formats using Gerbonara library.
    """
    
    def __init__(self, gerber_file: str, verbose: bool = True):
        """
        Initialize the Gerber renderer.
        
        Args:
            gerber_file: Path to .GTO (or other Gerber) file
            verbose: Print status messages
        """
        self.gerber_file = gerber_file
        self.verbose = verbose
        self.gerber_data = None
        self.bounds = None
        
    def check_dependencies(self) -> bool:
        """Check if required libraries are installed"""
        try:
            import gerber
            if self.verbose:
                print("✓ gerbonara library available")
            return True
        except ImportError:
            print("✗ gerbonara not installed")
            print("\nInstall with:")
            print("  pip install gerbonara pillow reportlab numpy")
            return False
    
    def load(self) -> bool:
        """
        Load and parse the Gerber file.
        
        Returns:
            True if successful
        """
        try:
            from gerber import loads
            
            if not os.path.exists(self.gerber_file):
                print(f"Error: File not found: {self.gerber_file}")
                return False
            
            with open(self.gerber_file, 'r', encoding='utf-8', errors='ignore') as f:
                gerber_content = f.read()
            
            self.gerber_data = loads(gerber_content)
            
            if self.verbose:
                print(f"✓ Loaded {self.gerber_file}")
                if hasattr(self.gerber_data, 'bounds'):
                    self.bounds = self.gerber_data.bounds
                    print(f"  Bounds: X({self.bounds[0]:.2f}-{self.bounds[2]:.2f}) "
                          f"Y({self.bounds[1]:.2f}-{self.bounds[3]:.2f})")
            
            return True
            
        except ImportError:
            print("Error: gerbonara library not installed")
            print("Install with: pip install gerbonara")
            return False
        except Exception as e:
            print(f"Error loading Gerber file: {e}")
            return False
    
    def render_to_png(self, output_file: str, 
                     width: int = 2400, height: int = 3200,
                     dpi: int = 300) -> bool:
        """
        Render to PNG image.
        
        Args:
            output_file: Output filename
            width: Image width in pixels
            height: Image height in pixels
            dpi: Resolution in dots per inch
            
        Returns:
            True if successful
        """
        try:
            if self.gerber_data is None:
                print("Error: Gerber file not loaded. Call load() first.")
                return False
            
            from gerber.render import GerberContext
            from PIL import Image
            
            if self.verbose:
                print(f"Rendering to PNG: {output_file}")
                print(f"  Resolution: {width}×{height} @ {dpi} DPI")
            
            # Create rendering context
            ctx = GerberContext()
            ctx.push(0)
            
            # Render the gerber data
            for item in self.gerber_data.statements:
                ctx.execute(item)
            
            # Convert to image and save
            image = ctx.image()
            image.save(output_file)
            
            if self.verbose:
                print(f"✓ Saved PNG: {output_file}")
            
            return True
            
        except ImportError:
            print("Error: Required libraries not installed")
            print("Install with: pip install gerbonara pillow")
            return False
        except Exception as e:
            print(f"Error rendering to PNG: {e}")
            return False
    
    def render_to_svg(self, output_file: str) -> bool:
        """
        Render to SVG format (perfect for web viewers).
        
        Args:
            output_file: Output filename
            
        Returns:
            True if successful
        """
        try:
            if self.gerber_data is None:
                print("Error: Gerber file not loaded. Call load() first.")
                return False
            
            if self.verbose:
                print(f"Rendering to SVG: {output_file}")
            
            # SVG rendering (if gerbonara supports it)
            # This is more complex - requires custom SVG generation from gerber data
            
            print("Note: SVG rendering requires custom implementation")
            print("Alternative: Use PNG and convert to SVG with external tool")
            
            return False
            
        except Exception as e:
            print(f"Error rendering to SVG: {e}")
            return False
    
    def get_bounds(self) -> Optional[Tuple[float, float, float, float]]:
        """Get the bounding box of the rendered content"""
        return self.bounds


class SimpleGerberRenderer:
    """
    Simplified Gerber renderer that works with basic Gerber parsing
    without requiring full gerbonara library for rendering.
    
    Useful for getting basic visualization while full setup is in progress.
    """
    
    @staticmethod
    def create_placeholder_png(output_file: str, 
                               width: int = 2400, height: int = 3200):
        """
        Create a placeholder PNG image with grid.
        Use this while setting up full Gerbonara rendering.
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create white image
            img = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(img)
            
            # Draw grid
            grid_size = 100
            for x in range(0, width, grid_size):
                draw.line([(x, 0), (x, height)], fill='lightgray', width=1)
            for y in range(0, height, grid_size):
                draw.line([(0, y), (width, y)], fill='lightgray', width=1)
            
            # Draw title
            title = "Gerber Silkscreen Rendering\n(Placeholder - waiting for .GTO file)"
            draw.text((100, 100), title, fill='black')
            
            img.save(output_file)
            print(f"✓ Created placeholder: {output_file}")
            
        except ImportError:
            print("Pillow not installed. Install with: pip install pillow")


# ============================================================================
# INSTALLATION HELPER
# ============================================================================

def check_and_install_dependencies():
    """
    Check for required libraries and provide installation instructions.
    """
    print("\n" + "="*70)
    print("DEPENDENCY CHECK")
    print("="*70 + "\n")
    
    dependencies = {
        'gerbonara': 'pip install gerbonara',
        'PIL': 'pip install pillow',
        'numpy': 'pip install numpy',
        'reportlab': 'pip install reportlab'
    }
    
    missing = []
    
    for lib_name, install_cmd in dependencies.items():
        try:
            __import__(lib_name.replace('PIL', 'PIL'))
            print(f"✓ {lib_name:15} installed")
        except ImportError:
            print(f"✗ {lib_name:15} NOT installed")
            missing.append(install_cmd)
    
    if missing:
        print("\n" + "="*70)
        print("INSTALLATION REQUIRED")
        print("="*70)
        for cmd in missing:
            print(f"  {cmd}")
        print("="*70 + "\n")
        return False
    
    print("\n✓ All dependencies installed!\n")
    return True


# ============================================================================
# TEST / MAIN
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("GERBER SILKSCREEN RENDERER TEST")
    print("="*70 + "\n")
    
    # First check dependencies
    print("Checking dependencies...\n")
    deps_ok = check_and_install_dependencies()
    
    if not deps_ok:
        print("Please install required libraries and run again")
        print("\nQuick install all:")
        print("  pip install gerbonara pillow reportlab numpy")
    
    # Try to render GTO file
    gto_file = 'Panel 436-5002_R.GTO'
    
    print(f"\nAttempting to render: {gto_file}\n")
    
    renderer = GerberRenderer(gto_file, verbose=True)
    
    if renderer.check_dependencies():
        if renderer.load():
            bounds = renderer.get_bounds()
            if bounds:
                print(f"\nSuccessfully loaded! Ready to render.")
                # renderer.render_to_png('silkscreen.png')
        else:
            print(f"\n⚠ Could not load {gto_file}")
            print("Make sure you have the file in the same directory")
    else:
        print("\nPlease install gerbonara to enable rendering")
        print("  pip install gerbonara")