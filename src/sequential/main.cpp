#include "word_counter_sequential.h"
#include <iostream>
#include <iomanip>

/**
 * @brief Main driver program for sequential word counter
 * 
 * Usage: sequential_counter <input_file> [output_file] [top_n]
 */
int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <input_file> [output_file] [top_n]\n";
        std::cerr << "Example: " << argv[0] << " data/test_10mb.txt results/output.txt 100\n";
        return 1;
    }
    
    std::string inputFile = argv[1];
    std::string outputFile = (argc > 2) ? argv[2] : "results/sequential/output.txt";
    int topN = (argc > 3) ? std::stoi(argv[3]) : 100;
    
    std::cout << "===========================================\n";
    std::cout << "  Sequential Word Frequency Counter\n";
    std::cout << "===========================================\n";
    std::cout << "Input File: " << inputFile << "\n";
    std::cout << "Output File: " << outputFile << "\n";
    std::cout << "Top N Words: " << topN << "\n";
    std::cout << "-------------------------------------------\n";
    
    // Create word counter instance
    WordCounterSequential counter;
    
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
