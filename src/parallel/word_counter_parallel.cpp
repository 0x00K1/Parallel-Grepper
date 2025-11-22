#include "word_counter_parallel.h"

#include <algorithm>
#include <cctype>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <omp.h>
#include <sstream>

WordCounterParallel::WordCounterParallel(SyncMethod mode)
    : executionTime(0.0), totalWords(0), uniqueWords(0), syncMethod(mode) {}

std::string WordCounterParallel::normalizeWord(const std::string& word) {
    std::string normalized;
    normalized.reserve(word.length());

    // Cannot parallelize: order-sensitive accumulation into a single string buffer.
    for (char c : word) {
        if (std::isalpha(static_cast<unsigned char>(c))) {
            normalized += std::tolower(static_cast<unsigned char>(c));
        }
    }

    return normalized;
}

bool WordCounterParallel::isValidChar(char c) {
    return std::isalpha(static_cast<unsigned char>(c));
}

WordCounterParallel::WordMap WordCounterParallel::countWords(const std::string& text) {
    auto startTime = std::chrono::high_resolution_clock::now();

    WordMap wordFreq;
    std::istringstream stream(text);
    std::string word;

    std::vector<std::string> rawWords;
    rawWords.reserve(text.size() / 5 + 1);

    // Cannot parallelize: std::istringstream provides no thread-safe random access.
    while (stream >> word) {
        rawWords.push_back(word);
    }

    wordFreq = buildWordMapFromList(rawWords);
    uniqueWords = wordFreq.size();

    auto endTime = std::chrono::high_resolution_clock::now();
    executionTime = std::chrono::duration<double, std::milli>(endTime - startTime).count();

    return wordFreq;
}

WordCounterParallel::WordMap WordCounterParallel::countWordsFromFile(const std::string& filename) {
    auto startTime = std::chrono::high_resolution_clock::now();

    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Error: Cannot open file " << filename << std::endl;
        executionTime = 0.0;
        return WordMap();
    }

    WordMap wordFreq;
    std::string word;
    std::vector<std::string> rawWords;

    // Cannot parallelize input extraction: std::ifstream >> word is inherently sequential.
    while (file >> word) {
        rawWords.push_back(word);
    }

    file.close();

    wordFreq = buildWordMapFromList(rawWords);
    uniqueWords = wordFreq.size();

    auto endTime = std::chrono::high_resolution_clock::now();
    executionTime = std::chrono::duration<double, std::milli>(endTime - startTime).count();
    // RACE CONDITION: shared variable updated with no synchronization


    return wordFreq;
}

std::vector<std::pair<std::string, unsigned long long>>
WordCounterParallel::getTopWords(const WordMap& wordMap, int n) {
    std::vector<std::pair<std::string, unsigned long long>> wordVec(wordMap.begin(), wordMap.end());

    // std::sort must remain sequential here to preserve deterministic ordering.
    std::sort(wordVec.begin(), wordVec.end(),
              [](const auto& a, const auto& b) { return a.second > b.second; });

    if (n > 0 && n < static_cast<int>(wordVec.size())) {
        wordVec.resize(n);
    }

    return wordVec;
}

void WordCounterParallel::saveResults(const WordMap& wordMap, const std::string& filename, int topN) {
    std::ofstream outFile(filename);
    if (!outFile.is_open()) {
        std::cerr << "Error: Cannot create output file " << filename << std::endl;
        return;
    }

    outFile << "Word Frequency Analysis Results\n";
    outFile << "================================\n";
    outFile << "Total Words: " << totalWords << "\n";
    outFile << "Unique Words: " << uniqueWords << "\n";
    outFile << "Execution Time: " << std::fixed << std::setprecision(2)
            << executionTime << " ms\n";
    outFile << "================================\n\n";

    auto sortedWords = getTopWords(wordMap, topN);

    outFile << std::left << std::setw(30) << "Word"
            << std::right << std::setw(15) << "Frequency" << "\n";
    outFile << std::string(45, '-') << "\n";

    // Cannot parallelize safely: writing to a single ostream must remain ordered.
    for (const auto& [w, freq] : sortedWords) {
        outFile << std::left << std::setw(30) << w << std::right << std::setw(15) << freq << "\n";
    }

    outFile.close();
    std::cout << "Results saved to: " << filename << std::endl;
}

WordCounterParallel::WordMap
WordCounterParallel::buildWordMapFromList(const std::vector<std::string>& rawWords) {
    WordMap wordFreq;
    totalWords = 0;

    if (rawWords.empty()) {
        return wordFreq;
    }

    unsigned long long totalWordCount = 0;

    if (syncMethod == SyncMethod::Reduction) {
#pragma omp parallel reduction(+ : totalWordCount)
    {
        WordMap localMap;

#pragma omp for schedule(static)
        for (int i = 0; i < static_cast<int>(rawWords.size()); ++i) {
            std::string normalized = normalizeWord(rawWords[static_cast<size_t>(i)]);
            if (!normalized.empty()) {
                localMap[normalized]++;
                // Update per-method: reduction aggregates this increment, atomic uses atomic, critical uses critical section
                totalWordCount++;
            }
        }

#pragma omp critical
        {
            for (const auto& entry : localMap) {
                // Merge: wordFreq is shared; merging must be synchronized to avoid data races on unordered_map
                wordFreq[entry.first] += entry.second;
            }
        }
    }
    }
    else {
#pragma omp parallel
    {
        WordMap localMap;

#pragma omp for schedule(static)
        for (int i = 0; i < static_cast<int>(rawWords.size()); ++i) {
            std::string normalized = normalizeWord(rawWords[static_cast<size_t>(i)]);
            if (!normalized.empty()) {
                localMap[normalized]++;
                if (syncMethod == SyncMethod::Atomic) {
#pragma omp atomic
                    totalWordCount++;
                } else { // Critical
#pragma omp critical
                    totalWordCount++;
                }
            }
        }

#pragma omp critical
        {
            for (const auto& entry : localMap) {
                wordFreq[entry.first] += entry.second;
            }
        }
    }
    }

    // Aggregation happens serially because std::unordered_map is not thread-safe.
    totalWords = totalWordCount;

    return wordFreq;
}