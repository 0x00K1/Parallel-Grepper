#ifndef WORD_COUNTER_SEQUENTIAL_H
#define WORD_COUNTER_SEQUENTIAL_H

#include <string>
#include <unordered_map>
#include <vector>
#include <chrono>

/**
 * @brief Sequential Word Frequency Counter
 * 
 * This class implements a sequential algorithm for counting word frequencies
 * in large text files. It serves as the baseline for parallel implementation.
 */
class WordCounterSequential {
public:
    using WordMap = std::unordered_map<std::string, unsigned long long>;
    
    /**
     * @brief Construct a new Word Counter Sequential object
     */
    WordCounterSequential();
    
    /**
     * @brief Process a text file and count word frequencies
     * @param filename Path to the input text file
     * @return WordMap containing word frequencies
     */
    WordMap countWordsFromFile(const std::string& filename);
    
    /**
     * @brief Process text content and count word frequencies
     * @param text Input text string
     * @return WordMap containing word frequencies
     */
    WordMap countWords(const std::string& text);
    
    /**
     * @brief Get the top N most frequent words
     * @param wordMap Word frequency map
     * @param n Number of top words to return
     * @return Vector of pairs (word, frequency) sorted by frequency
     */
    std::vector<std::pair<std::string, unsigned long long>> 
        getTopWords(const WordMap& wordMap, int n);
    
    /**
     * @brief Save word frequencies to a file
     * @param wordMap Word frequency map
     * @param filename Output file path
     * @param topN Only save top N words (0 = save all)
     */
    void saveResults(const WordMap& wordMap, const std::string& filename, int topN = 0);
    
    /**
     * @brief Get the last execution time in milliseconds
     * @return Execution time
     */
    double getExecutionTime() const { return executionTime; }
    
    /**
     * @brief Get total word count
     * @return Total number of words processed
     */
    unsigned long long getTotalWords() const { return totalWords; }
    
    /**
     * @brief Get unique word count
     * @return Number of unique words
     */
    size_t getUniqueWords() const { return uniqueWords; }

private:
    double executionTime;           // Last execution time in milliseconds
    unsigned long long totalWords;  // Total word count
    size_t uniqueWords;             // Unique word count
    
    /**
     * @brief Normalize a word (lowercase, remove punctuation)
     * @param word Input word
     * @return Normalized word
     */
    std::string normalizeWord(const std::string& word);
    
    /**
     * @brief Check if character is valid for word
     * @param c Character to check
     * @return true if valid
     */
    bool isValidChar(char c);
};

#endif // WORD_COUNTER_SEQUENTIAL_H
