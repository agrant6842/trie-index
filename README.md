# Trie Index

A prefix tree for fast autocomplete over a fixed vocabulary. Works on any sequence of hashable tokens — characters, words, or numbers — not just strings.

```python
from trie_index import Trie

t = Trie()
for word in ["cat", "car", "card", "care", "cart"]:
    t.insert(word)

[tuple(s) for s, _ in t.complete("car")]  # [('c','a','r'), ('c','a','r','d'), ...]
["".join(s) for s, _ in t.complete("car")]  # ['car', 'card', 'care', 'cart']

t.contains("card")   # True
t.get("car")          # True (default value)
```

## Why

Filtering a vocabulary by prefix scans the whole list every query. A trie makes prefix completion O(prefix length + number of completions), which matters when completions are requested frequently and the vocabulary is large but the returned set is small.

The trade-off is memory: every token of every entry becomes a node. For a few thousand short strings this is negligible; for millions of long entries it adds up.

## Edge cases

- The empty sequence is a valid entry: `t.insert([])` creates a terminal root node, and `t.contains([])` returns `True`.
- `complete([])` returns the entire vocabulary, not an empty list.
- Completions are ordered by child insertion order, not alphabetically. Insert your vocabulary in the order you want results emitted, or sort the returned list yourself.
- Values default to `True`; pass an explicit `value` to `insert` if you need to attach a payload.
