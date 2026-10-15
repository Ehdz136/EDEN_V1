import tkinter as tk
import math
import json
from pathlib import Path
from tkinter import messagebox

from world import World
from config import WORLD_SIZE


class EdenVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("EDEN | Civilization Observation System")
        self.root.geometry("1150x850")
        self.root.minsize(1000, 700)
        self.root.configure(bg="#101820")

        self.world = World(seed=42)
        self.running = False
        self.timer = None

        self.selected_agent = None
        self.active_view = "world"
        self.active_subject_tab = "profile"

        self.cell_size = 55
        self.map_size = WORLD_SIZE * self.cell_size

        self.colors = [
            "#67e8f9",
            "#c4b5fd",
            "#fbbf24",
            "#fb7185",
            "#5eead4"
        ]

        self.build_interface()
        self.draw_world()
        self.update_stats()
        self.update_agent_profile()

    # ======================================
    # INTERFACE
    # ======================================

    def build_interface(self):
        # Pack controls FIRST to prevent them disappearing.
        controls = tk.Frame(self.root, bg="#101820")
        controls.pack(
            side="bottom",
            fill="x",
            padx=25,
            pady=(8, 16)
        )

        header = tk.Frame(self.root, bg="#101820")
        header.pack(fill="x", padx=25, pady=(18, 8))

        tk.Label(
            header,
            text="EDEN / GENESIS",
            font=("Segoe UI", 22, "bold"),
            fg="#6ee7b7",
            bg="#101820"
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Artificial Civilization Observation System",
            font=("Segoe UI", 10),
            fg="#94a3b8",
            bg="#101820"
        ).pack(anchor="w")

        content = tk.Frame(self.root, bg="#101820")
        content.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=12
        )

        # ======================================
        # LEFT PANEL
        # ======================================

        world_panel = tk.Frame(
            content,
            bg="#172a27",
            padx=12,
            pady=12
        )
        world_panel.pack(side="left", anchor="n")

        tabs = tk.Frame(world_panel, bg="#172a27")
        tabs.pack(fill="x", pady=(0, 10))

        self.world_tab = tk.Button(
            tabs,
            text="WORLD VIEW",
            command=lambda: self.switch_view("world"),
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=12,
            pady=8
        )
        self.world_tab.pack(side="left", padx=(0, 8))

        self.network_tab = tk.Button(
            tabs,
            text="SOCIAL NETWORK",
            command=lambda: self.switch_view("network"),
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=12,
            pady=8
        )
        self.network_tab.pack(side="left")

        self.view_holder = tk.Frame(
            world_panel,
            bg="#172a27"
        )
        self.view_holder.pack()

        self.canvas = tk.Canvas(
            self.view_holder,
            width=self.map_size,
            height=self.map_size,
            bg="#214d3d",
            highlightthickness=0,
            cursor="hand2"
        )
        self.canvas.bind("<Button-1>", self.select_agent)

        self.network_canvas = tk.Canvas(
            self.view_holder,
            width=self.map_size,
            height=self.map_size,
            bg="#14202b",
            highlightthickness=0,
            cursor="hand2"
        )
        self.network_canvas.bind(
            "<Button-1>",
            self.select_network_agent
        )

        self.canvas.pack()

        self.view_hint = tk.Label(
            world_panel,
            text="Click an agent to inspect its profile",
            font=("Segoe UI", 9),
            fg="#94a3b8",
            bg="#172a27"
        )
        self.view_hint.pack(pady=(10, 0))

        self.update_view_tabs()

        # ======================================
        # RIGHT PANEL
        # ======================================

        right_panel = tk.Frame(
            content,
            bg="#101820"
        )
        right_panel.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(20, 0)
        )

        # WORLD STATISTICS
        stats_panel = tk.Frame(
            right_panel,
            bg="#1c2933",
            padx=20,
            pady=15
        )
        stats_panel.pack(fill="x", pady=(0, 12))

        tk.Label(
            stats_panel,
            text="WORLD MONITOR",
            font=("Segoe UI", 13, "bold"),
            fg="#e2e8f0",
            bg="#1c2933"
        ).pack(anchor="w", pady=(0, 10))

        self.day_label = self.create_stat(
            stats_panel, "DAY"
        )
        self.season_label = self.create_stat(
            stats_panel, "SEASON"
        )
        self.population_label = self.create_stat(
            stats_panel, "POPULATION"
        )
        self.hunger_label = self.create_stat(
            stats_panel, "AVERAGE HUNGER"
        )
        self.food_label = self.create_stat(
            stats_panel, "AVAILABLE FOOD"
        )

        # ======================================
        # SUBJECT OBSERVATION
        # ======================================

        profile_panel = tk.Frame(
            right_panel,
            bg="#1c2933",
            padx=20,
            pady=15
        )
        profile_panel.pack(fill="both", expand=True)

        tk.Label(
            profile_panel,
            text="EDEN / SUBJECT OBSERVATION",
            font=("Segoe UI", 13, "bold"),
            fg="#6ee7b7",
            bg="#1c2933"
        ).pack(anchor="w", pady=(0, 10))

        # NEW: Subject tabs
        subject_tabs = tk.Frame(
            profile_panel,
            bg="#1c2933"
        )
        subject_tabs.pack(fill="x", pady=(0, 10))

        self.profile_tab_button = tk.Button(
            subject_tabs,
            text="SUBJECT PROFILE",
            command=lambda: self.switch_subject_tab("profile"),
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=10,
            pady=7
        )
        self.profile_tab_button.pack(
            side="left",
            padx=(0, 7)
        )

        self.journal_tab_button = tk.Button(
            subject_tabs,
            text="PERSONAL JOURNAL",
            command=lambda: self.switch_subject_tab("journal"),
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=10,
            pady=7
        )
        self.journal_tab_button.pack(side="left")

        # Scrollable observation area
        profile_body = tk.Frame(
            profile_panel,
            bg="#1c2933"
        )
        profile_body.pack(
            fill="both",
            expand=True
        )

        scrollbar = tk.Scrollbar(
            profile_body,
            orient="vertical"
        )
        scrollbar.pack(side="right", fill="y")

        self.profile_text = tk.Text(
            profile_body,
            font=("Consolas", 10),
            fg="#e2e8f0",
            bg="#1c2933",
            insertbackground="#e2e8f0",
            wrap="word",
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            state="disabled",
            yscrollcommand=scrollbar.set
        )
        self.profile_text.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.config(
            command=self.profile_text.yview
        )

        # NEW: Export button
        self.export_button = tk.Button(
            profile_panel,
            text="EXPORT SELECTED JOURNAL",
            command=self.export_journal,
            font=("Segoe UI", 9, "bold"),
            bg="#334155",
            fg="white",
            relief="flat",
            padx=12,
            pady=8
        )
        self.export_button.pack(
            anchor="e",
            pady=(10, 0)
        )

        self.update_subject_tabs()

        # ======================================
        # BOTTOM CONTROLS
        # ======================================

        tk.Button(
            controls,
            text="NEXT DAY →",
            command=self.next_day,
            font=("Segoe UI", 11, "bold"),
            bg="#334155",
            fg="white",
            relief="flat",
            padx=18,
            pady=10
        ).pack(side="left", padx=(0, 10))

        self.play_button = tk.Button(
            controls,
            text="▶ PLAY",
            command=self.toggle_play,
            font=("Segoe UI", 11, "bold"),
            bg="#047857",
            fg="white",
            relief="flat",
            padx=18,
            pady=10
        )
        self.play_button.pack(side="left")

        tk.Button(
            controls,
            text="RESET",
            command=self.reset_world,
            font=("Segoe UI", 11, "bold"),
            bg="#475569",
            fg="white",
            relief="flat",
            padx=18,
            pady=10
        ).pack(side="right")

    def create_stat(self, parent, label):
        row = tk.Frame(parent, bg="#1c2933")
        row.pack(fill="x", pady=3)

        tk.Label(
            row,
            text=label,
            font=("Segoe UI", 9),
            fg="#94a3b8",
            bg="#1c2933"
        ).pack(side="left")

        value_label = tk.Label(
            row,
            text="--",
            font=("Segoe UI", 11, "bold"),
            fg="#f8fafc",
            bg="#1c2933"
        )
        value_label.pack(side="right")

        return value_label

    # ======================================
    # WORLD VIEW
    # ======================================

    def draw_world(self):
        self.canvas.delete("all")

        self.canvas.create_rectangle(
            0, 0,
            self.map_size, self.map_size,
            fill="#214d3d",
            outline=""
        )

        for x in range(WORLD_SIZE):
            for y in range(WORLD_SIZE):
                if (x * 7 + y * 3) % 5 == 0:
                    x1 = x * self.cell_size
                    y1 = y * self.cell_size

                    self.canvas.create_oval(
                        x1 + 7,
                        y1 + 7,
                        x1 + self.cell_size - 7,
                        y1 + self.cell_size - 7,
                        fill="#285943",
                        outline=""
                    )

        for x, y in self.world.food:
            cx = x * self.cell_size + self.cell_size / 2
            cy = y * self.cell_size + self.cell_size / 2

            self.canvas.create_oval(
                cx - 6, cy - 6,
                cx + 6, cy + 6,
                fill="#bef264",
                outline=""
            )

        for agent in self.world.agents:
            cx = agent.x * self.cell_size + self.cell_size / 2
            cy = agent.y * self.cell_size + self.cell_size / 2

            color = self.colors[
                agent.id % len(self.colors)
            ]

            if self.selected_agent == agent.id:
                self.canvas.create_oval(
                    cx - 16, cy - 16,
                    cx + 16, cy + 16,
                    outline="#ffffff",
                    width=3
                )

            self.canvas.create_oval(
                cx - 10, cy - 10,
                cx + 10, cy + 10,
                fill=color,
                outline="#f8fafc",
                width=2
            )

            self.canvas.create_text(
                cx, cy,
                text=str(agent.id),
                font=("Segoe UI", 8, "bold"),
                fill="#101820"
            )

    # ======================================
    # SOCIAL NETWORK
    # ======================================

    def switch_view(self, view):
        self.active_view = view

        self.canvas.pack_forget()
        self.network_canvas.pack_forget()

        if view == "network":
            self.network_canvas.pack()
            self.draw_network()
        else:
            self.canvas.pack()
            self.draw_world()

        self.update_view_tabs()

    def update_view_tabs(self):
        for button, name in (
            (self.world_tab, "world"),
            (self.network_tab, "network")
        ):
            active = self.active_view == name

            button.config(
                bg="#047857" if active else "#334155",
                fg="white",
                activebackground="#065f46"
            )

        if self.active_view == "network":
            hint = (
                "Click a subject to inspect relationships "
                "• Green: friends • Red: rivals"
            )
        else:
            hint = "Click an agent to inspect its profile"

        self.view_hint.config(text=hint)

    def network_positions(self):
        agents = sorted(
            self.world.agents,
            key=lambda a: a.id
        )

        center = self.map_size / 2
        radius = self.map_size * 0.37
        count = len(agents)

        if not count:
            return {}

        return {
            agent.id: (
                center + radius * math.cos(
                    2 * math.pi * i / count
                    - math.pi / 2
                ),
                center + radius * math.sin(
                    2 * math.pi * i / count
                    - math.pi / 2
                )
            )
            for i, agent in enumerate(agents)
        }

    def draw_network(self):
        canvas = self.network_canvas
        canvas.delete("all")

        positions = self.network_positions()
        agents = {
            a.id: a for a in self.world.agents
        }

        ids = sorted(agents)
        selected = self.selected_agent

        canvas.create_text(
            18, 18,
            anchor="nw",
            text="RELATIONSHIP NETWORK",
            fill="#6ee7b7",
            font=("Segoe UI", 12, "bold")
        )

        canvas.create_text(
            18, 43,
            anchor="nw",
            text="Lines reflect simulated trust",
            fill="#94a3b8",
            font=("Segoe UI", 9)
        )

        for i, a_id in enumerate(ids):
            for b_id in ids[i + 1:]:
                a = agents[a_id]
                b = agents[b_id]

                a_rel = a.relationships.get(b_id)
                b_rel = b.relationships.get(a_id)

                if not a_rel and not b_rel:
                    continue

                if (
                    selected is not None
                    and selected not in (a_id, b_id)
                ):
                    continue

                if selected == a_id and a_rel:
                    trust = a_rel["trust"]
                elif selected == b_id and b_rel:
                    trust = b_rel["trust"]
                else:
                    values = [
                        r["trust"]
                        for r in (a_rel, b_rel)
                        if r
                    ]
                    trust = sum(values) / len(values)

                if trust >= 25:
                    color = "#6ee7b7"
                elif trust <= -40:
                    color = "#fb7185"
                else:
                    color = "#64748b"

                x1, y1 = positions[a_id]
                x2, y2 = positions[b_id]

                canvas.create_line(
                    x1, y1,
                    x2, y2,
                    fill=color,
                    width=3 if selected in (a_id, b_id) else 2
                )

                if selected in (a_id, b_id):
                    canvas.create_text(
                        (x1 + x2) / 2,
                        (y1 + y2) / 2 - 9,
                        text=f"{trust:+.0f}",
                        fill="#f8fafc",
                        font=("Consolas", 9, "bold")
                    )

        for agent_id in ids:
            x, y = positions[agent_id]

            highlighted = selected == agent_id

            connected = (
                selected is None
                or highlighted
                or (
                    selected in agents
                    and agent_id in
                    agents[selected].relationships
                )
            )

            fill = (
                self.colors[agent_id % len(self.colors)]
                if connected else "#475569"
            )

            canvas.create_oval(
                x - 21, y - 21,
                x + 21, y + 21,
                fill="#1c2933",
                outline="#ffffff" if highlighted else fill,
                width=4 if highlighted else 2
            )

            canvas.create_text(
                x, y,
                text=f"{agent_id:03d}",
                fill=fill,
                font=("Consolas", 11, "bold")
            )

        if selected is None:
            footer = (
                "Select a subject to see their trust scores"
            )
        else:
            footer = (
                f"Viewing SUBJECT {selected:03d}'s relationships"
            )

        canvas.create_text(
            self.map_size / 2,
            self.map_size - 20,
            text=footer,
            fill="#94a3b8",
            font=("Segoe UI", 9)
        )

    def select_network_agent(self, event):
        for agent_id, (x, y) in self.network_positions().items():
            distance_squared = (
                (event.x - x) ** 2
                + (event.y - y) ** 2
            )

            if distance_squared <= 24 ** 2:
                self.selected_agent = agent_id
                self.draw_network()
                self.draw_world()
                self.update_agent_profile()
                return

    # ======================================
    # SELECT AGENT
    # ======================================

    def select_agent(self, event):
        grid_x = event.x // self.cell_size
        grid_y = event.y // self.cell_size

        for agent in reversed(self.world.agents):
            if (
                agent.x == grid_x
                and agent.y == grid_y
            ):
                self.selected_agent = agent.id

                self.draw_world()
                self.draw_network()
                self.update_agent_profile()
                return

    # ======================================
    # WORLD STATISTICS
    # ======================================

    def update_stats(self):
        self.day_label.config(
            text=str(self.world.day)
        )

        self.season_label.config(
            text=self.world.season
        )

        self.population_label.config(
            text=str(len(self.world.agents))
        )

        if self.world.agents:
            average_hunger = sum(
                agent.hunger
                for agent in self.world.agents
            ) / len(self.world.agents)
        else:
            average_hunger = 0

        self.hunger_label.config(
            text=f"{average_hunger:.1f}"
        )

        self.food_label.config(
            text=str(len(self.world.food))
        )

    # ======================================
    # SUBJECT TABS
    # ======================================

    def switch_subject_tab(self, tab):
        self.active_subject_tab = tab
        self.update_subject_tabs()
        self.update_agent_profile()

        # Start at the top when changing tabs.
        self.profile_text.yview_moveto(0)

    def update_subject_tabs(self):
        for button, name in (
            (self.profile_tab_button, "profile"),
            (self.journal_tab_button, "journal")
        ):
            active = self.active_subject_tab == name

            button.config(
                bg="#047857" if active else "#334155",
                fg="white",
                activebackground="#065f46"
            )

    def get_selected_agent(self):
        if self.selected_agent is None:
            return None

        return next(
            (
                agent
                for agent in self.world.agents
                if agent.id == self.selected_agent
            ),
            None
        )

    # ======================================
    # SUBJECT PROFILE
    # ======================================

    def update_agent_profile(self):
        agent = self.get_selected_agent()

        if agent is None:
            self.set_profile_text(
                "Click an agent in the world or social "
                "network to inspect it."
            )
            return

        if self.active_subject_tab == "journal":
            self.set_profile_text(
                self.format_journal(agent)
            )
        else:
            self.set_profile_text(
                self.format_profile(agent)
            )

    def format_profile(self, agent):
        social_lines = []

        for other_id, memory in sorted(
            agent.social_memory.items(),
            key=lambda item: item[1]["encounters"],
            reverse=True
        ):
            relationship = agent.relationships.get(other_id)

            if relationship:
                trust = relationship["trust"]
                label = agent.relationship_label(other_id)

                social_lines.append(
                    f"Subject {other_id:03d} | "
                    f"{label} | Trust: {trust:+.1f}\n"
                    f"  Encounters: {memory['encounters']} | "
                    f"Positive: {relationship['positive']} | "
                    f"Negative: {relationship['negative']}\n"
                    f"  Last event: "
                    f"{relationship['last_interaction']}"
                )
            else:
                social_lines.append(
                    f"Subject {other_id:03d}: "
                    f"{memory['encounters']} encounters"
                )

        social_text = (
            "\n\n".join(social_lines)
            if social_lines
            else "No individuals encountered yet."
        )

        relationships = agent.relationships

        friends = sum(
            1
            for r in relationships.values()
            if r["trust"] >= 25
        )

        rivals = sum(
            1
            for r in relationships.values()
            if r["trust"] <= -40
        )

        episodes = getattr(agent, "episodes", None)
        episode_count = (
            len(episodes.events)
            if episodes is not None
            else 0
        )

        profile = (
            f"SUBJECT {agent.id:03d}\n"
            f"{'─' * 35}\n\n"

            f"Position: ({agent.x}, {agent.y})\n"
            f"Current Action: {agent.last_action}\n\n"

            f"PHYSICAL STATE\n"
            f"Energy: {agent.energy}/100\n"
            f"Hunger: {agent.hunger}/100\n\n"

            f"PERSONALITY\n"
            f"Curiosity:   {agent.curiosity:.2f}\n"
            f"Sociability: {agent.sociability:.2f}\n"
            f"Cooperation: {agent.cooperation:.2f}\n\n"

            f"MEMORY\n"
            f"Known Food: {len(agent.food_memory)}\n"
            f"Past Locations: {len(agent.long_term_memory)}\n"
            f"Recorded Episodes: {episode_count}\n\n"

            f"SOCIAL RELATIONSHIPS\n"
            f"Individuals Met: {len(agent.social_memory)}\n"
            f"Nearby Right Now: {len(agent.nearby_agents)}\n"
            f"Friends / Close Friends: {friends}\n"
            f"Rivals: {rivals}\n\n"

            f"{social_text}\n\n"

            f"SURVIVAL\n"
            f"Food Collected: {agent.food_collected}"
        )

        return profile

    # ======================================
    # PERSONAL JOURNAL
    # ======================================

    def format_journal(self, agent):
        episodes = getattr(agent, "episodes", None)

        if episodes is None:
            return (
                f"SUBJECT {agent.id:03d} / PERSONAL JOURNAL\n\n"
                "Episodic memory is not available.\n"
                "Check that your updated agent.py is installed."
            )

        events = list(episodes.events)

        header = (
            f"EDEN / OBSERVER ARCHIVE\n"
            f"SUBJECT {agent.id:03d} / PERSONAL JOURNAL\n"
            f"{'─' * 35}\n"
            f"Current Day: {self.world.day}\n"
            f"Recorded Events: {len(events)}\n\n"
            f"Entries are based on actual simulation events.\n"
            f"Newest events appear first.\n\n"
        )

        if not events:
            return (
                header
                + "No recorded experiences yet.\n\n"
                + "Advance the simulation to begin recording."
            )

        entries = []

        for episode in reversed(events):
            event_type = episode.kind.replace(
                "_", " "
            ).upper()

            entries.append(
                f"DAY {episode.day:03d} | {event_type}\n"
                f"{episode.description}"
            )

        return header + "\n\n".join(entries)

    # ======================================
    # EXPORT JOURNAL
    # ======================================

    def export_journal(self):
        agent = self.get_selected_agent()

        if agent is None:
            messagebox.showinfo(
                "EDEN Observer Archive",
                "Select a subject before exporting a journal."
            )
            return

        episodes = getattr(agent, "episodes", None)

        if episodes is None:
            messagebox.showerror(
                "EDEN Observer Archive",
                "This subject does not have episodic memory."
            )
            return

        # Project directory containing visualizer.py
        project_root = Path(__file__).resolve().parent

        archive_folder = (
            project_root
            / "data"
            / "observer_archive"
        )

        archive_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        base_name = (
            f"subject_{agent.id:03d}_day_{self.world.day:03d}"
        )

        text_path = archive_folder / (
            base_name + "_journal.txt"
        )

        json_path = archive_folder / (
            base_name + "_episodes.json"
        )

        # Export readable journal.
        text_path.write_text(
            self.format_journal(agent),
            encoding="utf-8"
        )

        # Export structured episode records.
        episodes.export_json(json_path)

        messagebox.showinfo(
            "EDEN Observer Archive",
            "Journal exported successfully!\n\n"
            f"Saved to:\n{archive_folder}\n\n"
            f"{text_path.name}\n"
            f"{json_path.name}"
        )

    # ======================================
    # SCROLLABLE TEXT
    # ======================================

    def set_profile_text(self, text):
        previous_position = self.profile_text.yview()[0]

        self.profile_text.config(state="normal")
        self.profile_text.delete("1.0", "end")
        self.profile_text.insert("1.0", text)
        self.profile_text.config(state="disabled")

        self.profile_text.yview_moveto(
            previous_position
        )

    # ======================================
    # SIMULATION CONTROLS
    # ======================================

    def next_day(self):
        self.world.simulate_day()

        self.draw_world()
        self.draw_network()
        self.update_stats()
        self.update_agent_profile()

    def toggle_play(self):
        self.running = not self.running

        if self.running:
            self.play_button.config(
                text="❚❚ PAUSE"
            )
            self.run_simulation()
        else:
            self.play_button.config(
                text="▶ PLAY"
            )

            if self.timer is not None:
                self.root.after_cancel(
                    self.timer
                )
                self.timer = None

    def run_simulation(self):
        if self.running:
            self.next_day()

            self.timer = self.root.after(
                700,
                self.run_simulation
            )

    def reset_world(self):
        self.running = False

        if self.timer is not None:
            self.root.after_cancel(
                self.timer
            )
            self.timer = None

        self.play_button.config(
            text="▶ PLAY"
        )

        self.world = World(seed=42)
        self.selected_agent = None
        self.active_subject_tab = "profile"

        self.update_subject_tabs()
        self.draw_world()
        self.draw_network()
        self.update_stats()
        self.update_agent_profile()


if __name__ == "__main__":
    root = tk.Tk()
    app = EdenVisualizer(root)
    root.mainloop()