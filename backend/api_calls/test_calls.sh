#!/bin/bash

curl -X POST http://10.150.134.25:8000/move -H "Content-Type: application/json" -d '{"direction":"forward"}'