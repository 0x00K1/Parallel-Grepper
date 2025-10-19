# 🔨 Build Guide - Parallel Word Frequency Counter

This guide provides detailed instructions for building both sequential and parallel versions of the word frequency counter on different platforms.

---

## Prerequisites

- **C++ Compiler:** GCC 15.2.0+ with OpenMP support
  - Windows: MinGW-w64 (WinLibs POSIX UCRT)
  - Linux: GCC via package manager
  - macOS: GCC via Homebrew
- **Python 3.8+** for benchmarking and analysis

#### Python Packages
```bash
pip install pandas matplotlib seaborn numpy
```

Or use the requirements file:
```bash
pip install -r benchmarks/requirements.txt
```

### Platform-Specific Setup

#### 🪟 Windows

**Option 1: Install via WinGet (Recommended)**
```powershell
# Install MinGW-w64 (WinLibs POSIX UCRT)
winget install BrechtSanders.WinLibs.POSIX.UCRT

# Verify installation
g++ --version
# Expected output: g++ (MinGW-W64 ... GCC-15.2.0) 15.2.0

# Check OpenMP support
g++ -fopenmp -dM -E - < nul | findstr OPENMP
```

**Option 2: Manual Installation**
1. Download MinGW-w64 from [WinLibs](https://winlibs.com/)
2. Extract to `C:\mingw64`
3. Add `C:\mingw64\bin` to PATH:
   ```powershell
   $env:PATH += ";C:\mingw64\bin"
   ```

**Verify PATH Configuration:**
```powershell
# Check if g++ is accessible
where.exe g++

# Add to PATH permanently (if needed)
[Environment]::SetEnvironmentVariable(
    "Path",
    [Environment]::GetEnvironmentVariable("Path", "User") + ";C:\mingw64\bin",
    "User"
)
```

#### 🐧 Linux (Ubuntu/Debian)

```bash
# Update package list
sudo apt update

# Install GCC and build tools
sudo apt install g++ build-essential

# Verify installation
g++ --version
gcc --version

# Check OpenMP support
echo | g++ -fopenmp -dM -E - | grep -i openmp
```

#### 🍎 macOS

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install GCC (includes OpenMP)
brew install gcc

# The compiler will be named gcc-13 (or similar)
gcc-13 --version

# Create symlink (optional)
ln -s /usr/local/bin/gcc-13 /usr/local/bin/g++
```

---

## Building Sequential Version

#### 🪟 **Windows (PowerShell)**

Use the provided build script:
```powershell
# Build using script
.\scripts\build.ps1

# Or compile manually
g++ -std=c++17 -O3 -o build/sequential_counter.exe `
    src/sequential/word_counter_sequential.cpp `
    src/sequential/main.cpp

# Run the program
.\build\sequential_counter.exe data\test_10mb.txt
```

#### 🐧/🍎 **Linux / macOS (Bash)**

Use the provided build script:
```bash
# Make script executable (first time only)
chmod +x scripts/build.sh

# Build using script
./scripts/build.sh

# Or compile manually
g++ -std=c++17 -O3 -o build/sequential_counter \
    src/sequential/word_counter_sequential.cpp \
    src/sequential/main.cpp

# Run the program
./build/sequential_counter data/test_10mb.txt
```

### Generate test datasets

```bash
pip install -r benchmarks/requirements.txt
python benchmarks/generate_dataset.py
```

### Running Benchmarks

```bash
python benchmarks/run_benchmarks.py
```

### Analyze Results

```bash
python benchmarks/analyze_results.py
```

---

## Building Parallel Version

> **Status:** Coming Soon

### External Links
- [OpenMP Documentation](https://www.openmp.org/specifications/)
- [MinGW-w64 (WinLibs)](https://winlibs.com/)
- [GCC Manual](https://gcc.gnu.org/onlinedocs/)
- [C++17 Reference](https://en.cppreference.com/w/cpp/17)