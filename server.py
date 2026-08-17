# Servidor gRPC que expone el modelo "Grid Painter"como un servicio remoto.

import sys
import os
import time
from concurrent import futures

import grpc

sys.path.append(os.path.join(os.path.dirname(__file__), "generated"))

import grid_painter_pb2
import grid_painter_pb2_grpc

from grid_painter_core import run_simulation, compare_agents


class GridPainterServicer(grid_painter_pb2_grpc.GridPainterServiceServicer):

    def RunSimulation(self, request, context):
        brain_type = "reactive" if request.brain_type == grid_painter_pb2.REACTIVE else "modelbased"

        rows = request.rows or 5
        cols = request.cols or 5
        max_steps = request.max_steps or 2000

        result = run_simulation(
            brain_type=brain_type,
            rows=rows,
            cols=cols,
            max_steps=max_steps,
            record_path=request.record_path,
        )

        response = grid_painter_pb2.SimulationResponse(
            steps=result["steps"],
            painted_cells=result["painted_cells"],
            total_cells=result["total_cells"],
            completed=result["completed"],
        )

        if request.record_path:
            for (r, c) in result["path"]:
                response.path.add(row=r, col=c)

        return response

    def CompareAgents(self, request, context):
        rows = request.rows or 5
        cols = request.cols or 5
        trials = request.trials or 20

        result = compare_agents(rows=rows, cols=cols, trials=trials)

        return grid_painter_pb2.CompareResponse(
            trials=result["trials"],
            avg_reactive_steps=result["avg_reactive_steps"],
            avg_modelbased_steps=result["avg_modelbased_steps"],
            improvement_pct=result["improvement_pct"],
        )


def serve(port=50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grid_painter_pb2_grpc.add_GridPainterServiceServicer_to_server(
        GridPainterServicer(), server
    )
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"GridPainter gRPC server escuchando en el puerto {port}...")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 50051
    serve(port)
