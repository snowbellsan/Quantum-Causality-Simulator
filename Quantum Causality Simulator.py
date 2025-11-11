import numpy as np
import random
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib
# Font settings
matplotlib.rcParams['font.family'] = 'Arial' 
import matplotlib.pyplot as plt
from tkinter import scrolledtext
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time
import csv
from datetime import datetime

# --------------------------
# --- Style Constants ---
# --------------------------
# Dark Theme Color Palette
BG_DARK = "#1a1a2e"
BG_MEDIUM = "#16213e"
BG_LIGHT = "#0f3460"
ACCENT_PRIMARY = "#e94560" # Red/Pink Accent
ACCENT_SECONDARY = "#00d4ff" # Cyan Accent
TEXT_PRIMARY = "#eaeaea"
TEXT_SECONDARY = "#a0a0a0"
SPECIAL_BH_COLOR = "#FF00FF" # Vivid Pink/Magenta for Black Hole
SPECIAL_OBS_COLOR = "#ffff00" # Vivid Yellow for Observation

# --------------------------
# --- Physical Constants ---
# --------------------------
GLOBAL_CBR_STRENGTH = 2.0
UNCERTAINTY_PROB = 0.1
BH_PROB = 0.01
DIFFUSION_RATE = 0.2
DISSIPATION_FACTOR = 0.5
QUANTUM_AMPLITUDE_TEMP = 0.5
QUANTUM_AMPLITUDE_FRAG = 50.0
CAUSALITY_STRENGTH = 0.8 
ENTANGLEMENT_PROB = 0.05

# --------------------------
# --- LocalCellState ---
# --------------------------
class LocalCellState:
    def __init__(self, cbr_strength, uncert_prob):
        self.cbr_strength = cbr_strength
        self.uncert_prob = uncert_prob
        self.local_temperature = cbr_strength * 10
        self.entropy_fragments = 0
        self.postponed_buffer = 0
        self.observation_count = 0
        self.causality_links = []
        self.entangled_with = None
        
    def update_local_events(self, new_events, bh_prob, dissipation_factor):
        at_risk_info = new_events * self.uncert_prob
        self.postponed_buffer += at_risk_info
        
        temp_increase = new_events * 0.05
        self.local_temperature += temp_increase
        entropy_increase = int(new_events * 0.02 * (1 + self.local_temperature / 100))
        self.entropy_fragments += entropy_increase

        action_log = f"Events: {new_events}, Temp+{temp_increase:.1f}, Fragments+{entropy_increase}, Postponed+{at_risk_info:.1f}\n"

        if random.random() < bh_prob:
            bh_residual = new_events * 0.3
            self.entropy_fragments += int(bh_residual * 0.5)
            dissipated_amount = self.entropy_fragments * dissipation_factor
            self.entropy_fragments -= int(dissipated_amount)
            self.local_temperature += int(dissipated_amount * 0.01)
            action_log += f"⚫BlackHole! Fragments adjusted, Temp+{int(dissipated_amount*0.01)}\n" 

        clean_up = int(self.entropy_fragments * 0.01 * self.cbr_strength)
        self.entropy_fragments -= clean_up
        if self.entropy_fragments < 0:
            self.entropy_fragments = 0
        action_log += f"Cleanup: {clean_up}, Fragments now {self.entropy_fragments:.0f}\n"

        return action_log

    def handle_observation(self, resolve_fraction):
        if self.postponed_buffer > 0:
            self.observation_count += 1
            resolved_amount = self.postponed_buffer * resolve_fraction
            self.postponed_buffer -= resolved_amount
            
            temp_spike = resolved_amount * 0.15
            self.local_temperature += temp_spike
            self.entropy_fragments += int(resolved_amount * 0.5)
            
            return f"👁️Observation #{self.observation_count}: resolved {resolved_amount:.1f}, Temp+{temp_spike:.1f}, Fragments+{int(resolved_amount*0.5)}\n"
        return ""

# --------------------------
# --- FinalGridSimulator ---
# --------------------------
class FinalGridSimulator:
    def __init__(self, size=5):
        self.size = size
        self.diffusion_rate = DIFFUSION_RATE
        self.bh_prob = BH_PROB
        self.grid = np.empty((size, size), dtype=object)
        for i in range(size):
            for j in range(size):
                self.grid[i, j] = LocalCellState(GLOBAL_CBR_STRENGTH, UNCERTAINTY_PROB)

        self.agent_center = range(1, 4)
        self.agent_params = {'obs_prob': 0.1, 'resolve_frac': 0.5}
        self.bg_params = {'obs_prob': 0.01, 'resolve_frac': 0.1}
        
        self.total_entropy_history = []
        self.total_temp_history = []
        self.bh_events = 0
        
        # Export data storage
        self.step_data = []

    def step(self):
        global CAUSALITY_STRENGTH
        
        log = ""
        temp_matrix = np.zeros((self.size, self.size))
        frag_matrix = np.zeros((self.size, self.size))
        obs_matrix = np.zeros((self.size, self.size))
        
        bh_locs = []
        ent_locs = []
        
        # Entanglement Creation
        if random.random() < ENTANGLEMENT_PROB:
            i1, j1 = random.randint(0, self.size-1), random.randint(0, self.size-1)
            i2, j2 = random.randint(0, self.size-1), random.randint(0, self.size-1)
            if (i1, j1) != (i2, j2):
                if self.grid[i1, j1].entangled_with:
                     self.grid[i1, j1].entangled_with = None
                if self.grid[i2, j2].entangled_with:
                     self.grid[i2, j2].entangled_with = None
                     
                self.grid[i1, j1].entangled_with = (i2, j2)
                self.grid[i2, j2].entangled_with = (i1, j1)
                ent_locs.extend([(i1, j1), (i2, j2)])
                log += f"🔗Entanglement created between ({i1},{j1}) and ({i2},{j2})\n"

        # Local Event Updates and Observations
        for i in range(self.size):
            for j in range(self.size):
                cell = self.grid[i, j]
                events = random.randint(500, 1500)
                params = self.agent_params if i in self.agent_center and j in self.agent_center else self.bg_params

                cell_log = cell.update_local_events(events, self.bh_prob, DISSIPATION_FACTOR)
                if "BlackHole" in cell_log:
                    self.bh_events += 1
                    bh_locs.append((i, j))
                log += f"[Cell {i},{j}] " + cell_log
                
                if random.random() < params['obs_prob']:
                    obs_log = cell.handle_observation(params['resolve_frac'])
                    log += obs_log
                    
                    if cell.entangled_with:
                        ei, ej = cell.entangled_with
                        entangled_cell = self.grid[ei, ej]
                        entangled_cell.local_temperature += cell.local_temperature * 0.1 
                        log += f"↔️Entanglement effect on ({ei},{ej})\n"

                # Quantum Fluctuation
                noise_temp = random.uniform(-QUANTUM_AMPLITUDE_TEMP, QUANTUM_AMPLITUDE_TEMP) * (1 - CAUSALITY_STRENGTH)
                noise_frag = random.uniform(-QUANTUM_AMPLITUDE_FRAG, QUANTUM_AMPLITUDE_FRAG) * (1 - CAUSALITY_STRENGTH)
                cell.local_temperature += noise_temp
                cell.entropy_fragments += noise_frag
                if cell.entropy_fragments < 0:
                    cell.entropy_fragments = 0

                temp_matrix[i, j] = cell.local_temperature
                frag_matrix[i, j] = cell.entropy_fragments
                obs_matrix[i, j] = cell.observation_count

        # Diffusion
        new_temp = temp_matrix.copy()
        new_frag = frag_matrix.copy()
        for i in range(self.size):
            for j in range(self.size):
                neighbors = []
                for di, dj in [(-1,0),(1,0),(0,-1),(0,1)]:
                    ni, nj = i+di, j+dj
                    if 0<=ni<self.size and 0<=nj<self.size:
                        neighbors.append((ni,nj))
                if neighbors:
                    avg_temp = np.mean([temp_matrix[ni,nj] for ni,nj in neighbors])
                    avg_frag = np.mean([frag_matrix[ni,nj] for ni,nj in neighbors])
                    effective_diffusion = self.diffusion_rate * CAUSALITY_STRENGTH
                    
                    new_temp[i,j] = temp_matrix[i,j]*(1-effective_diffusion) + avg_temp*effective_diffusion
                    new_frag[i,j] = frag_matrix[i,j]*(1-effective_diffusion) + avg_frag*effective_diffusion

        for i in range(self.size):
            for j in range(self.size):
                self.grid[i,j].local_temperature = new_temp[i,j]
                self.grid[i,j].entropy_fragments = new_frag[i,j]

        total_entropy = np.sum(frag_matrix)
        total_temp = np.sum(temp_matrix)
        self.total_entropy_history.append(total_entropy)
        self.total_temp_history.append(total_temp)
        
        # Store step data for export
        self.step_data.append({
            'total_entropy': total_entropy,
            'total_temperature': total_temp,
            'bh_events_total': self.bh_events,
            'bh_events_this_step': len(bh_locs),
            'entanglement_pairs': len(ent_locs) // 2,
            'causality_strength': CAUSALITY_STRENGTH
        })

        return log, new_temp, new_frag, obs_matrix, bh_locs, ent_locs

    def reset(self):
        for i in range(self.size):
            for j in range(self.size):
                self.grid[i,j] = LocalCellState(GLOBAL_CBR_STRENGTH, UNCERTAINTY_PROB)
        self.total_entropy_history = []
        self.total_temp_history = []
        self.bh_events = 0
        self.step_data = []
        
    def export_to_csv(self, filename):
        """Export simulation data to CSV file"""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                if not self.step_data:
                    return False
                    
                fieldnames = ['step', 'total_entropy', 'total_temperature', 
                             'bh_events_total', 'bh_events_this_step', 
                             'entanglement_pairs', 'causality_strength']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for step, data in enumerate(self.step_data, start=1):
                    row = {'step': step}
                    row.update(data)
                    writer.writerow(row)
            return True
        except Exception as e:
            print(f"Export error: {e}")
            return False

# --------------------------
# --- Modern Styled Button ---
# --------------------------
class ModernButton(tk.Canvas):
    def __init__(self, parent, text, command, width=120, height=40, bg_color=ACCENT_PRIMARY, hover_color=ACCENT_SECONDARY):
        super().__init__(parent, width=width, height=height, bg=BG_DARK, highlightthickness=0)
        self.text = text
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.current_color = bg_color
        
        self.rect = self.create_rectangle(2, 2, width-2, height-2, fill=bg_color, outline=bg_color, width=2)
        self.text_obj = self.create_text(width//2, height//2, text=text, fill=TEXT_PRIMARY, font=("Arial", 11, "bold"))
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        
    def on_enter(self, e):
        self.itemconfig(self.rect, fill=self.hover_color, outline=self.hover_color)
        
    def on_leave(self, e):
        self.itemconfig(self.rect, fill=self.bg_color, outline=self.bg_color)
        
    def on_click(self, e):
        original_fill = self.bg_color
        self.itemconfig(self.rect, fill=ACCENT_SECONDARY if original_fill != ACCENT_SECONDARY else ACCENT_PRIMARY, outline="white")
        self.update_idletasks()
        self.after(100, lambda: self.itemconfig(self.rect, fill=original_fill, outline=original_fill))
        self.command()

# --------------------------
# --- GUI ---
# --------------------------
class SimulationGUI:
    def __init__(self, root, simulator, steps=500, delay=0.5):
        self.root = root
        self.simulator = simulator
        self.steps = steps
        self.delay = delay 
        self.running = False
        self.current_step = 0
        
        self.max_temp_val = GLOBAL_CBR_STRENGTH * 10 
        self.max_frag_val = 1 
        self.max_obs_val = 1 

        self.im_refs = {}
        self.cbar_refs = {}
        self.loading_text_ref = None 

        root.title("Quantum Causality Simulator")
        root.configure(bg=BG_DARK)
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Dark.TFrame', background=BG_DARK)
        style.configure('Medium.TFrame', background=BG_MEDIUM)
        style.configure('Dark.TLabel', background=BG_DARK, foreground=TEXT_PRIMARY, font=("Arial", 10))
        style.configure('Title.TLabel', background=BG_DARK, foreground=ACCENT_SECONDARY, font=("Arial", 14, "bold"))
        style.configure('Dark.TLabelframe', background=BG_MEDIUM, foreground=TEXT_PRIMARY, borderwidth=2)
        style.configure('Dark.TLabelframe.Label', background=BG_MEDIUM, foreground=ACCENT_SECONDARY, font=("Arial", 11, "bold"))

        style.configure('TProgressbar', 
                        troughcolor=BG_DARK, 
                        background=ACCENT_PRIMARY,
                        bordercolor=BG_MEDIUM,
                        lightcolor=ACCENT_SECONDARY,
                        darkcolor=ACCENT_PRIMARY,
                        thickness=10)
        
        main_container = ttk.Frame(root, style='Dark.TFrame')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        header_frame = ttk.Frame(main_container, style='Dark.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = ttk.Label(header_frame, text="⚛️ Quantum Causality Simulator (Enhanced)", style='Title.TLabel')
        title_label.pack(side=tk.LEFT)
        
        left_panel = ttk.Frame(main_container, style='Dark.TFrame')
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        log_frame = ttk.LabelFrame(left_panel, text="📊 System Log (Important Events Highlighted)", style='Dark.TLabelframe')
        log_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.text_area = scrolledtext.ScrolledText(log_frame, width=60, height=6, 
                                                 bg=BG_LIGHT, fg=TEXT_PRIMARY, 
                                                 insertbackground=ACCENT_SECONDARY,
                                                 font=("Consolas", 8),
                                                 relief=tk.FLAT)
        self.text_area.pack(padx=5, pady=5)
        
        self.text_area.tag_config("bh_event", foreground=SPECIAL_BH_COLOR, font=("Consolas", 8, "bold"))
        self.text_area.tag_config("observation", foreground=SPECIAL_OBS_COLOR, font=("Consolas", 8, "bold"))
        self.text_area.tag_config("entanglement", foreground=ACCENT_SECONDARY, font=("Consolas", 8, "bold"))
        self.text_area.tag_config("step_header", foreground=TEXT_SECONDARY, font=("Consolas", 8))

        viz_frame = ttk.Frame(left_panel, style='Medium.TFrame')
        viz_frame.pack(fill=tk.BOTH, expand=True)
        
        plt.style.use('dark_background')
        self.fig, ((self.ax_temp, self.ax_frag), (self.ax_obs, self.ax_stats)) = plt.subplots(
            2, 2, figsize=(7, 5), facecolor=BG_MEDIUM
        )
        
        for ax in [self.ax_temp, self.ax_frag, self.ax_obs, self.ax_stats]:
            ax.set_facecolor(BG_LIGHT)
        
        self.ax2_stats = self.ax_stats.twinx()
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=viz_frame)
        self.canvas.get_tk_widget().configure(bg=BG_MEDIUM)
        self.canvas.get_tk_widget().pack(padx=5, pady=5)

        control_panel = ttk.Frame(left_panel, style='Medium.TFrame')
        control_panel.pack(fill=tk.X, pady=(10, 0))
        
        button_frame = ttk.Frame(control_panel, style='Medium.TFrame')
        button_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.start_button = ModernButton(button_frame, "▶ Start", self.start_simulation, 
                                         bg_color="#2ecc71", hover_color="#27ae60")
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.pause_button = ModernButton(button_frame, "⏸ Pause", self.pause_simulation,
                                         bg_color="#f39c12", hover_color="#e67e22")
        self.pause_button.pack(side=tk.LEFT, padx=5)
        
        self.reset_button = ModernButton(button_frame, "🔄 Reset", self.reset_simulation,
                                         bg_color=ACCENT_PRIMARY, hover_color="#c0392b")
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        self.help_button = ModernButton(button_frame, "❓ Help", self.show_help,
                                        bg_color=ACCENT_SECONDARY, hover_color="#0099cc")
        self.help_button.pack(side=tk.LEFT, padx=5)
        
        # NEW: Export Button
        self.export_button = ModernButton(button_frame, "💾 Export", self.export_data,
                                         bg_color="#9b59b6", hover_color="#8e44ad")
        self.export_button.pack(side=tk.LEFT, padx=5)
        
        status_progress_frame = ttk.Frame(control_panel, style='Medium.TFrame')
        status_progress_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        self.stats_label = ttk.Label(status_progress_frame, text="Step: 0 | BH events: 0 | Total Entropy: 0", 
                                     style='Dark.TLabel', font=("Arial", 11, "bold"))
        self.stats_label.pack(pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(status_progress_frame, orient=tk.HORIZONTAL, length=200, mode='determinate', style='TProgressbar')
        self.progress_bar.pack(pady=(0, 5), fill=tk.X)

        right_panel = ttk.Frame(main_container, style='Medium.TFrame')
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 0))
        
        causality_frame = ttk.LabelFrame(right_panel, text="⚡ Causality Control", style='Dark.TLabelframe')
        causality_frame.pack(fill=tk.X, pady=(0, 10), padx=10)
        
        self.causality_label = ttk.Label(causality_frame, 
                                         text=f"Causality Strength: {CAUSALITY_STRENGTH:.2f}", 
                                         style='Dark.TLabel', font=("Arial", 10, "bold"))
        self.causality_label.pack(pady=(10, 5))
        
        slider_container = tk.Frame(causality_frame, bg=BG_MEDIUM)
        slider_container.pack(pady=5)
        
        self.causality_slider = tk.Scale(slider_container, from_=0.0, to=1.0, resolution=0.01,
                                         orient=tk.HORIZONTAL, length=200, 
                                         command=self.update_causality,
                                         bg=BG_LIGHT, fg=TEXT_PRIMARY, 
                                         troughcolor=BG_DARK, 
                                         activebackground=ACCENT_SECONDARY,
                                         highlightthickness=0,
                                         font=("Arial", 8))
        self.causality_slider.set(CAUSALITY_STRENGTH)
        self.causality_slider.pack()
        
        slider_label = ttk.Label(causality_frame, text="← Chaos | Determinism →", 
                                 style='Dark.TLabel', font=("Arial", 9, "italic"))
        slider_label.pack(pady=(0, 10))
        
        desc_frame = ttk.LabelFrame(right_panel, text="📖 Quick Guide", style='Dark.TLabelframe')
        desc_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.description = scrolledtext.ScrolledText(desc_frame, width=30, height=15,
                                                     bg=BG_LIGHT, fg=TEXT_PRIMARY,
                                                     font=("Arial", 8),
                                                     relief=tk.FLAT,
                                                     wrap=tk.WORD)
        self.description.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        self.description.insert(tk.END,
            "🎯 Quick Guide\n\n"
            "【Grid Explanation】\n"
            "• **Refer to colorbars**\n"
            "• **Grid markers:**\n"
            "  - ⚫︎: Black Hole event\n"
            "  - ✖️: Quantum entanglement\n\n"
            "• Top-left: Local Temperature \n"
            "  Information processing activity\n\n"
            "• Top-right: Info Fragments \n"
            "  Entropy accumulation\n\n"
            "• Bottom-left: Observation Density \n"
            "  Consciousness emergence zone\n\n"
            "• Bottom-right: Statistics Graph \n"
            "  (Latest data emphasized)\n\n"
            "【Causality Control】\n"
            "Adjust determinism vs.\n"
            "randomness with slider\n\n"
            "Central 3×3 white box is\n"
            "the observation agent area\n\n"
            "【Export Function】\n"
            "Click 💾 Export to save\n"
            "simulation data as CSV"
        )
        self.description.config(state=tk.DISABLED)

    def _get_help_text(self):
        return """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ⚛️ Quantum Causality Simulator - Complete Guide
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[OVERVIEW]
This simulator visualizes the computational physics concept 
that "the universe is an information processing system."

Observe in real-time how concepts from quantum theory, 
thermodynamics, and information theory interact within 
a 5x5 grid space.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[DETAILED GRID EXPLANATION]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 Local Temperature
• Color Scale: **Inferno (Black → Yellow)**
• Meaning: **Information processing activity** or 
  **energy density** at each cell.
• Dynamics: Rises due to new events and observation. 
  Diffuses to neighbors based on CAUSALITY_STRENGTH.
→ **Brighter colors (more yellow) = higher temperature**

 Info Fragments (Entropy Fragments)
• Color Scale: **Viridis (Purple → Yellow)**
• Meaning: Represents the **trace of lost/dissipated 
  information** and total **entropy (randomness)**.
• Dynamics: Increases due to information processing 
  and Black Hole events.
→ **Brighter colors (more yellow) = greater entropy**

 Observation Density
• Color Scale: **Plasma (Dark Blue → Yellow)**
• Meaning: Cumulative count of **"observations 
  (information determination)"** in that cell.
• Feature: The **Agent Area** (central 3x3) has high 
  observation probability.
→ **Brighter colors = more "determined reality"**

 Global Statistics
• **Green Line: Total Entropy** | **Red Line: Total Temp**
• Dynamics: Uses transparency on the line and marks 
  the latest data point for visual dynamism.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[GRID ICONS]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• **⚫︎ (Vivid Pink Circle)**: Black Hole (BH) event 
  occurred in this cell in the current step.
• **✖️ (Cyan Cross)**: This cell is currently part of 
  a Quantum Entanglement pair.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[CAUSALITY CONTROL PARAMETER]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚡ **CAUSALITY_STRENGTH**

| Value | 1.0 (Determinism) | 0.0 (Chaos/Free Will) |
|---|---|---|
| **Diffusion** | Maximized | Stopped |
| **Quantum Fluctuation**| Minimized | Dominant |

→ Visual philosophical experiment: **"Fate vs. Free Will"**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[EXPORT FUNCTION]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💾 **Export to CSV**

Click the Export button to save simulation data including:
• Step number
• Total entropy per step
• Total temperature per step
• Black hole events (total and per step)
• Entanglement pairs count
• Causality strength value

Data is saved with timestamp in filename for easy tracking.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
    def show_help(self):
        help_window = tk.Toplevel(self.root)
        help_window.title("Complete Guide | Quantum Causality Simulator")
        help_window.configure(bg=BG_DARK)
        
        help_text_area = scrolledtext.ScrolledText(help_window, width=80, height=35, 
                                                 wrap=tk.WORD, font=("Arial", 10),
                                                 bg=BG_LIGHT, fg=TEXT_PRIMARY,
                                                 relief=tk.FLAT)
        help_text_area.pack(padx=15, pady=15)
        
        help_text_area.insert(tk.END, self._get_help_text())
        help_text_area.config(state=tk.DISABLED)

    def update_causality(self, value):
        global CAUSALITY_STRENGTH
        CAUSALITY_STRENGTH = float(value)
        self.causality_label.config(text=f"Causality Strength: {CAUSALITY_STRENGTH:.2f}")

    def show_loading(self):
        self.loading_text_ref = self.fig.text(0.5, 0.5, 'Now Loading...', 
                                              ha='center', va='center', 
                                              fontsize=30, color=ACCENT_SECONDARY, 
                                              weight='bold', transform=self.fig.transFigure)
        self.canvas.draw_idle()

    def hide_loading(self):
        if self.loading_text_ref:
            self.loading_text_ref.remove()
            self.loading_text_ref = None

    def start_simulation(self):
        if not self.running:
            self.show_loading()
            self.running = True
            threading.Thread(target=self.run_simulation, daemon=True).start()

    def pause_simulation(self):
        self.running = False
        self.hide_loading()

    def reset_simulation(self):
        self.running = False
        self.simulator.reset()
        self.current_step = 0
        self.text_area.delete("1.0", tk.END)
        self.max_temp_val = GLOBAL_CBR_STRENGTH * 10
        self.max_frag_val = 1
        self.max_obs_val = 1

        self.ax_temp.clear()
        self.ax_frag.clear()
        self.ax_obs.clear()
        self.ax_stats.clear()
        self.ax2_stats.clear()

        for cbar in self.cbar_refs.values():
            if cbar:
                try:
                    cbar.remove()
                except:
                    pass

        self.im_refs = {}
        self.cbar_refs = {}
        self.loading_text_ref = None 
        self.hide_loading()
        self.progress_bar['value'] = 0
       
        self.canvas.draw()
        self.stats_label.config(text="Step: 0 | BH events: 0 | Total Entropy: 0")
    
    def export_data(self):
        """Export simulation data to CSV file"""
        if not self.simulator.step_data:
            messagebox.showwarning("No Data", "No simulation data to export. Please run the simulation first.")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"quantum_sim_data_{timestamp}.csv"
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=default_filename,
            title="Export Simulation Data"
        )
        
        if filename:
            success = self.simulator.export_to_csv(filename)
            if success:
                messagebox.showinfo("Export Complete", 
                                   f"Data successfully exported to:\n{filename}\n\n"
                                   f"Total steps: {len(self.simulator.step_data)}")
            else:
                messagebox.showerror("Export Failed", "Failed to export data. Please try again.")

    def run_simulation(self):
        while self.running and self.current_step < self.steps:
            self.current_step += 1
            
            log, temp_matrix, frag_matrix, obs_matrix, bh_locs, ent_locs = self.simulator.step() 
            
            self.max_temp_val = max(self.max_temp_val, np.max(temp_matrix) if temp_matrix.size > 0 else 0)
            self.max_frag_val = max(self.max_frag_val, np.max(frag_matrix) if frag_matrix.size > 0 else 0)
            self.max_obs_val = max(self.max_obs_val, np.max(obs_matrix) if obs_matrix.size > 0 else 0)
            
            full_log_entry = f"\n─── Step {self.current_step} ───\n{log[:400]}...\n"
            self.text_area.insert(tk.END, full_log_entry, "step_header")
            
            start_index = f"{self.text_area.index(tk.END)} - {len(full_log_entry)}c"
            
            if "BlackHole!" in log:
                 self.text_area.tag_add("bh_event", f"{start_index} + 1c", f"{start_index} + {len(full_log_entry)}c")
            if "Observation #" in log:
                 self.text_area.tag_add("observation", f"{start_index} + 1c", f"{start_index} + {len(full_log_entry)}c")
            if "Entanglement created" in log or "Entanglement effect" in log:
                 self.text_area.tag_add("entanglement", f"{start_index} + 1c", f"{start_index} + {len(full_log_entry)}c")

            self.text_area.yview(tk.END)

            progress_value = (self.current_step / self.steps) * 100
            self.progress_bar['value'] = progress_value
            self.root.update_idletasks()
            
            self.update_plots(temp_matrix, frag_matrix, obs_matrix, bh_locs, ent_locs)
            
            self.stats_label.config(text=f"Step: {self.current_step} | BH events: {self.simulator.bh_events} | Total Entropy: {np.sum(frag_matrix):.0f}")
            
            time.sleep(self.delay)
            self.hide_loading()
            
        if self.current_step >= self.steps:
            self.running = False
            self.progress_bar['value'] = 100
            self.stats_label.config(text=f"Simulation Complete | Steps: {self.steps} | Total Entropy: {np.sum(frag_matrix):.0f}")
            self.hide_loading()

    def update_plots(self, temp_matrix, frag_matrix, obs_matrix, bh_locs, ent_locs):
        
        if self.current_step == 1 and self.loading_text_ref:
            self.hide_loading()
            
        def draw_matrix(ax, matrix, title, cmap, agent_color, v_max, cbar_key, label_text, bh_locs, ent_locs):
            
            ax.clear() 
            ax.set_facecolor(BG_LIGHT)

            ax.set_title(title, color=TEXT_PRIMARY, fontsize=12, fontweight='bold', pad=10)
            vmin = 0.1
            im = ax.imshow(matrix, cmap=cmap, interpolation='nearest', vmin=vmin, vmax=max(v_max, 1))
            self.im_refs[cbar_key] = im
            
            if cbar_key not in self.cbar_refs or self.cbar_refs[cbar_key] is None:
                cbar = self.fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
                cbar.set_label(label_text, color=TEXT_PRIMARY, fontsize=9, rotation=270, labelpad=15)
                cbar.ax.tick_params(colors=TEXT_PRIMARY, labelsize=8)
                cbar.outline.set_edgecolor(TEXT_SECONDARY)
                self.cbar_refs[cbar_key] = cbar
            else:
                self.cbar_refs[cbar_key].mappable.set_clim(vmin, max(v_max, 1)) 
                self.cbar_refs[cbar_key].update_normal()
            
            for r in self.simulator.agent_center:
                for c in self.simulator.agent_center:
                    ax.add_patch(plt.Rectangle((c-0.5, r-0.5), 1, 1, 
                                             fill=False, edgecolor=agent_color, 
                                             linewidth=2.5, linestyle='--'))
            
            for r, c in bh_locs:
                ax.plot(c, r, 'o', markerfacecolor=SPECIAL_BH_COLOR, markeredgecolor=BG_DARK, markersize=12, alpha=0.9, label='Black Hole')
                
            for r, c in ent_locs:
                ax.plot(c, r, 'X', markerfacecolor=ACCENT_SECONDARY, markeredgecolor=ACCENT_SECONDARY, markersize=14, alpha=0.9, markeredgewidth=2, label='Entangled')
            
            ax.set_xticks([])
            ax.set_yticks([])
            ax.spines['top'].set_color(BG_LIGHT)
            ax.spines['bottom'].set_color(BG_LIGHT)
            ax.spines['left'].set_color(BG_LIGHT)
            ax.spines['right'].set_color(BG_LIGHT)

        draw_matrix(self.ax_temp, temp_matrix, " Local Temperature", 'inferno', SPECIAL_OBS_COLOR, self.max_temp_val, 'temp', 'Temperature (Hot)', bh_locs, ent_locs)
        draw_matrix(self.ax_frag, frag_matrix, " Info Fragments", 'viridis', SPECIAL_OBS_COLOR, self.max_frag_val, 'frag', 'Fragments (High Entropy)', bh_locs, ent_locs)
        draw_matrix(self.ax_obs, obs_matrix, " Observation Density", 'plasma', ACCENT_SECONDARY, self.max_obs_val, 'obs', 'Observations (Fixed Reality)', bh_locs, ent_locs)
        
        self.ax_stats.clear()
        self.ax2_stats.clear()
        
        self.ax_stats.set_title(" Global Statistics", color=TEXT_PRIMARY, fontsize=12, fontweight='bold', pad=10)
        self.ax_stats.set_facecolor(BG_LIGHT)
        
        if len(self.simulator.total_entropy_history) > 1:
            steps_so_far = range(1, len(self.simulator.total_entropy_history)+1)
            
            line1 = self.ax_stats.plot(steps_so_far, self.simulator.total_entropy_history, 
                                      label='Total Entropy', color='#2ecc71', linewidth=2, alpha=0.6)
            self.ax_stats.plot(self.current_step, self.simulator.total_entropy_history[-1], 'o', color='#2ecc71', markersize=6, alpha=1.0)
            self.ax_stats.set_ylabel('Total Entropy', color='#2ecc71', fontsize=10, fontweight='bold')
            self.ax_stats.tick_params(axis='y', labelcolor='#2ecc71')
            
            line2 = self.ax2_stats.plot(steps_so_far, self.simulator.total_temp_history, 
                                       label='Total Temp', color=ACCENT_PRIMARY, 
                                       linestyle='--', linewidth=2, alpha=0.6)
            self.ax2_stats.plot(self.current_step, self.simulator.total_temp_history[-1], 'o', color=ACCENT_PRIMARY, markersize=6, alpha=1.0)
            self.ax2_stats.set_ylabel('Total Temp', color=ACCENT_PRIMARY, fontsize=10, fontweight='bold')
            self.ax2_stats.tick_params(axis='y', labelcolor=ACCENT_PRIMARY)
            
            lines = line1 + line2
            labels = [l.get_label() for l in lines]
            self.ax_stats.legend(lines, labels, loc='upper left', fontsize=8, 
                                 framealpha=0.8, facecolor=BG_MEDIUM, edgecolor=TEXT_SECONDARY)
            
            self.ax_stats.set_xlabel('Step', fontsize=10, color=TEXT_PRIMARY)
            self.ax_stats.grid(True, alpha=0.2, color=TEXT_SECONDARY)
            
            for ax in [self.ax_stats, self.ax2_stats]:
                ax.spines['top'].set_color(BG_LIGHT)
                ax.spines['bottom'].set_color(TEXT_SECONDARY)
                ax.spines['left'].set_color(TEXT_SECONDARY)
                ax.spines['right'].set_color(TEXT_SECONDARY)
                ax.tick_params(colors=TEXT_SECONDARY)

        self.fig.tight_layout()
        self.canvas.draw()

# --------------------------
# --- Main Execution ---
# --------------------------
if __name__ == "__main__":
    root = tk.Tk()
    sim = FinalGridSimulator(size=5)
    gui = SimulationGUI(root, sim, steps=500, delay=0.5)
    root.mainloop()