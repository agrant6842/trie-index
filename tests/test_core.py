import unittest

from trie_index import Trie


class TestInsertAndContains(unittest.TestCase):
    def test_insert_and_contains_single(self):
        t = Trie()
        t.insert("hello")
        self.assertTrue(t.contains("hello"))
        self.assertFalse(t.contains("hell"))
        self.assertFalse(t.contains("helloo"))

    def test_empty_sequence_is_terminal(self):
        t = Trie()
        t.insert([])
        self.assertTrue(t.contains([]))
        self.assertEqual(len(t), 1)

    def test_contains_for_missing_prefix_returns_false(self):
        t = Trie()
        t.insert("apple")
        self.assertFalse(t.contains("apricot"))
        self.assertFalse(t.contains("app"))

    def test_reinsert_overwrites_value_not_size(self):
        t = Trie()
        t.insert("cat", value=1)
        t.insert("cat", value=2)
        self.assertEqual(len(t), 1)
        self.assertEqual(t.get("cat"), 2)


class TestGet(unittest.TestCase):
    def test_get_returns_default_for_missing(self):
        t = Trie()
        t.insert("dog", value="bark")
        self.assertEqual(t.get("dog"), "bark")
        self.assertIsNone(t.get("do"))
        self.assertIsNone(t.get("dogs"))
        self.assertEqual(t.get("do", default="missing"), "missing")

    def test_get_default_value_is_true(self):
        t = Trie()
        t.insert("bird")
        self.assertTrue(t.get("bird"))


class TestComplete(unittest.TestCase):
    def test_complete_returns_matching_descendants(self):
        t = Trie()
        for w in ["cat", "car", "card", "care", "cart"]:
            t.insert(w)
        results = t.complete("car")
        words = ["".join(seq) for seq, _ in results]
        self.assertEqual(words, ["car", "card", "care", "cart"])

    def test_complete_includes_prefix_if_terminal(self):
        t = Trie()
        t.insert("pre")
        t.insert("prefix")
        t.insert("preview")
        words = ["".join(seq) for seq, _ in t.complete("pre")]
        self.assertEqual(words, ["pre", "prefix", "preview"])

    def test_complete_empty_prefix_returns_all(self):
        t = Trie()
        for w in ["a", "b", "c"]:
            t.insert(w)
        words = sorted("".join(seq) for seq, _ in t.complete([]))
        self.assertEqual(words, ["a", "b", "c"])

    def test_complete_unknown_prefix_returns_empty(self):
        t = Trie()
        t.insert("hello")
        self.assertEqual(t.complete("xyz"), [])

    def test_complete_respects_limit(self):
        t = Trie()
        for w in ["aa", "ab", "ac", "ad", "ae"]:
            t.insert(w)
        results = t.complete("a", limit=3)
        self.assertEqual(len(results), 3)
        words = ["".join(seq) for seq, _ in results]
        self.assertEqual(words, ["aa", "ab", "ac"])

    def test_complete_returns_values(self):
        t = Trie()
        t.insert("apple", value=5)
        t.insert("apricot", value=7)
        results = dict(("".join(seq), v) for seq, v in t.complete("ap"))
        self.assertEqual(results.get("apple"), 5)
        self.assertEqual(results.get("apricot"), 7)

    def test_complete_preserves_insertion_order_of_children(self):
        t = Trie()
        for w in ["zebra", "zoo", "zoom"]:
            t.insert(w)
        words = ["".join(seq) for seq, _ in t.complete("z")]
        self.assertEqual(words, ["zebra", "zoo", "zoom"])


class TestTokenTuples(unittest.TestCase):
    def test_token_sequences_not_just_strings(self):
        t = Trie()
        t.insert(("a", "b", "c"), value="abc")
        t.insert(("a", "b", "d"), value="abd")
        self.assertTrue(t.contains(("a", "b", "c")))
        results = t.complete(("a", "b"))
        seqs = sorted(seq for seq, _ in results)
        self.assertEqual(seqs, [("a", "b", "c"), ("a", "b", "d")])

    def test_numeric_tokens(self):
        t = Trie()
        t.insert([1, 2, 3], value="one-two-three")
        t.insert([1, 2, 4], value="one-two-four")
        results = t.complete([1, 2])
        values = {v for _, v in results}
        self.assertEqual(values, {"one-two-three", "one-two-four"})


class TestEdgeCases(unittest.TestCase):
    def test_len_tracks_unique_entries(self):
        t = Trie()
        self.assertEqual(len(t), 0)
        t.insert("a")
        t.insert("b")
        t.insert("a")
        self.assertEqual(len(t), 2)

    def test_iter_yields_all_entries(self):
        t = Trie()
        for w in ["m", "n", "o"]:
            t.insert(w)
        words = sorted("".join(seq) for seq, _ in t)
        self.assertEqual(words, ["m", "n", "o"])

    def test_prefix_longer_than_any_entry_returns_empty(self):
        t = Trie()
        t.insert("hi")
        self.assertEqual(t.complete("hello"), [])

    def test_single_char_overlapping_vocab(self):
        t = Trie()
        for w in ["a", "aa", "aaa"]:
            t.insert(w)
        words = ["".join(seq) for seq, _ in t.complete("a")]
        self.assertEqual(words, ["a", "aa", "aaa"])


if __name__ == "__main__":
    unittest.main()
