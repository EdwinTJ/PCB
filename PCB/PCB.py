import pandas as pd
import re
import matplotlib.pyplot as plt
import chardet

with open('Panel 436-5002_R.csv', 'rb') as f:
    result = chardet.detect(f.read())
    encoding = result['encoding']
    print(f"Detected encoding: {encoding}")

# Skip first 12 lines
# TODO make it auto until it finds the first real HEAD
df = pd.read_csv('Panel 436-5002_R.csv', skiprows=12, encoding=encoding)

# Initial structure and data
print("DataFrame Head:")
print(df.head())
print("\nCleaned Colums:")
df.info()

# The columns seem to have leading/trailing whitespace and quotes in the names
df.columns = df.columns.str.strip().str.replace('"', '')

# Check clenaed colums
print("\nCleaned Colums:")
print(df.columns)

# ================
# Create PDF
# ================
df['Center-X(mm)'] = df['Center-X(mm)'].str.replace('mm', '').astype(float)
df['Center-Y(mm)'] = df['Center-Y(mm)'].str.replace('mm', '').astype(float)

# Determine board extents for plotting context (using the component boundary as an estimate)
min_x = df['Center-X(mm)'].min()
max_x = df['Center-Y(mm)'].max()
min_y = df['Center-Y(mm)'].min()
max_y = df['Center-Y(mm)'].max()

# Create plot
plt.figure(figsize=(10,6))

# 1. Simulate the board outline (GKO) by adding a small margin around components
# This represents the context of the PCB boundary
margin = 5 #mm
board_x = [min_x - margin, max_x + margin, max_x + margin, min_x - margin, min_x - margin]
board_y = [min_y - margin, min_y - margin, max_y + margin, max_y + margin, min_y - margin]
plt.plot(board_x,board_y,'k--', label='Simulated Board Outline(GKO)')

# 2 Plot components center points (PnP data)
plt.plot(df['Center-X(mm)'],df['Center-Y(mm)'], 'ro', markersize=4,label='Component Cneter (Pnp)')

# 3 Add Designatos Labels (Silkscreen/GTO data)
for i,row in df.iterrows():
    plt.text(row['Center-X(mm)'] + 0.5, row['Center-Y(mm)'], row['Designator'], fontsize=8, ha='left', va='center')

plt.title('Simulated PCB Layout: Designator Location Panel 436-5002_R')
plt.xlabel('X Coordinate (mm)')
plt.ylabel('Y Coordinate (mm)')
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()
plt.axis('equal') # Ensure scale is correct
plt.savefig('pcb_designator_layout.pdf')

print("Data cleaning successful. Coordinates are now floats.")