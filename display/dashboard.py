import pygame

class Dashboard:
    def __init__(self, x, y, width, height, sims, model_names):
        self.rect = pygame.Rect(x, y, width, height)
        self.sims = sims
        self.model_names = model_names
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 32)
        
        # Colors for graph lines corresponding to models if needed, or just distinct colors
        self.graph_colors = [
            (255, 100, 100), # Reddish (Model 1)
            (100, 255, 100), # Greenish (Model 2)
            (100, 100, 255)  # Blueish (Model 3)
        ]
        self.bg_color = (30, 30, 30)
        self.axis_color = (200, 200, 200)

    def draw(self, surface):
        # Draw Dashboard Background
        pygame.draw.rect(surface, self.bg_color, self.rect)
        
        # Draw Section Titles/Stats
        section_width = self.rect.width // len(self.sims)
        
        for i, (sim, name) in enumerate(zip(self.sims, self.model_names)):
            section_x = self.rect.x + i * section_width
            
            # Draw Model Name
            name_text = self.title_font.render(name, True, self.graph_colors[i])
            surface.blit(name_text, (section_x + 10, self.rect.y + 10))
            
            # Draw Collision Count
            col_text = self.font.render(f"Crashes: {sim.collision_count}", True, (255, 255, 255))
            surface.blit(col_text, (section_x + 10, self.rect.y + 40))
            
            # Draw Current Avg Wait
            if sim.waiting_time_history:
                curr_wait = sim.waiting_time_history[-1]
            else:
                curr_wait = 0
            wait_text = self.font.render(f"Avg Wait: {curr_wait:.1f}s", True, (255, 255, 255))
            surface.blit(wait_text, (section_x + 10, self.rect.y + 65))

        # Graph Dimensions
        graph_width = (self.rect.width - 60) // 2  # Split width for 2 graphs, with padding
        graph_height = self.rect.height - 110
        graph_y = self.rect.y + 100
        
        # --- Graph 1: Average Waiting Time ---
        g1_x = self.rect.x + 20
        self._draw_graph(surface, g1_x, graph_y, graph_width, graph_height, "Avg Waiting Time (s)", 
                         lambda sim: sim.waiting_time_history, method='avg')

        # --- Graph 2: Cumulative Crashes ---
        g2_x = g1_x + graph_width + 20
        self._draw_graph(surface, g2_x, graph_y, graph_width, graph_height, "Cumulative Crashes", 
                         lambda sim: sim.collision_history, method='max')

    def _draw_graph(self, surface, x, y, w, h, title, data_extractor, method='avg'):
        # Background
        pygame.draw.rect(surface, (0, 0, 0), (x, y, w, h))
        pygame.draw.line(surface, self.axis_color, (x, y + h), (x + w, y + h), 2) # X Axis
        pygame.draw.line(surface, self.axis_color, (x, y), (x, y + h), 2) # Y Axis
        
        # Title
        title_surf = self.font.render(title, True, (200, 200, 200))
        surface.blit(title_surf, (x, y - 20))

        # Determine Scale
        max_val = 1
        for sim in self.sims:
            history = data_extractor(sim)
            if history:
                max_val = max(max_val, max(history))
        
        max_val *= 1.1 # Padding
        
        # Draw Lines
        for i, sim in enumerate(self.sims):
            raw_history = data_extractor(sim)
            if len(raw_history) < 2:
                continue
                
            # Adaptive Downsampling
            # We want roughly 1 point per pixel of width to maintain detail but avoid overcrowding
            # However, 'w' might be large, so let's cap it reasonably, e.g., w/2 or w
            target_points = int(w) 
            history = self._downsample_data(raw_history, target_points, method=method)

            points = []
            num_points = len(history)
            
            step_x = w / (num_points - 1) if num_points > 1 else 0
            
            for j, val in enumerate(history):
                px = x + j * step_x
                py = y + h - (val / (max_val if max_val > 0 else 1) * h)
                points.append((px, py))
            
            if len(points) > 1:
                pygame.draw.lines(surface, self.graph_colors[i], False, points, 2)

    def _downsample_data(self, data, max_points, method='avg'):
        if not data:
            return []
        if len(data) <= max_points:
            return data
        
        chunk_size = len(data) / max_points
        downsampled = []
        
        for i in range(max_points):
            start_index = int(i * chunk_size)
            end_index = int((i + 1) * chunk_size)
            chunk = data[start_index : end_index]
            
            if not chunk: # Should not happen mathematically but safe check
                continue
                
            if method == 'avg':
                val = sum(chunk) / len(chunk)
            elif method == 'max':
                val = max(chunk) # Useful for cumulative or peak detection
            else:
                val = chunk[-1] # Valid for cumulative counters
            
            downsampled.append(val)
            
        return downsampled
