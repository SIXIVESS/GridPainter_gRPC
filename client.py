#Cliente de prueba para el servicio gRPC GridPainterService.


import sys
import os

import grpc

sys.path.append(os.path.join(os.path.dirname(__file__), "generated"))

import grid_painter_pb2
import grid_painter_pb2_grpc


def run_simulation_demo(stub, brain_type, rows=6, cols=6, record_path=False):
    label = "REACTIVE" if brain_type == grid_painter_pb2.REACTIVE else "MODEL_BASED"
    request = grid_painter_pb2.SimulationRequest(
        brain_type=brain_type,
        rows=rows,
        cols=cols,
        max_steps=2000,
        record_path=record_path,
    )
    response = stub.RunSimulation(request)

    print(f"\n--- RunSimulation ({label}) grid {rows}x{cols} ---")
    print(f"  steps         : {response.steps}")
    print(f"  painted_cells : {response.painted_cells}/{response.total_cells}")
    print(f"  completed     : {response.completed}")
    if record_path:
        path_preview = [(p.row, p.col) for p in response.path[:10]]
        print(f"  path (first 10 of {len(response.path)}): {path_preview}")


def compare_agents_demo(stub, rows=6, cols=6, trials=20):
    request = grid_painter_pb2.CompareRequest(rows=rows, cols=cols, trials=trials)
    response = stub.CompareAgents(request)

    print(f"\n--- CompareAgents grid {rows}x{cols}, {trials} trials ---")
    print(f"  avg reactive steps    : {response.avg_reactive_steps:.2f}")
    print(f"  avg model-based steps : {response.avg_modelbased_steps:.2f}")
    print(f"  improvement           : {response.improvement_pct:.1f}%")


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "localhost:50051"

    with grpc.insecure_channel(target) as channel:
        stub = grid_painter_pb2_grpc.GridPainterServiceStub(channel)

        run_simulation_demo(stub, grid_painter_pb2.REACTIVE, rows=6, cols=6, record_path=True)
        run_simulation_demo(stub, grid_painter_pb2.MODEL_BASED, rows=6, cols=6, record_path=True)
        compare_agents_demo(stub, rows=6, cols=6, trials=20)


if __name__ == "__main__":
    main()
