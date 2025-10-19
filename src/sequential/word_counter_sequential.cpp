#include "word_counter_sequential.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <algorithm>
#include <cctype>
#include <iomanip>

WordCounterSequential::WordCounterSequential() 
    : executionTime(0.0), totalWords(0), uniqueWords(0) {
}

std::string WordCounterSequential::normalizeWord(const std::string& word) {
    std::string normalized;
    normalized.reserve(word.length());
    
    // Convert to lowercase and remove non-alphabetic characters
    for (char c : word) {
        if (std::isalpha(static_cast<unsigned char>(c))) {
            normalized += std::tolower(static_cast<unsigned char>(c));
        }
    }
    
    return normalized;
}

bool WordCounterSequential::isValidChar(char c) {
    return std::isalpha(static_cast<unsigned char>(c));
}

WordCounterSequential::WordMap WordCounterSequential::countWords(const std::string& text) {
    auto startTime = std::chrono::high_resolution_clock::now();
    
    WordMap wordFreq;
    std::istringstream stream(text);
    std::string word;
    totalWords = 0;
    
    // Process each word in the text
    while (stream >> word) {
        std::string normalized = normalizeWord(word);
        
        if (!normalized.empty()) {
            wordFreq[normalized]++;
            totalWords++;
        }
    }
    
    uniqueWords = wordFreq.size();
    
    auto endTime = std::chrono::high_resolution_clock::now();
    executionTime = std::chrono::duration<double, std::milli>(endTime - startTime).count();
    
    return wordFreq;
}

WordCounterSequential::WordMap WordCounterSequential::countWordsFromFile(const std::string& filename) {
    auto startTime = std::chrono::high_resolution_clock::now();
    
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Error: Cannot open file " << filename << std::endl;
        executionTime = 0.0;
        return WordMap();
    }
    
    WordMap wordFreq;
    std::string word;
    totalWords = 0;
    
    // Read file word by word for memory efficiency
    while (file >> word) {
        std::string normalized = normalizeWord(word);
        
        if (!normalized.empty()) {
            wordFreq[normalized]++;
            totalWords++;
        }
    }
    
    file.close();
    uniqueWords = wordFreq.size();
    
    auto endTime = std::chrono::high_resolution_clock::now();
    executionTime = std::chrono::duration<double, std::milli>(endTime - startTime).count();
    
    return wordFreq;
}

std::vector<std::pair<std::string, unsigned long long>> 
WordCounterSequential::getTopWords(const WordMap& wordMap, int n) {
    // Convert map to vector for sorting
    std::vector<std::pair<std::string, unsigned long long>> wordVec(
        wordMap.begin(), wordMap.end()
    );
    
    // Sort by frequency (descending)
    std::sort(wordVec.begin(), wordVec.end(),
        [](const auto& a, const auto& b) {
            return a.second > b.second;
        }
    );
    
    // Return top N words
    if (n > 0 && n < static_cast<int>(wordVec.size())) {
        wordVec.resize(n);
    }
    
    return wordVec;
}

void WordCounterSequential::saveResults(const WordMap& wordMap, 
                                       const std::string& filename, 
                                       int topN) {
    std::ofstream outFile(filename);
    if (!outFile.is_open()) {
        std::cerr << "Error: Cannot create output file " << filename << std::endl;
        return;
    }
    
    // Write header
    outFile << "Word Frequency Analysis Results\n";
    outFile << "================================\n";
    outFile << "Total Words: " << totalWords << "\n";
    outFile << "Unique Words: " << uniqueWords << "\n";
    outFile << "Execution Time: " << std::fixed << std::setprecision(2) 
            << executionTime << " ms\n";
    outFile << "================================\n\n";
    
    // Get sorted words
    auto sortedWords = getTopWords(wordMap, topN);
    
    outFile << std::left << std::setw(30) << "Word" 
            << std::right << std::setw(15) << "Frequency" << "\n";
    outFile << std::string(45, '-') << "\n";
    
    for (const auto& [word, freq] : sortedWords) {
        outFile << std::left << std::setw(30) << word 
                << std::right << std::setw(15) << freq << "\n";
    }
    
    outFile.close();
    std::cout << "Results saved to: " << filename << std::endl;
}
