#ifndef WORD_COUNTER_PARALLEL_H
#define WORD_COUNTER_PARALLEL_H

#include <string>
#include <unordered_map>
#include <vector>
#include <chrono>

/**
 * @brief OpenMP-based parallel word frequency counter.
 */
class WordCounterParallel {
public:
    using WordMap = std::unordered_map<std::string, unsigned long long>;

    // Enum to select synchronization method for shared counters
    enum class SyncMethod { Critical, Atomic, Reduction };
    explicit WordCounterParallel(SyncMethod mode = SyncMethod::Reduction);

    WordMap countWordsFromFile(const std::string& filename);
    WordMap countWords(const std::string& text);

    std::vector<std::pair<std::string, unsigned long long>>
        getTopWords(const WordMap& wordMap, int n);

    void saveResults(const WordMap& wordMap, const std::string& filename, int topN = 0);

    double getExecutionTime() const { return executionTime; }
    unsigned long long getTotalWords() const { return totalWords; }
    size_t getUniqueWords() const { return uniqueWords; }

private:
    double executionTime;
    unsigned long long totalWords;
    size_t uniqueWords;
    SyncMethod syncMethod = SyncMethod::Reduction;

    std::string normalizeWord(const std::string& word);
    bool isValidChar(char c);

    WordMap buildWordMapFromList(const std::vector<std::string>& rawWords);
};

#endif // WORD_COUNTER_PARALLEL_H