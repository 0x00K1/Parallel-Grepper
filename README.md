# Parallel Text Processing and Word Frequency Counter

## 🎯 Project Overview

This project implements a parallel word frequency counter using OpenMP to demonstrate performance improvements in large-scale text processing. We compare sequential and parallel implementations across various dataset sizes and thread configurations.

---

## 📁 Project Structure

```
parallel-grepper/
├── docs/                          # Documentation and proposal
├── src/
│   ├── sequential/               # Sequential implementation
│   └── parallel/                 # Parallel implementation (OpenMP)
├── benchmarks/                   # Benchmarking scripts and results
├── data/                         # Test datasets (10MB to 100MB+)
├── scripts/                      # Utility scripts
└── results/                      # Output word frequency results
```

## 🚀 Quick Start

### Prerequisites

- **C++ Compiler:** GCC 15.2.0+ with OpenMP support
  - Windows: MinGW-w64 (WinLibs POSIX UCRT)
  - Linux: GCC via package manager
  - macOS: GCC via Homebrew
- **Python 3.8+** for benchmarking and analysis

### [Building Sequential Version](docs/BUILD_GUIDE.md#building-sequential-version)

---

### [Building Parallel Version](docs/BUILD_GUIDE.md#building-parallel-version) 

---

## 📄 License

This project is developed for educational purposes as part of ARTI503 coursework.