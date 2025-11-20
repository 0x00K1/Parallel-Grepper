#!/bin/bash

# Build script for sequential word counter
# Usage: ./build.sh

echo "================================"
echo "Building Sequential Word Counter"
echo "================================"

# Create build directory
mkdir -p build
mkdir -p results/sequential
mkdir -p results/parallel

# Compile with optimizations
echo "Compiling..."
g++ -std=c++17 -O3 -march=native \
    -o build/sequential_counter \
    src/sequential/word_counter_sequential.cpp \
    src/sequential/main.cpp

if [ $? -eq 0 ]; then
    echo "Build successful!"
    echo "Executable: build/sequential_counter"
    echo ""
    echo "Run with: ./build/sequential_counter <input_file>"
else
    echo "Build failed!"
    exit 1
fi

echo "\nBuilding Parallel Word Counter"
echo "================================"
echo "Compiling parallel (OpenMP)..."
g++ -std=c++17 -O3 -march=native -fopenmp \
    -o build/parallel_counter \
    src/parallel/word_counter_parallel.cpp \
    src/parallel/main.cpp

if [ $? -eq 0 ]; then
    echo "Parallel build successful!"
    echo "Executable: build/parallel_counter"
    echo "Run with: ./build/parallel_counter <input_file> [output_file] [top_n] [threads]"
else
    echo "Parallel build failed!"
    exit 1
fi
