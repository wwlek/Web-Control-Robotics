#!/bin/bash

curl -X POST http://10.177.95.25:8000/move -H "Content-Type: application/json" -d '{"direction":"forward"}'