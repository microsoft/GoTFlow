import tkinter as tk

class WorkflowDesigner(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Workflow Designer')

        self.canvas = tk.Canvas(self, bg='white', width=800, height=600)
        self.canvas.pack(padx=10, pady=10)

        # Buttons to add shapes and connections
        tk.Button(self, text="Add Executor", command=lambda: self.add_executor(self.last_click_pos)).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(self, text="Add Decision", command=lambda: self.add_decision(self.last_click_pos)).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(self, text="Add Connection", command=self.start_connection_mode).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(self, text="Delete Shape", command=self.delete_shape).pack(side=tk.LEFT, padx=5, pady=5)

        # Bind events to handlers
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self._drag_data = {"x": 0, "y": 0, "item": None, "line": None}
        self.selected_items = []
        self.last_click_pos = (50, 50)
        self.connection_mode = False
        self.connection_line = None
        self.start_item = None

    def add_executor(self, position):
        x, y = position
        self.canvas.create_rectangle(x, y, x+100, y+50, fill="sky blue", tags="draggable")

    def add_decision(self, position):
        x, y = position
        points = [x, y-25, x+50, y, x, y+25, x-50, y]
        self.canvas.create_polygon(points, fill="light green", tags="draggable")

    def start_connection_mode(self):
        self.connection_mode = True
        self.canvas.bind("<Motion>", self.on_motion)
        self.reset_selection()

    def end_connection_mode(self):
        self.connection_mode = False
        self.canvas.unbind("<Motion>")
        if self.connection_line is not None:
            self.canvas.delete(self.connection_line)
            self.connection_line = None

    def add_connection(self, start_item, end_item):
        x1, y1, x2, y2 = self.canvas.bbox(start_item)
        start_x, start_y = (x1 + x2) // 2, (y1 + y2) // 2
        x1, y1, x2, y2 = self.canvas.bbox(end_item)
        end_x, end_y = (x1 + x2) // 2, (y1 + y2) // 2
        self.canvas.create_line(start_x, start_y, end_x, end_y, arrow=tk.LAST)

    def delete_shape(self):
        for item in self.selected_items:
            self.canvas.delete(item)
        self.reset_selection()

    def on_canvas_click(self, event):
        self.last_click_pos = (event.x, event.y)
        item = self.canvas.find_withtag("current")
        if item and "draggable" in self.canvas.gettags(item):
            if self.connection_mode:
                if not self.start_item:
                    self.start_item = item[0]
                    self.connection_line = self.canvas.create_line(event.x, event.y, event.x, event.y, arrow=tk.LAST)
                else:
                    self.add_connection(self.start_item, item[0])
                    self.end_connection_mode()
                    self.start_item = None
            else:
                self._drag_data["item"] = item
                self._drag_data["x"] = event.x
                self._drag_data["y"] = event.y
                self.select_item(item[0], toggle=True)
        else:
            self.reset_selection()
            if self.connection_mode:
                self.end_connection_mode()

    # The rest of your methods like select_item, on_drag, on_release ...

    def on_motion(self, event):
        if self.connection_line is not None and self.start_item is not None:
            self.canvas.coords(self.connection_line, self.canvas.coords(self.start_item)[:2] + [event.x, event.y])

    def select_item(self, item, multiple=False, toggle=False):
        if toggle:
            if item in self.selected_items:
                self.canvas.itemconfig(item, outline='')
                self.selected_items.remove(item)
            else:
                if not multiple:
                    self.reset_selection()
                self.canvas.itemconfig(item, outline='black')
                self.selected_items.append(item)
        else:
            if not multiple:
                self.reset_selection()
            if item not in self.selected_items:
                self.canvas.itemconfig(item, outline='black')
                self.selected_items.append(item)

    def reset_selection(self):
        for item in self.selected_items:
            self.canvas.itemconfig(item, outline='')
        self.selected_items = []

    def on_drag(self, event):
        if self._drag_data["item"] is not None and "draggable" in self.canvas.gettags(self._drag_data["item"]):
            delta_x = event.x - self._drag_data["x"]
            delta_y = event.y - self._drag_data["y"]
            self.canvas.move(self._drag_data["item"], delta_x, delta_y)
            self._drag_data["x"] = event.x
            self._drag_data["y"] = event.y

    def on_release(self, event):
        """ End dragging of an object """
        # Reset the drag data for the next drag operation
        self._drag_data["item"] = None
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0

        if self.connection_mode and self._drag_data["line"] is not None:
            # If in connection mode and there is a line being drawn, finalize it
            self.canvas.delete(self._drag_data["line"])
            self._drag_data["line"] = None
            self.end_connection_mode()


if __name__ == "__main__":
    app = WorkflowDesigner()
    app.mainloop()
