"""
Este modulo contiene la logica "Grid Painter", tomada de
una clase (Intelligent Systems) sin modificaciones de
comportamiento.

Un agente pintor debe pintar TODAS las celdas de una cuadricula (grid)
caminando por ella. Se implementan dos "cerebros" (brains):
  - SimpleReactiveBrain: se mueve aleatoriamente (sin memoria).
  - ModelBasedBrain: planea una ruta en zigzag/serpiente para evitar
    revisitar celdas (con memoria).
"""

import random


class GridEnvironment:
    def __init__(self, rows=5, cols=5):
        self.rows = rows
        self.cols = cols
        # False = sin pintar, True = pintada
        self.grid = [[False] * cols for _ in range(rows)]
        # El agente inicia en la esquina superior izquierda
        self.agent_pos = (0, 0)
        # Se pinta la celda inicial de inmediato
        self.grid[0][0] = True
        self.steps = 0

    def is_complete(self):
        #Retorna True cuando todas las celdas han sido pintadas
        return all(self.grid[r][c]
                   for r in range(self.rows)
                   for c in range(self.cols))

    def total_cells(self):
        return self.rows * self.cols

    def painted_cells(self):
        return sum(self.grid[r][c]
                   for r in range(self.rows)
                   for c in range(self.cols))

    def display(self):
        #Imprime la cuadricula. Agente = 'A', pintada = '#', vacia = '.'
        ar, ac = self.agent_pos
        lines = [f"Step {self.steps} | Painted: {self.painted_cells()}/{self.total_cells()}"]
        for r in range(self.rows):
            row_str = ""
            for c in range(self.cols):
                if (r, c) == (ar, ac):
                    row_str += " A "
                elif self.grid[r][c]:
                    row_str += " # "
                else:
                    row_str += " . "
            lines.append(row_str)
        return "\n".join(lines)


class Sensor:
    def __init__(self, environment):
        self.env = environment

    def perceive(self):
        #Retorna una instantanea de lo que el agente percibe actualmente:
        #position: (row, col) del agente
        #neighbors: lista de celdas adyacentes validas
  
        row, col = self.env.agent_pos
        neighbors = self._get_neighbors(row, col)
        return {
            "position": (row, col),
            "neighbors": neighbors
        }

    def _get_neighbors(self, row, col):
        #Retorna las celdas adyacentes validas incluyendo diagonales
        candidates = [
            (row - 1, col),      # arriba
            (row + 1, col),      # abajo
            (row,     col - 1),  # izquierda
            (row,     col + 1),  # derecha
            (row - 1, col - 1),  # arriba-izquierda (diagonal)
            (row - 1, col + 1),  # arriba-derecha  (diagonal)
            (row + 1, col - 1),  # abajo-izquierda (diagonal)
            (row + 1, col + 1),  # abajo-derecha   (diagonal)
        ]
        return [
            (r, c) for r, c in candidates
            if 0 <= r < self.env.rows and 0 <= c < self.env.cols
        ]


class Actuator:
    def __init__(self, environment):
        self.env = environment

    def move_to(self, new_pos):
        #Mueve al agente a new_pos y pinta esa celda
        self.env.agent_pos = new_pos
        r, c = new_pos
        self.env.grid[r][c] = True
        self.env.steps += 1


class SimpleReactiveBrain:
    #Toma decisiones basandose unicamente en la percepcion actual (sin memoria).
    def __init__(self, sensor, actuator):
        self.sensor = sensor
        self.actuator = actuator

    def decide_and_act(self):
        perception = self.sensor.perceive()
        neighbors = perception["neighbors"]

        if neighbors:
            chosen = random.choice(neighbors)
            self.actuator.move_to(chosen)


class ModelBasedBrain:
    #Mantiene un estado interno (memoria) para tomar mejores decisiones.
    #Construye una ruta en zigzag/serpiente que cubre toda la cuadricula.

    def __init__(self, sensor, actuator, environment):
        self.sensor = sensor
        self.actuator = actuator
        self.env = environment

        # Se construye la ruta una sola vez al inicio
        self.route = self._build_snake_route(environment.rows, environment.cols)
        self.index = 1

    def _build_snake_route(self, rows, cols):
        #Construye y retorna una ruta en zigzag que cubre toda la
        #cuadricula exactamente una vez
        route = []
        for r in range(rows):
            if r % 2 == 0:
                cols_order = range(cols)
            else:
                cols_order = range(cols - 1, -1, -1)
            for c in cols_order:
                route.append((r, c))
        return route

    def decide_and_act(self):
        if self.index >= len(self.route):
            return

        next_cell = self.route[self.index]
        perception = self.sensor.perceive()
        neighbors = perception["neighbors"]

        if next_cell in neighbors:
            self.actuator.move_to(next_cell)
            self.index += 1


def run_simulation(brain_type="reactive", rows=5, cols=5, max_steps=2000,
                    record_path=False):
  
    #Ejecuta un episodio completo hasta que la cuadricula este completamente
    #pintada (o se alcance max_steps)
    env = GridEnvironment(rows, cols)
    sensor = Sensor(env)
    actuator = Actuator(env)

    if brain_type == "reactive":
        brain = SimpleReactiveBrain(sensor, actuator)
    else:
        brain = ModelBasedBrain(sensor, actuator, env)

    path = [env.agent_pos] if record_path else None

    while not env.is_complete() and env.steps < max_steps:
        brain.decide_and_act()
        if record_path:
            path.append(env.agent_pos)

    return {
        "steps": env.steps,
        "painted_cells": env.painted_cells(),
        "total_cells": env.total_cells(),
        "completed": env.is_complete(),
        "path": path if record_path else [],
    }


def compare_agents(rows=5, cols=5, trials=20):
    reactive_steps = []
    modelbased_steps = []

    for _ in range(trials):
        result = run_simulation("reactive", rows, cols, max_steps=10000)
        reactive_steps.append(result["steps"])

        result = run_simulation("modelbased", rows, cols, max_steps=10000)
        modelbased_steps.append(result["steps"])

    avg_r = sum(reactive_steps) / len(reactive_steps)
    avg_m = sum(modelbased_steps) / len(modelbased_steps)
    pct = ((avg_r - avg_m) / avg_r) * 100 if avg_r else 0.0

    return {
        "trials": trials,
        "avg_reactive_steps": avg_r,
        "avg_modelbased_steps": avg_m,
        "improvement_pct": pct,
    }
