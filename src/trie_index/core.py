"""Trie (prefix tree) over a fixed vocabulary.

The trie stores arbitrary hashable tokens, not just characters. This lets callers
use it for word-level autocomplete (`['hello', 'world']`) or character-level
autocomplete (`['h','e','l','l','o']`) by choosing what they feed in as sequences.

Tokens are kept in dict insertion order (Python >= 3.7 guarantees dict ordering).
A vocabulary iterated in a stable order therefore yields stable completion output.
We deliberately avoid sorting tokens: it would surprise callers whose vocabularies
already encode priority (e.g. by frequency).
"""

from typing import Iterable, Iterator, List, Optional, Sequence, Tuple


class _Node:
    """Internal trie node.

    A node is terminal when its ``value`` is not ``None``. We use ``None`` as the
    sentinel for "not a word end" rather than a separate boolean flag so that
    callers can store a payload (any non-None value) at each vocabulary entry —
    for instance a frequency or an original index — without expanding the API.
    """

    __slots__ = ("children", "value")

    def __init__(self) -> None:
        self.children: dict = {}
        self.value: Optional[object] = None


class Trie:
    """A prefix tree supporting insertion and longest-prefix completion.

    A trie trades memory for fast prefix lookup: completing a prefix of length k
    costs O(k + m) where m is the number of completions returned, independent of
    the total vocabulary size. For a fixed vocabulary with many short prefixes
    and frequent completions, this beats scanning and filtering the vocabulary
    on every query.
    """

    def __init__(self) -> None:
        self._root = _Node()
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def insert(self, sequence: Sequence, value: Optional[object] = True) -> None:
        """Insert ``sequence`` and associate it with ``value``.

        Re-inserting an existing sequence overwrites the previously stored value
        and does not increase the size, so a "fixed vocabulary" built from a set
        or deduplicated list stays the expected size.

        ``value`` defaults to ``True`` so that callers who only care about
        membership get a truthy result from :meth:`get` without thinking about
        payloads.
        """
        node = self._root
        for token in sequence:
            nxt = node.children.get(token)
            if nxt is None:
                nxt = _Node()
                node.children[token] = nxt
            node = nxt
        if node.value is None:
            self._size += 1
        node.value = value

    def contains(self, sequence: Sequence) -> bool:
        """Return True if ``sequence`` was inserted as a complete entry."""
        node = self._walk(sequence)
        return node is not None and node.value is not None

    def get(self, sequence: Sequence, default: Optional[object] = None) -> Optional[object]:
        """Return the value associated with ``sequence`` or ``default`` if absent."""
        node = self._walk(sequence)
        if node is None or node.value is None:
            return default
        return node.value

    def complete(self, prefix: Sequence, limit: Optional[int] = None) -> List[Tuple[Sequence, object]]:
        """Return up to ``limit`` (or all) entries that start with ``prefix``.

        Each result is a ``(sequence, value)`` tuple where ``sequence`` is the
        full stored entry and ``value`` is whatever was passed to :meth:`insert`.

        The empty prefix completes to the entire vocabulary. A prefix that is
        itself a complete entry is included in its own completions.

        Results are emitted in depth-first order following child insertion
        order, which gives stable, vocabulary-determined output. If you need a
        different ranking (e.g. by frequency), sort the returned list yourself
        or store frequency as the value and sort by ``-value``.
        """
        start = self._walk(prefix)
        if start is None:
            return []
        results: List[Tuple[Sequence, object]] = []
        # We pass a list as the accumulator rather than yielding from a generator
        # so the limit can short-circuit cleanly without exposing partial state
        # to the caller if they stop iterating early.
        prefix_list = list(prefix)
        self._collect(start, prefix_list, results, limit)
        return results

    def _walk(self, sequence: Iterable) -> Optional[_Node]:
        node = self._root
        for token in sequence:
            nxt = node.children.get(token)
            if nxt is None:
                return None
            node = nxt
        return node

    def _collect(
        self,
        node: _Node,
        path: List,
        results: List[Tuple[Sequence, object]],
        limit: Optional[int],
    ) -> None:
        if limit is not None and len(results) >= limit:
            return
        if node.value is not None:
            results.append((tuple(path), node.value))
            if limit is not None and len(results) >= limit:
                return
        for token, child in node.children.items():
            path.append(token)
            self._collect(child, path, results, limit)
            path.pop()

    def __iter__(self) -> Iterator[Tuple[Sequence, object]]:
        """Iterate over all ``(sequence, value)`` entries in stable order."""
        return iter(self.complete([]))
