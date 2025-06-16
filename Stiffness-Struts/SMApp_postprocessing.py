import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from scipy.signal import savgol_filter
from scipy.signal import argrelextrema
import matplotlib.widgets as widgets

def load_and_process_csv(file_path):
    df = pd.read_csv(file_path, skiprows=25, header=None)
    df.columns = ['Force', 'Angle']
    df['Force'] = df['Force'].abs()
    df['Time'] = range(len(df))
    return df

def filter_data(df):
    window_size = 31
    poly_order = 2
    df['Force_filtered'] = savgol_filter(df['Force'], window_size, poly_order)
    return df

def find_force_maximums(df, order=50):
    # Find local maxima in force data
    maxima_indices = argrelextrema(df['Force_filtered'].values, np.greater, order=order)[0]
    max_points = df.iloc[maxima_indices][['Time', 'Force_filtered']]
    max_points = max_points.rename(columns={'Force_filtered': 'Force'})
    return max_points.reset_index(drop=True)

class ManualPointEditor:
    def __init__(self, fig, ax, df, max_points):
        self.fig = fig
        self.ax = ax
        self.df = df
        self.max_points = max_points.copy()
        self.manual_points = []
        self.deleted_points = set()
        self.point_plots = {}  # Store scatter plot objects for each point
        self.point_texts = {}  # Store text objects for each point
        
        # Connect mouse events
        self.cid_click = fig.canvas.mpl_connect('button_press_event', self.onclick)
        
        # Add "Done" button
        axdone = plt.axes([0.81, 0.01, 0.1, 0.05])
        self.btn_done = widgets.Button(axdone, 'Done')
        self.btn_done.on_clicked(self.on_done)
        
        # Add instructions text
        plt.figtext(0.5, 0.01, "Left click: Add point | Right click: Delete nearest point | Click 'Done' when finished", 
                   ha="center", fontsize=11, bbox={"facecolor":"orange", "alpha":0.3, "pad":5})
        
        # Initial plot of points
        self.update_point_display()
        
    def onclick(self, event):
        if event.inaxes == self.ax:
            if event.button == 1:  # Left click - add point
                self.add_point(event)
            elif event.button == 3:  # Right click - delete point
                self.delete_nearest_point(event)
    
    def add_point(self, event):
        x = int(round(event.xdata))
        if 0 <= x < len(self.df):
            y = self.df.iloc[x]['Force_filtered']
            self.manual_points.append({'Time': x, 'Force': y})
            print(f"Added point at Time={x}, Force={y:.2f}")
            self.update_point_display()
    
    def delete_nearest_point(self, event):
        click_x = event.xdata
        click_y = event.ydata
        
        # Get all current points (original + manual - deleted)
        all_points = self.get_all_current_points()
        
        if len(all_points) == 0:
            return
        
        # Find nearest point
        min_distance = float('inf')
        nearest_idx = -1
        nearest_source = None
        
        # Check original points
        for idx, point in self.max_points.iterrows():
            if idx not in self.deleted_points:
                distance = np.sqrt((point['Time'] - click_x)**2 + 
                                 ((point['Force'] - click_y) / max(self.df['Force_filtered']))**2)
                if distance < min_distance:
                    min_distance = distance
                    nearest_idx = idx
                    nearest_source = 'original'
        
        # Check manual points
        for idx, point in enumerate(self.manual_points):
            distance = np.sqrt((point['Time'] - click_x)**2 + 
                             ((point['Force'] - click_y) / max(self.df['Force_filtered']))**2)
            if distance < min_distance:
                min_distance = distance
                nearest_idx = idx
                nearest_source = 'manual'
        
        # Delete the nearest point
        if nearest_source == 'original':
            self.deleted_points.add(nearest_idx)
            point = self.max_points.iloc[nearest_idx]
            print(f"Deleted original point at Time={point['Time']}, Force={point['Force']:.2f}")
        elif nearest_source == 'manual':
            point = self.manual_points.pop(nearest_idx)
            print(f"Deleted manual point at Time={point['Time']}, Force={point['Force']:.2f}")
        
        self.update_point_display()
    
    def get_all_current_points(self):
        # Combine original points (minus deleted) with manual points
        current_points = []
        
        # Add non-deleted original points
        for idx, point in self.max_points.iterrows():
            if idx not in self.deleted_points:
                current_points.append({'Time': point['Time'], 'Force': point['Force']})
        
        # Add manual points
        current_points.extend(self.manual_points)
        
        # Sort by time
        current_points.sort(key=lambda x: x['Time'])
        
        return current_points
    
    def update_point_display(self):
        # Clear existing point plots and texts
        for plot_obj in self.point_plots.values():
            plot_obj.remove()
        for text_obj in self.point_texts.values():
            text_obj.remove()
        
        self.point_plots.clear()
        self.point_texts.clear()
        
        # Get current points
        current_points = self.get_all_current_points()
        
        # Plot current points
        for i, point in enumerate(current_points):
            # Plot the point
            scatter = self.ax.scatter(point['Time'], point['Force'], 
                                    color='red', s=100, zorder=5)
            self.point_plots[i] = scatter
            
            # Add number label
            text = self.ax.text(point['Time'], point['Force'], f"{i + 1}", 
                              fontsize=10, ha='center', va='bottom', zorder=6)
            self.point_texts[i] = text
        
        self.fig.canvas.draw()
    
    def on_done(self, event):
        plt.close(self.fig)
    
    def get_updated_max_points(self):
        current_points = self.get_all_current_points()
        if not current_points:
            return pd.DataFrame(columns=['Time', 'Force'])
        
        return pd.DataFrame(current_points)

def interactive_maximums_selection(df, max_points):
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Plot raw and filtered force data
    ax.plot(df['Time'], df['Force'], alpha=0.3, label='Raw Force', color='lightgreen')
    ax.plot(df['Time'], df['Force_filtered'], label='Filtered Force', color='green')

    ax.set_xlabel('Time (samples)')
    ax.set_ylabel('Force (N)', color='green')
    ax.set_title('Force Time Series - Edit Maximum Points')
    ax.grid(True)
    ax.legend(loc='upper left')
    
    point_editor = ManualPointEditor(fig, ax, df, max_points)
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.15)  # Make room for the button and instructions
    plt.show()
    
    return point_editor.get_updated_max_points()

def plot_time_series_with_maximums(df, max_points, ax):
    # Plot raw and filtered force data
    ax.plot(df['Time'], df['Force'], alpha=0.3, label='Raw Force', color='lightgreen')
    ax.plot(df['Time'], df['Force_filtered'], label='Filtered Force', color='green')

    # Plot detected maximums
    if not max_points.empty:
        ax.scatter(max_points['Time'], max_points['Force'], color='red', s=100, label='Force Maximums')
        for i, point in max_points.iterrows():
            ax.text(point['Time'], point['Force'], f"{i + 1}", fontsize=10, ha='center', va='bottom')

    ax.set_xlabel('Time (samples)')
    ax.set_ylabel('Force (N)', color='green')
    ax.set_title('Force Time Series with Force Maximums')
    ax.grid(True)
    ax.legend(loc='upper left')

def plot_force_maximums_analysis(max_points, ax):
    if len(max_points) < 2:
        ax.text(0.5, 0.5, "Not enough maximum points detected for analysis",
                transform=ax.transAxes, fontsize=14, ha='center', va='center')
        return

    # Plot force maximums
    y = max_points['Force'].values
    x = np.array(range(len(y)))
    
    # Create bar chart of force values
    ax.bar(x, y, color='green', alpha=0.7)
    
    # Add data points and connecting line
    ax.plot(x, y, 'ro-', linewidth=2)
    
    # Add regression line
    slope, intercept = np.polyfit(x, y, 1)
    regression_line = slope * x + intercept
    ax.plot(x, regression_line, 'b--', linewidth=2, 
            label=f'Regression: {slope:.2f}x + {intercept:.2f}')
    
    # Calculate R-squared
    r_squared = np.corrcoef(x, y)[0, 1] ** 2
    
    # Add force values above bars
    for i, val in enumerate(y):
        ax.text(i, val + max(y)*0.02, f"{val:.2f}N", ha='center')

    # Calculate statistics
    avg_force = np.mean(y)
    std_force = np.std(y)
    max_force = np.max(y)
    
    # Add statistics text box
    stats_text = (f"Max Force: {max_force:.2f} N\n"
                  f"Avg Force: {avg_force:.2f} N\n"
                  f"Std Dev: {std_force:.2f} N\n"
                  f"Trend: {slope:.3f} N/cycle\n"
                  f"R²: {r_squared:.4f}")
    
    ax.text(0.05, 0.95, stats_text,
            transform=ax.transAxes, fontsize=12, verticalalignment='top', 
            bbox=dict(facecolor='white', alpha=0.7))

    ax.set_xlabel('Maximum Point Number')
    ax.set_ylabel('Force (N)')
    ax.set_xticks(x)
    ax.set_xticklabels([f"{i+1}" for i in range(len(y))])
    ax.grid(True, axis='y')
    ax.legend()

def analyze_force_data(file_path):
    df = load_and_process_csv(file_path)
    df_filtered = filter_data(df)
    
    # Auto-detect force maximums
    max_points = find_force_maximums(df_filtered)
    
    print(f"\nAutomatic detection found {len(max_points)} maximum points.")
    print("Opening interactive plot to manually edit points...")
    print("Left click to add points, right click to delete nearest point")
    
    # Allow manual editing of points
    max_points = interactive_maximums_selection(df_filtered, max_points)
    
    # Generate final analysis plots
    fig, axes = plt.subplots(2, 1, figsize=(14, 12))
    plot_time_series_with_maximums(df_filtered, max_points, axes[0])
    plot_force_maximums_analysis(max_points, axes[1])
    plt.tight_layout()
    plt.show()

    return df_filtered, max_points

if __name__ == "__main__":
    # Set default folder path
    folder_path = r"C:\Abilitymade Dropbox\Abilitymade team folder\Product Development & Testing\20250214_StiffnessMahine\CSV FILES"

    if not os.path.exists(folder_path):
        print(f"Default directory not found: {folder_path}")
        file_path = input("Enter the full path to the CSV file: ")
    else:
        csv_files = [f for f in os.listdir(folder_path) if f.endswith(".csv")]
        if not csv_files:
            print("No CSV files found in the directory.")
            file_path = input("Enter the full path to the CSV file: ")
        else:
            print("Available CSV files:")
            for i, file_name in enumerate(csv_files):
                print(f"{i + 1}: {file_name}")
            file_index = int(input("Enter the number of the file you want to process: ")) - 1
            if file_index < 0 or file_index >= len(csv_files):
                print("Invalid selection. Using first file.")
                file_index = 0
            file_path = os.path.join(folder_path, csv_files[file_index])

    # Analyze the data
    df_filtered, max_points = analyze_force_data(file_path)

    print("\nFinal Force Maximums:")
    print(f"Total number of maximum points: {len(max_points)}")
    
    if not max_points.empty:
        print("\nMaximum Points Data:")
        print(max_points)

        if len(max_points) > 1:
            forces = max_points['Force'].values
            x_indices = np.array(range(len(forces)))
            slope, intercept = np.polyfit(x_indices, forces, 1)
            r_squared = np.corrcoef(x_indices, forces)[0, 1] ** 2
            
            print(f"\nAnalysis Results:")
            print(f"Maximum Force: {np.max(forces):.2f} N")
            print(f"Average Force: {np.mean(forces):.2f} N")
            print(f"Standard Deviation: {np.std(forces):.2f} N")
            print(f"Range: {np.max(forces) - np.min(forces):.2f} N")
            print(f"Coefficient of Variation: {(np.std(forces)/np.mean(forces))*100:.2f}%")
            print(f"\nRegression Results:")
            print(f"Trend (slope): {slope:.3f} N/cycle")
            print(f"Intercept: {intercept:.2f} N")
            print(f"R²: {r_squared:.4f}")
            print(f"Equation: Force = {slope:.3f} × Cycle + {intercept:.2f}")
    else:
        print("No maximum points selected.")