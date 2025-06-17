import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches

# Parse FEA strut data
fea_data = """
data_Thickness6.0_Width27_Height110,1.068947087
data_Thickness6.5_Width27_Height110,1.368925394
data_Thickness7.0_Width27_Height110,1.718213058
data_Thickness7.5_Width27_Height110,2.116402116
data_Thickness8.0_Width27_Height110,2.567723713
data_Thickness6.0_Width27_Height100,1.331694281
data_Thickness6.5_Width27_Height100,1.697193703
data_Thickness7.0_Width27_Height100,2.123024054
data_Thickness7.5_Width27_Height100,2.61037037
data_Thickness8.0_Width27_Height100,3.175503916
data_Thickness6.0_Width27_Height90,1.737619461
data_Thickness6.5_Width27_Height90,2.206044562
data_Thickness7.0_Width27_Height90,2.752167332
data_Thickness7.5_Width27_Height90,3.377807803
data_Thickness8.0_Width27_Height90,4.102564103
data_Thickness6.0_Width27_Height80,2.286584714
data_Thickness6.5_Width27_Height80,2.895277208
data_Thickness7.0_Width27_Height80,3.605841924
data_Thickness7.5_Width27_Height80,4.418412698
data_Thickness8.0_Width27_Height80,5.348311722
data_Thickness6.0_Width27_Height70,2.978850164
data_Thickness6.5_Width27_Height70,3.765060241
data_Thickness7.0_Width27_Height70,4.683840749
data_Thickness7.5_Width27_Height70,5.732301519
data_Thickness8.0_Width27_Height70,6.913238852
data_Thickness6.0_Width27_Height60,3.814216996
data_Thickness6.5_Width27_Height60,4.815331966
data_Thickness7.0_Width27_Height60,5.986254294
data_Thickness7.5_Width27_Height60,7.319365078
data_Thickness8.0_Width27_Height60,8.797278213
data_Thickness6.0_Width20_Height110,0.778210117
data_Thickness6.5_Width20_Height110,0.997008973
data_Thickness7.0_Width20_Height110,1.250781739
data_Thickness7.5_Width20_Height110,1.539645881
data_Thickness8.0_Width20_Height110,1.874414246
data_Thickness6.0_Width20_Height100,0.9694941638
data_Thickness6.5_Width20_Height100,1.236091725
data_Thickness7.0_Width20_Height100,1.545465917
data_Thickness7.5_Width20_Height100,1.89899923
data_Thickness8.0_Width20_Height100,2.318088098
data_Thickness6.0_Width20_Height90,1.261829653
data_Thickness6.5_Width20_Height90,1.603849238
data_Thickness7.0_Width20_Height90,2.007226014
data_Thickness7.5_Width20_Height90,2.470966148
data_Thickness8.0_Width20_Height90,3.006162633
data_Thickness6.0_Width20_Height80,1.664669261
data_Thickness6.5_Width20_Height80,2.108673978
data_Thickness7.0_Width20_Height80,2.624890557
data_Thickness7.5_Width20_Height80,3.214318706
data_Thickness8.0_Width20_Height80,3.904217433
data_Thickness6.0_Width20_Height70,2.164736443
data_Thickness6.5_Width20_Height70,2.748763057
data_Thickness7.0_Width20_Height70,3.423485108
data_Thickness7.5_Width20_Height70,4.197271773
data_Thickness8.0_Width20_Height70,5.078720163
data_Thickness6.0_Width20_Height60,2.776809339
data_Thickness6.5_Width20_Height60,3.507078763
data_Thickness7.0_Width20_Height60,4.357723579
data_Thickness7.5_Width20_Height60,5.324711315
data_Thickness8.0_Width20_Height60,6.421930648
"""

# Parse PDE type data
pde_data = """
PDE Type,Length,Category,Physical ST (N/Cycle)
Orthopedic,200,1,7.153
Orthopedic,250,0.5,2.407
Orthopedic,250,0.75,3.173
Orthopedic,250,1,3.953
Orthopedic,250,2,4.709
Orthopedic,250,3,5.811
Orthopedic,250,4,6.593
Orthopedic,250,5,6.418
Orthopedic,300,2,4.63
Adult Neuromuscular,200,2,5.231
Adult Neuromuscular,200,3,6.359
Adult Neuromuscular,200,4,7.202
Adult Neuromuscular,200,5,7.389
Adult Neuromuscular,250,1,1.951
Adult Neuromuscular,250,2,2.502
Adult Neuromuscular,250,3,2.943
Adult Neuromuscular,250,4,4.041
Adult Neuromuscular,250,5,5.165
Kids Neuromuscular,175,1,3.132
Kids Neuromuscular,175,2,3.88
Kids Neuromuscular,175,3,3.691
Kids Neuromuscular,175,4,3.894
Kids Neuromuscular,175,5,3.577
Kids Neuromuscular,225,1,1.354
Kids Neuromuscular,225,3,1.453
Kids Neuromuscular,225,5,1.856
Kids Neuromuscular,225,6,1.787
Kids Neuromuscular,225,7,2.016
"""

# Process FEA data
fea_lines = [line.strip() for line in fea_data.strip().split('\n') if line.strip()]
fea_df_data = []

for line in fea_lines:
    parts = line.split(',')
    filename = parts[0]
    stiffness = float(parts[1])
    
    # Extract parameters from filename
    params = filename.replace('data_', '').split('_')
    thickness = float(params[0].replace('Thickness', ''))
    width = int(params[1].replace('Width', ''))
    height = int(params[2].replace('Height', ''))
    
    fea_df_data.append({
        'thickness': thickness,
        'width': width,
        'height': height,
        'stiffness': stiffness
    })

fea_df = pd.DataFrame(fea_df_data)

# Process PDE data
from io import StringIO
pde_df = pd.read_csv(StringIO(pde_data))

# Create the overlapped visualization
fig, ax = plt.subplots(1, 1, figsize=(14, 10))
fig.suptitle('Combined FEA Strut Stiffness & PDE Type Analysis', fontsize=16, fontweight='bold')

# Plot FEA Strut Data
colors_width = {20: '#ff8c00', 27: '#2E8B57'}  # Orange for width 20, Green for width 27
markers_height = {60: 'o', 70: 's', 80: '^', 90: 'D', 100: 'v', 110: '<'}  # Different markers for each height

# Group by width and height for plotting
for width in fea_df['width'].unique():
    for height in fea_df['height'].unique():
        subset = fea_df[(fea_df['width'] == width) & (fea_df['height'] == height)]
        if not subset.empty:
            ax.plot(subset['thickness'], subset['stiffness'], 
                   color=colors_width[width], 
                   marker=markers_height[height],
                   markersize=10,
                   linewidth=3,
                   alpha=0.8,
                   label=f'FEA: W{width}mm H{height}mm')

# Plot PDE Type Data on same axis
colors_pde = {
    'Orthopedic': '#1f4e79',  # Dark blue
    'Adult Neuromuscular': '#ff8c00',  # Orange
    'Kids Neuromuscular': '#8b008b'  # Purple
}

# Plot horizontal lines for each PDE type and length combination
for pde_type in pde_df['PDE Type'].unique():
    for length in pde_df['Length'].unique():
        subset = pde_df[(pde_df['PDE Type'] == pde_type) & (pde_df['Length'] == length)]
        if not subset.empty:
            # Plot horizontal line for each stiffness value
            for _, row in subset.iterrows():
                ax.axhline(y=row['Physical ST (N/Cycle)'], 
                          color=colors_pde[pde_type],
                          linestyle='-',
                          alpha=0.3,
                          linewidth=1)
                
                # Add category marker
                ax.plot([8.1], [row['Physical ST (N/Cycle)']], 
                       marker='o',
                       markersize=6,
                       color=colors_pde[pde_type],
                       alpha=0.8)
                
                # Add text annotation
                ax.text(8.15, row['Physical ST (N/Cycle)'], 
                       f'{pde_type[:4]} L{int(length)} C{row["Category"]}',
                       color=colors_pde[pde_type],
                       fontsize=6,
                       va='center',
                       ha='left')

# Add order data as red circles using actual order specifications
order_data = [
    {'order': 2505018, 'thickness': 7.5, 'width': 20, 'height': 75, 'stiffness': 3.304},
    {'order': 2505033, 'thickness': 7.5, 'width': 20, 'height': 70, 'stiffness': 4.471},
    {'order': 2505031, 'thickness': 7.5, 'width': 18, 'height': 79, 'stiffness': 3.682}
]

for order in order_data:
    ax.scatter(order['thickness'], order['stiffness'], 
               color='red', s=120, marker='o', 
               edgecolors='darkred', linewidth=2,
               alpha=0.9, zorder=7,
               label='Orders' if order['order'] == 1 else "")
    
    # Add order number annotation
    ax.annotate(f"{order['order']}", 
                (order['thickness'], order['stiffness']),
                xytext=(30, 0), textcoords='offset points',
                fontsize=6, ha='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#ff5a5a', alpha=0.3),
                zorder=6)
    

# Customize the single axis
ax.set_xlabel('Thickness (mm)', fontsize=12, fontweight='bold')
ax.set_ylabel('Stiffness', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3)

# Add vertical grid lines at 0.25mm intervals
thickness_ticks = np.arange(6.0, 8.25, 0.25)
ax.set_xticks(thickness_ticks)
ax.grid(True, which='major', alpha=0.3)
ax.grid(True, which='minor', alpha=0.1)

ax.set_xlim(5.8, 8.2)
ax.set_ylim(0, 9)

# Create comprehensive legend
fea_handles = []
pde_handles = []
order_handles = []

# FEA legend entries
for width in sorted(fea_df['width'].unique()):
    for height in sorted(fea_df['height'].unique()):
        fea_handles.append(plt.Line2D([0], [0], color=colors_width[width], 
                                     marker=markers_height[height], linestyle='-',
                                     markersize=6, linewidth=2,
                                     label=f'FEA: W{width}mm H{height}mm'))

# PDE legend entries
for pde_type in colors_pde.keys():
    pde_handles.append(plt.Line2D([0], [0], color=colors_pde[pde_type], 
                                 linestyle='-', linewidth=1,
                                 label=f'PDE: {pde_type}'))

# Order legend entry
order_handles.append(plt.Line2D([0], [0], color='red', marker='o', linestyle='None',
                                markersize=8, markeredgecolor='darkred', markeredgewidth=1,
                                label='Orders'))

# Create three separate legends with smaller font size
legend1 = ax.legend(handles=fea_handles, loc='upper left', title='FEA Strut Data', 
                   fontsize=7, bbox_to_anchor=(0.02, 0.98), title_fontsize=8)
legend2 = ax.legend(handles=pde_handles, loc='lower right', title='PDE Type Data', 
                   fontsize=7, bbox_to_anchor=(0.98, 0.02), title_fontsize=8)
legend3 = ax.legend(handles=order_handles, loc='upper right', title='Orders', 
                   fontsize=7, bbox_to_anchor=(0.98, 0.98), title_fontsize=8)
ax.add_artist(legend1)
ax.add_artist(legend2)



plt.tight_layout()
plt.show()

# Print data summary
print("FEA Data Summary:")
print(fea_df.groupby(['width', 'height'])['stiffness'].agg(['mean', 'std', 'count']))
print("\nPDE Data Summary:")
print(pde_df.groupby('PDE Type')['Physical ST (N/Cycle)'].agg(['mean', 'std', 'count']))