# Grid Painter (servicio gRPC)

Este proyecto expone el modelo **Grid Painter** a través de un servicio **gRPC**.

El modelo original simula un agente que debe pintar todas las celdas
de una cuadrícula (grid), comparando dos "cerebros":

- **REACTIVE** (`SimpleReactiveBrain`): se mueve a un vecino aleatorio,
  sin memoria.
- **MODEL_BASED** (`ModelBasedBrain`): planea una ruta en zigzag/serpiente
  con memoria, evitando revisitar celdas.

## Instalación

```bash
pip install -r requirements.txt
```

Si se necesita regenerar los stubs de gRPC a partir del `.proto`:

```bash
python -m grpc_tools.protoc \
  -I proto \
  --python_out=generated \
  --grpc_python_out=generated \
  proto/grid_painter.proto
```

## Ejecutar el servidor

```bash
python server.py 50051
```

## Probar con el cliente propio

En otra terminal, con el servidor corriendo:

```bash
python client.py localhost:50051
```

Salida esperada (ejemplo):

```
--- RunSimulation (REACTIVE) grid 6x6 ---
  steps         : 646
  painted_cells : 36/36
  completed     : True
  path (first 10 of 647): [(0, 0), (1, 0), ...]

--- RunSimulation (MODEL_BASED) grid 6x6 ---
  steps         : 35
  painted_cells : 36/36
  completed     : True
  path (first 10 of 36): [(0, 0), (0, 1), ...]

--- CompareAgents grid 6x6, 20 trials ---
  avg reactive steps    : 259.30
  avg model-based steps : 35.00
  improvement           : 86.5%
```