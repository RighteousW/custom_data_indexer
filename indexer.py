"""
Custom Text Indexer with Trie-based Search and Persistence

A Python implementation of a text indexing system using a custom Trie (prefix tree)
data structure with persistent storage in both binary and JSON formats.

Author: Righteous Wasambo
License: MIT
"""

import pickle
import json
import os
import argparse


class TrieNode:
    """
    Node in the Trie data structure.
    
    Attributes:
        children (dict): Maps characters to child TrieNode objects
        occurrences (list): List of (filename, line_num, position, line_text) tuples
        is_end (bool): True if this node marks the end of a complete word
    """
    
    def __init__(self):
        self.children = {}
        self.occurrences = []  # [(filename, line_num, char_pos, line_text), ...]
        self.is_end = False


class Trie:
    """
    Trie (prefix tree) implementation for efficient word indexing and searching.
    
    Supports:
    - O(m) insertion where m is word length
    - O(m) exact search where m is word length
    - O(m + k) prefix search where k is number of matching words
    """
    
    def __init__(self):
        """Initialize empty Trie with root node."""
        self.root = TrieNode()
    
    def insert(self, word, filename, line_num, position, line_text):
        """
        Insert a word into the Trie with its location metadata.
        
        Args:
            word (str): Word to insert (should be lowercase, alphanumeric)
            filename (str): Name of file containing the word
            line_num (int): Line number where word appears
            position (int): Character position in line where word starts
            line_text (str): Complete text of the line
        
        Time Complexity: O(m) where m is length of word
        """
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
        node.occurrences.append((filename, line_num, position, line_text))
    
    def search_prefix(self, prefix):
        """
        Find all occurrences of words starting with the given prefix.
        
        Args:
            prefix (str): Prefix to search for
            
        Returns:
            list: List of (filename, line_num, position, line_text) tuples
            
        Time Complexity: O(m + k) where m is prefix length, k is number of results
        """
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        
        results = []
        self._collect_occurrences(node, results)
        return results
    
    def _collect_occurrences(self, node, results):
        """
        Recursively collect all occurrences from a given node.
        
        Args:
            node (TrieNode): Current node in traversal
            results (list): Accumulator for results
        """
        if node.is_end:
            results.extend(node.occurrences)
        
        for child in node.children.values():
            self._collect_occurrences(child, results)


class TextIndexer:
    """
    Main text indexing system using Trie for storage and retrieval.
    
    Features:
    - Indexes multiple text files with full context
    - Saves/loads index in binary (pickle) and JSON formats
    - Supports exact and prefix-based searching with context display
    """
    
    def __init__(self):
        """Initialize indexer with empty Trie."""
        self.index = Trie()
        self.indexed_files = set()
    
    def index_file(self, filename):
        """
        Read and index a text file.
        
        Args:
            filename (str): Path to text file to index
        """
        if not os.path.exists(filename):
            print(f"✗ File not found: {filename}")
            return
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line_text = line.rstrip('\n')
                    words_with_pos = self._extract_words(line_text)
                    
                    for word, position in words_with_pos:
                        self.index.insert(word, filename, line_num, position, line_text)
            
            self.indexed_files.add(filename)
            print(f"✓ Indexed file: {filename}")
        except Exception as e:
            print(f"✗ Error indexing {filename}: {e}")
    
    def _extract_words(self, text):
        """
        Extract words with their positions from text.
        
        Args:
            text (str): Text to extract words from
            
        Returns:
            list: List of (word, position) tuples
        """
        words = []
        current_word = ""
        word_start = -1
        
        for i, char in enumerate(text.lower()):
            if char.isalnum():
                if not current_word:
                    word_start = i
                current_word += char
            else:
                if current_word:
                    words.append((current_word, word_start))
                    current_word = ""
        
        if current_word:
            words.append((current_word, word_start))
        
        return words
    
    def search(self, query, chars_before=10, chars_after=20):
        """
        Search for a word or prefix in the index with context.
        
        Args:
            query (str): Word or prefix to search for
            chars_before (int): Characters to show before match (default: 10)
            chars_after (int): Characters to show after match (default: 20)
        """
        query = query.lower().strip()
        
        occurrences = self.index.search_prefix(query)
        
        if not occurrences:
            print(f"\n'{query}' not found in index")
            return
        
        print(f"\nFound {len(occurrences)} occurrence(s) of '{query}':\n")
        
        for idx, (filename, line_num, position, line_text) in enumerate(occurrences, 1):
            # Calculate context window
            start = max(0, position - chars_before)
            end = min(len(line_text), position + len(query) + chars_after)
            
            context = line_text[start:end]
            
            # Add ellipsis if truncated
            if start > 0:
                context = "..." + context
            if end < len(line_text):
                context = context + "..."
            
            print(f"{idx}. {filename}[line {line_num}] {context}")
    
    def save_binary(self, filename='index.bin'):
        """
        Save index to binary file using pickle.
        
        Args:
            filename (str): Output filename (default: 'index.bin')
        """
        try:
            data = {
                'trie': self.index,
                'indexed_files': list(self.indexed_files)
            }
            with open(filename, 'wb') as f:
                pickle.dump(data, f)
            print(f"✓ Saved binary index: {filename}")
        except Exception as e:
            print(f"✗ Error saving binary: {e}")
    
    def load_binary(self, filename='index.bin'):
        """
        Load index from binary file.
        
        Args:
            filename (str): Input filename (default: 'index.bin')
        
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            with open(filename, 'rb') as f:
                data = pickle.load(f)
            self.index = data['trie']
            self.indexed_files = set(data['indexed_files'])
            print(f"✓ Loaded binary index: {filename}")
            return True
        except FileNotFoundError:
            print(f"✗ Binary file not found: {filename}")
            return False
        except Exception as e:
            print(f"✗ Error loading binary: {e}")
            return False
    
    def save_json(self, filename='index.json'):
        """
        Save index to JSON file (human-readable).
        
        Args:
            filename (str): Output filename (default: 'index.json')
        """
        try:
            data = {
                'indexed_files': list(self.indexed_files),
                'index': self._trie_to_dict(self.index.root)
            }
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✓ Saved JSON index: {filename}")
        except Exception as e:
            print(f"✗ Error saving JSON: {e}")
    
    def _trie_to_dict(self, node):
        """
        Convert Trie to dictionary for JSON serialization.
        
        Args:
            node (TrieNode): Node to convert
            
        Returns:
            dict: Dictionary representation of node
        """
        result = {
            'is_end': node.is_end,
            'occurrences': node.occurrences,
            'children': {}
        }
        for char, child in node.children.items():
            result['children'][char] = self._trie_to_dict(child)
        return result


def interactive_mode(indexer):
    """
    Run interactive search interface.
    
    Args:
        indexer (TextIndexer): Indexer instance to use
    """
    print("\n" + "="*60)
    print("INTERACTIVE SEARCH MODE")
    print("="*60)
    print("Commands:")
    print("  search <query> [before] [after]  - Search with context")
    print("  index <filename>                 - Index a new file")
    print("  save                             - Save index")
    print("  load                             - Load index")
    print("  quit                             - Exit")
    print("\nExamples:")
    print("  search i lov")
    print("  search i lov 5 30")
    print("  index myfile.txt")

    while True:
        cmd = input("\n> ").strip()
        
        if cmd.lower() == 'quit':
            break
        elif cmd.lower().startswith('search '):
            parts = cmd[7:].split()
            if parts:
                query = parts[0]
                before = int(parts[1]) if len(parts) > 1 else 10
                after = int(parts[2]) if len(parts) > 2 else 20
                indexer.search(query, before, after)
        elif cmd.lower().startswith('index '):
            filename = cmd[6:].strip()
            indexer.index_file(filename)
        elif cmd.lower() == 'save':
            indexer.save_binary()
            indexer.save_json()
        elif cmd.lower() == 'load':
            indexer.load_binary()
        else:
            print("Invalid command. Type 'quit' to exit.")


def main():
    """
    Main entry point for the text indexer.
    
    Handles command-line arguments and executes appropriate actions.
    """
    parser = argparse.ArgumentParser(
        description='Custom Text Indexer - Index and search text files using a Trie data structure',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Index files and start interactive mode
  python3 indexer.py file1.txt file2.txt
  
  # Index files and search immediately
  python3 indexer.py file1.txt file2.txt --search "python"
  
  # Search with custom context
  python3 indexer.py --load --search "frie" --before 5 --after 30
  
  # Just load existing index and search
  python3 indexer.py --load --interactive
        """
    )
    
    parser.add_argument(
        'files',
        nargs='*',
        help='Text files to index'
    )
    
    parser.add_argument(
        '-s', '--search',
        type=str,
        help='Search query (prefix matching supported)'
    )
    
    parser.add_argument(
        '-b', '--before',
        type=int,
        default=10,
        help='Characters to show before match (default: 10)'
    )
    
    parser.add_argument(
        '-a', '--after',
        type=int,
        default=20,
        help='Characters to show after match (default: 20)'
    )
    
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Start interactive mode after indexing'
    )
    
    parser.add_argument(
        '-l', '--load',
        action='store_true',
        help='Load existing index from index.bin'
    )
    
    parser.add_argument(
        '--save',
        action='store_true',
        help='Save index after processing'
    )
    
    parser.add_argument(
        '--bin-file',
        type=str,
        default='index.bin',
        help='Binary index file (default: index.bin)'
    )
    
    parser.add_argument(
        '--json-file',
        type=str,
        default='index.json',
        help='JSON index file (default: index.json)'
    )
    
    args = parser.parse_args()
    
    # Initialize indexer
    indexer = TextIndexer()
    
    # Load existing index if requested
    if args.load:
        indexer.load_binary(args.bin_file)
    
    # Index new files
    if args.files:
        print("="*60)
        print("INDEXING FILES")
        print("="*60)
        for filename in args.files:
            indexer.index_file(filename)
    
    # Save if requested or if files were indexed
    if args.save or args.files:
        print("\n" + "="*60)
        print("SAVING INDEX")
        print("="*60)
        indexer.save_binary(args.bin_file)
        indexer.save_json(args.json_file)
    
    # Perform search if query provided
    if args.search:
        print("\n" + "="*60)
        print("SEARCH RESULTS")
        print("="*60)
        indexer.search(args.search, args.before, args.after)
    
    # Start interactive mode if requested or no other action
    if args.interactive or (not args.search and not args.files and not args.load):
        interactive_mode(indexer)
    
    # If nothing to do, show help
    if not args.files and not args.load and not args.search and not args.interactive:
        parser.print_help()


if __name__ == '__main__':
    main()