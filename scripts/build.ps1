# Build script for Windows PowerShell
# Usage: .\build.ps1

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Building Sequential Word Counter" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Create directories
New-Item -ItemType Directory -Force -Path build | Out-Null
New-Item -ItemType Directory -Force -Path results\sequential | Out-Null

# Compile
Write-Host "Compiling..." -ForegroundColor Yellow
g++ -std=c++17 -O3 -o build/sequential_counter.exe `
    src/sequential/word_counter_sequential.cpp `
    src/sequential/main.cpp

if ($LASTEXITCODE -eq 0) {
    Write-Host "Build successful!" -ForegroundColor Green
    Write-Host "Executable: build\sequential_counter.exe" -ForegroundColor Green
    Write-Host ""
    Write-Host "Run with: .\build\sequential_counter.exe <input_file>" -ForegroundColor Cyan
} else {
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}
