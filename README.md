# Scavenger hunt 
Build for TenneT - BTO - DD - Advanced Analytics - offsite November 2024

## Build container
```bash
docker build --platform=linux/amd64 -t scavenger-hunt --progress=plain .
```

## Run locally
```bash
docker run --rm -p 8501:8501 -p 8502:8502 scavenger-hunt
```
