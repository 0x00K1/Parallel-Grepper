#include "word_counter_parallel.h"
#include <iostream>
#include <iomanip>
#include <omp.h>

/**
 * @brief Main driver program for parallel word counter
 *
 * Usage: parallel_counter <input_file> [output_file] [top_n] [num_threads]
 */
static WordCounterParallel::SyncMethod parseSyncMethod(const std::string& s) {
    if (s == "critical") return WordCounterParallel::SyncMethod::Critical;
    if (s == "atomic") return WordCounterParallel::SyncMethod::Atomic;
    // default
    return WordCounterParallel::SyncMethod::Reduction;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <input_file> [output_file] [top_n] [num_threads]\n";
        std::cerr << "Example: " << argv[0] << " data/test_10mb.txt results/output.txt 100 4\n";
        return 1;
    }

    std::string inputFile = argv[1];
    std::string outputFile = (argc > 2) ? argv[2] : "results/parallel/output.txt";
    int topN = (argc > 3) ? std::stoi(argv[3]) : 100;
    int numThreads = (argc > 4) ? std::stoi(argv[4]) : 0;
    std::string syncModeStr = (argc > 5) ? argv[5] : "reduction";
    auto mode = parseSyncMethod(syncModeStr);

    if (numThreads > 0) {
        omp_set_num_threads(numThreads);
    }

    std::cout << "===========================================\n";
    std::cout << "  Parallel Word Frequency Counter (OpenMP)\n";
    std::cout << "===========================================\n";
    std::cout << "Input File: " << inputFile << "\n";
    std::cout << "Output File: " << outputFile << "\n";
    std::cout << "Top N Words: " << topN << "\n";
    std::cout << "Threads: " << omp_get_max_threads() << "\n";
    std::cout << "Sync Mode: " << syncModeStr << "\n";
    std::cout << "-------------------------------------------\n";

    // Create word counter instance
    WordCounterParallel counter(mode);

    // Process file
    std::cout << "Processing file...\n";
    auto wordFreq = counter.countWordsFromFile(inputFile);

    if (wordFreq.empty()) {
        std::cerr << "Error: No words processed!\n";
        return 1;
    }

    // Display statistics
    std::cout << "\nStatistics:\n";
    std::cout << "-------------------------------------------\n";
    std::cout << "Total Words:     " << counter.getTotalWords() << "\n";
    std::cout << "Unique Words:    " << counter.getUniqueWords() << "\n";
    std::cout << "Execution Time:  " << std::fixed << std::setprecision(2)
              << counter.getExecutionTime() << " ms\n";
    std::cout << "                 " << std::fixed << std::setprecision(4)
              << counter.getExecutionTime() / 1000.0 << " seconds\n";

    // Display top words
    std::cout << "\nTop " << std::min(10, topN) << " Most Frequent Words:\n";
    std::cout << "-------------------------------------------\n";
    auto topWords = counter.getTopWords(wordFreq, 10);

    int rank = 1;
    for (const auto& [word, freq] : topWords) {
        std::cout << std::right << std::setw(3) << rank++ << ". "
                  << std::left << std::setw(20) << word
                  << std::right << std::setw(10) << freq << "\n";
    }

    // Save results
    std::cout << "\nSaving results...\n";
    counter.saveResults(wordFreq, outputFile, topN);

    std::cout << "\nProcessing complete!\n";
    std::cout << "===========================================\n";

    return 0;
}