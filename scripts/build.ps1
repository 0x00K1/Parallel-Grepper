# Build script for Windows PowerShell
# Usage: .\build.ps1

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Building Sequential Word Counter" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Create directories
New-Item -ItemType Directory -Force -Path build | Out-Null
New-Item -ItemType Directory -Force -Path results\sequential | Out-Null
New-Item -ItemType Directory -Force -Path results\parallel | Out-Null

# Compile
Write-Host "Compiling..." -ForegroundColor Yellow
g++ -std=c++17 -O3 -o build/sequential_counter.exe `
    src/sequential/word_counter_sequential.cpp `
    src/sequential/main.cpp

Write-Host "\nBuilding Parallel Word Counter" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Compiling parallel (OpenMP)..." -ForegroundColor Yellow
g++ -std=c++17 -O3 -fopenmp -o build/parallel_counter.exe `
    src/parallel/word_counter_parallel.cpp `
    src/parallel/main.cpp

if ($LASTEXITCODE -eq 0) {
    Write-Host "Parallel build successful!" -ForegroundColor Green
    Write-Host "Executable: build\parallel_counter.exe" -ForegroundColor Green
    Write-Host "Run with: .\build\parallel_counter.exe <input_file> [output_file] [top_n] [threads]" -ForegroundColor Cyan
} else {
    Write-Host "Parallel build failed!" -ForegroundColor Red
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "Build successful!" -ForegroundColor Green
    Write-Host "Executable: build\sequential_counter.exe" -ForegroundColor Green
    Write-Host ""
    Write-Host "Run with: .\build\sequential_counter.exe <input_file>" -ForegroundColor Cyan
} else {
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}
