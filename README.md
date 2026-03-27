# Custom Text Indexer

A Python implementation of a text indexing system using a custom-built Trie (prefix tree) data structure. This project demonstrates fundamental data structure concepts without relying on built-in indexing libraries.

## Features

- **Custom Trie Implementation** - Built from scratch without using Python's built-in dict indexing
- **Multiple File Support** - Index and search across multiple text files
- **Exact & Prefix Search** - Find complete word matches or search with incomplete words
- **Context Display** - Shows surrounding text for each match (customizable)
- **Persistent Storage** - Save/load index in both binary (pickle) and JSON formats
- **CLI & Interactive Modes** - Use via command-line arguments or interactive interface
- **Efficient Indexing** - O(m) insertion and search time complexity

## Installation

```bash
# Clone the repository
git clone https://github.com/RighteousW/custom-text-indexer.git
cd custom-text-indexer

# No dependencies required - pure Python!
python indexer.py --help
```

## Usage

### Command-Line Interface

**Index files:**

```bash
python indexer.py file1.txt file2.txt song_lyrics.txt
```

**Index and search immediately:**

```bash
python indexer.py file1.txt file2.txt --search "python"
```

**Search with custom context:**

```bash
python indexer.py --load --search "i lov" --before 5 --after 30
```

**Start interactive mode:**

```bash
python indexer.py --load --interactive
```

### Interactive Mode

Commands available in interactive mode:

```
search <query> [before] [after]  - Search with context
index <filename>                 - Index a new file
save                             - Save index to disk
load                             - Load index from disk
quit                             - Exit
```

Example session:

```
> search i lov
Found 5 occurrence(s) of 'i lov':

1. file1.txt[line 3] i love refrigerators
2. song_lyrics.txt[line 10] i love you, i love you, i love you
3. file1.txt[line 1] i love programming in Python

> search i lov 5 30
Found 5 occurrence(s) of 'i lov':

1. file1.txt[line 3] ...3] i love refrigerators and oth...
2. song_lyrics.txt[line 10] ...0] i love you, i love you, i lo...

> quit
```

### Python API

```python
from indexer import TextIndexer

# Create indexer
indexer = TextIndexer()

# Index files
indexer.index_file('document.txt')
indexer.index_file('notes.txt')

# Save index
indexer.save_binary('my_index.bin')
indexer.save_json('my_index.json')

# Search with context (10 chars before, 20 after)
indexer.search('python', chars_before=10, chars_after=20)

# Load existing index
indexer.load_binary('my_index.bin')
```

## Command-Line Arguments

```
usage: indexer.py [-h] [-s SEARCH] [-b BEFORE] [-a AFTER] [-i] [-l] [--save]
                  [--bin-file BIN_FILE] [--json-file JSON_FILE]
                  [files ...]

positional arguments:
  files                 Text files to index

optional arguments:
  -h, --help            show this help message and exit
  -s SEARCH, --search SEARCH
                        Search query (prefix matching supported)
  -b BEFORE, --before BEFORE
                        Characters to show before match (default: 10)
  -a AFTER, --after AFTER
                        Characters to show after match (default: 20)
  -i, --interactive     Start interactive mode after indexing
  -l, --load            Load existing index from index.bin
  --save                Save index after processing
  --bin-file BIN_FILE   Binary index file (default: index.bin)
  --json-file JSON_FILE JSON index file (default: index.json)
```

## How It Works

### Trie Data Structure

The indexer uses a Trie (prefix tree) where:

- Each node represents a character in a word
- Paths from root to leaf form complete words
- Each node stores occurrence metadata: `(filename, line_num, position, line_text)`
- Shared prefixes share the same path, saving memory

**Example Structure:**

```
    root
     |
     p
    / \
   r   -----------a
   |              |
   o              t
   |              |
(programming) (patience)
```

### Time Complexity

- **Insertion:** O(m) where m = word length
- **Exact Search:** O(m) where m = word length
- **Prefix Search:** O(m + k) where m = prefix length, k = number of results

### Storage Format

**Binary (index.bin):**

- Compact pickle serialization of entire Trie
- Fast to load/save
- Not human-readable

**JSON (index.json):**

- Human-readable structure
- Useful for debugging and inspection
- Larger file size

## Project Structure

```
custom-text-indexer/
├── indexer.py          # Main implementation
├── README.md           # This file
├── index.bin           # Binary index (generated)
├── index.json          # JSON index (generated)
├── random_text1.txt           # Sample data
├── random_text2.txt     # Sample data
└── LICENSE             # MIT License
```

## Code Structure

### Classes

**`TrieNode`**

- Represents a single node in the Trie
- Stores children nodes, occurrences list, and end-of-word flag

**`Trie`**

- Core data structure for indexing
- Methods: `insert()`, `search_prefix()`

**`TextIndexer`**

- High-level interface for file indexing and searching
- Methods: `index_file()`, `search()`, `save_binary()`, `load_binary()`, `save_json()`

### Functions

**`main()`**

- Entry point handling argparse CLI
- Orchestrates indexing, searching, and interactive mode

**`interactive_mode()`**

- REPL interface for searching and managing index

## Examples

### Index Multiple Files

```bash
python indexer.py docs/*.txt logs/*.txt
```

### Search Across Files

```bash
python indexer.py --load --search "error" --before 20 --after 50
```

### Build and Save Index

```bash
python indexer.py file1.txt file2.txt file3.txt --save
```

### Load and Search

```bash
python indexer.py --load --search "hello world"
```

## Use Cases

- **Log File Analysis** - Quickly search through large log files
- **Document Search** - Index and search text documents with context
- **Code Search** - Find code snippets with surrounding context
- **Research** - Search through papers, notes, and references
- **Educational** - Learn Trie data structures and text indexing

## Limitations

- In-memory index (loaded entirely into RAM)
- Text files only (UTF-8 encoding)
- Case-insensitive (all words normalized to lowercase)
- Alphanumeric characters only (punctuation removed during indexing)
- No fuzzy matching or spell correction

## Contributing

Contributions welcome! Areas for improvement:

- Add fuzzy/approximate matching (Levenshtein distance)
- Implement index compression
- Add support for large files (streaming indexing)
- Support case-sensitive searching
- Add ranking/relevance scoring
- Implement phrase search (multi-word queries)
- Add regex pattern matching

## License

MIT License - see LICENSE file for details

