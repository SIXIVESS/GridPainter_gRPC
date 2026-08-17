# Grid Painter — servicio gRPC

Este proyecto expone el modelo **Grid Painter** (tomado del notebook
`Grid_Painter.ipynb`) a través de un servicio **gRPC**, tal como se
pidió en la asignación.

El modelo original simula un agente que debe pintar todas las celdas
de una cuadrícula (grid), comparando dos "cerebros":

- **REACTIVE** (`SimpleReactiveBrain`): se mueve a un vecino aleatorio,
  sin memoria.
- **MODEL_BASED** (`ModelBasedBrain`): planea una ruta en zigzag/serpiente
  con memoria, evitando revisitar celdas.

## Estructura del proyecto

```
grid_painter_grpc/
├── grid_painter_core.py        # Lógica original del modelo (del notebook)
├── proto/
│   └── grid_painter.proto      # Definición del servicio gRPC
├── generated/                  # Código generado por protoc (stubs)
│   ├── grid_painter_pb2.py
│   └── grid_painter_pb2_grpc.py
├── server.py                   # Servidor gRPC
├── client.py                   # Cliente de prueba
└── requirements.txt
```

## Servicio expuesto (`grid_painter.proto`)

```protobuf
service GridPainterService {
  rpc RunSimulation (SimulationRequest) returns (SimulationResponse);
  rpc CompareAgents (CompareRequest) returns (CompareResponse);
}
```

- **RunSimulation**: ejecuta una simulación completa con el tipo de
  agente indicado (`REACTIVE` o `MODEL_BASED`), tamaño de grid
  (`rows` x `cols`), un límite de pasos (`max_steps`) y, opcionalmente,
  retorna el recorrido completo (`record_path`).
- **CompareAgents**: ejecuta ambos agentes N veces (`trials`) y
  retorna el promedio de pasos de cada uno junto al % de mejora del
  agente basado en modelo respecto al reactivo.

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
python3 server.py 50051
```

Esto levanta el servidor gRPC en `localhost:50051` (el puerto es
opcional, por defecto es `50051`).

## Probar con el cliente propio

En otra terminal, con el servidor corriendo:

```bash
python3 client.py localhost:50051
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

## Probar con Postman

Postman soporta gRPC de forma nativa desde la versión 9+:

1. Abrir Postman → **New** → **gRPC Request**.
2. En la URL del servidor, escribir `localhost:50051` (usar
   conexión **sin TLS / Plaintext**, ya que el servidor usa
   `add_insecure_port`).
3. Importar la definición del servicio: **Select a .proto file** o
   **Import a .proto** y seleccionar `proto/grid_painter.proto`
   (o usar Server Reflection si se habilita).
4. Elegir el método `GridPainterService/RunSimulation` o
   `GridPainterService/CompareAgents`.
5. En el body, enviar el mensaje en JSON, por ejemplo:

```json
{
  "brain_type": "MODEL_BASED",
  "rows": 6,
  "cols": 6,
  "max_steps": 2000,
  "record_path": true
}
```

para `RunSimulation`, o

```json
{
  "rows": 6,
  "cols": 6,
  "trials": 20
}
```

para `CompareAgents`.

6. Presionar **Invoke** y revisar la respuesta.

> Nota: también se puede usar `grpcurl` como alternativa de línea de
> comandos:
> ```bash
> grpcurl -plaintext -import-path proto -proto grid_painter.proto \
>   -d '{"brain_type":"MODEL_BASED","rows":6,"cols":6,"max_steps":2000,"record_path":true}' \
>   localhost:50051 gridpainter.GridPainterService/RunSimulation
> ```
