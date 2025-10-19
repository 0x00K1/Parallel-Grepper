"""
Dataset Generator for Word Frequency Counter Benchmarks
========================================================
Generates test datasets of various sizes with realistic text content.
"""

import random
import string
from pathlib import Path

class DatasetGenerator:
    def __init__(self, output_dir="data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Common English words for realistic text
        self.common_words = [
            "the", "be", "to", "of", "and", "a", "in", "that", "have", "I",
            "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
            "this", "but", "his", "by", "from", "they", "we", "say", "her", "she",
            "or", "an", "will", "my", "one", "all", "would", "there", "their", "what",
            "so", "up", "out", "if", "about", "who", "get", "which", "go", "me",
            "when", "make", "can", "like", "time", "no", "just", "him", "know", "take",
            "people", "into", "year", "your", "good", "some", "could", "them", "see", "other",
            "than", "then", "now", "look", "only", "come", "its", "over", "think", "also",
            "back", "after", "use", "two", "how", "our", "work", "first", "well", "way",
            "even", "new", "want", "because", "any", "these", "give", "day", "most", "us",
            # Technical words for variety
            "data", "system", "process", "computer", "program", "algorithm", "function",
            "variable", "code", "memory", "processor", "parallel", "thread", "execution",
            "performance", "optimization", "analysis", "result", "test", "benchmark"
        ]
        
        # Less common words (appear less frequently)
        self.uncommon_words = [
            "serendipity", "ephemeral", "paradigm", "quintessential", "ubiquitous",
            "ambiguous", "coherent", "intricate", "meticulous", "pragmatic",
            "resilient", "substantial", "versatile", "anomaly", "criterion",
            "hierarchy", "infrastructure", "methodology", "phenomenon", "protocol"
        ]
    
    def generate_realistic_text(self, target_size_mb):
        """Generate realistic text with word frequency distribution"""
        target_size = target_size_mb * 1024 * 1024
        current_size = 0
        text_parts = []
        
        print(f"  Generating {target_size_mb} MB of text...")
        
        while current_size < target_size:
            # Generate a paragraph (10-50 words)
            paragraph_length = random.randint(10, 50)
            words = []
            
            for _ in range(paragraph_length):
                # 90% common words, 10% uncommon words (Zipf-like distribution)
                if random.random() < 0.9:
                    word = random.choice(self.common_words)
                else:
                    word = random.choice(self.uncommon_words)
                
                # Occasionally capitalize (proper nouns)
                if random.random() < 0.1:
                    word = word.capitalize()
                
                words.append(word)
            
            # Add some punctuation
            paragraph = ' '.join(words)
            if random.random() < 0.7:
                paragraph += '.'
            elif random.random() < 0.5:
                paragraph += '!'
            else:
                paragraph += '?'
            
            paragraph += '\n'
            
            text_parts.append(paragraph)
            current_size += len(paragraph.encode('utf-8'))
            
            # Progress indicator
            if len(text_parts) % 1000 == 0:
                progress = (current_size / target_size) * 100
                print(f"    Progress: {progress:.1f}%", end='\r')
        
        print(f"    Progress: 100.0%")
        return ''.join(text_parts)
    
    def generate_dataset(self, size_mb, filename=None):
        """Generate a single dataset file"""
        if filename is None:
            filename = f"test_{size_mb}mb.txt"
        
        output_path = self.output_dir / filename
        
        print(f"\nGenerating: {filename}")
        print(f"   Target size: {size_mb} MB")
        
        text = self.generate_realistic_text(size_mb)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        # Verify size
        actual_size = output_path.stat().st_size / (1024 * 1024)
        print(f"   Actual size: {actual_size:.2f} MB")
        print(f"   Saved to: {output_path}")
        
        return output_path
    
    def generate_all_datasets(self):
        """Generate standard test datasets"""
        sizes = [10, 25, 50, 100]
        
        print("\n" + "="*60)
        print("  DATASET GENERATOR")
        print("="*60)
        print(f"Output directory: {self.output_dir}")
        print(f"Datasets to generate: {sizes} MB")
        print("="*60)
        
        generated_files = []
        
        for size in sizes:
            try:
                output_path = self.generate_dataset(size)
                generated_files.append(output_path)
            except Exception as e:
                print(f"   Error generating {size}MB dataset: {e}")
        
        print("\n" + "="*60)
        print(f"Generated {len(generated_files)} datasets")
        print("="*60)
        
        return generated_files

def main():
    print("\nStarting Dataset Generation...")
    
    generator = DatasetGenerator()
    generator.generate_all_datasets()
    
    print("\nDataset generation complete!")
    print("   You can now run benchmarks with: python run_benchmarks.py")

if __name__ == "__main__":
    main()
