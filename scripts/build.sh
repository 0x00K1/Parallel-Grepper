#!/bin/bash

# Build script for sequential word counter
# Usage: ./build.sh

echo "================================"
echo "Building Sequential Word Counter"
echo "================================"

# Create build directory
mkdir -p build
mkdir -p results/sequential

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
