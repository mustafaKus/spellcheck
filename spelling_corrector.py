"""Implements the spell checking with Peter Norvig's approach with more than one dictionary
    see the blog post here https://norvig.com/spell-correct.html"""

from itertools import chain
from string import ascii_lowercase, digits, punctuation


class SpellingCorrector:

    """Implements the spell checking with Peter Norvig's approach with more than one dictionary
    see the blog post here https://norvig.com/spell-correct.html"""

    _CHARACTERS = ascii_lowercase + digits + punctuation + " "

    def __init__(self, word_2_frequency, retokenizer=None, tokenizer=None):
        self._word_2_frequency = word_2_frequency
        self._tokenizer = tokenizer or (lambda utterance: utterance.split())
        self._retokenizer = retokenizer or (lambda tokens: " ".join(tokens))

    def _candidates(self, token):
        """Returns candidate words from the dictionaries by looking at the edit distances"""
        token_as_list = [token]
        token_1_edits = SpellingCorrector._one_edit_token_distances(token)
        token_2_edits = SpellingCorrector._two_edits_token_distances(token)
        return (
            self._known_in(token_as_list) or self._known_in(token_1_edits) or self._known_in(token_2_edits) or
            token_as_list)

    def _correct_token(self, token):
        """Corrects tokens"""
        token_candidates = self._candidates(token)
        return max(token_candidates, key=self._frequency_of)

    def _frequency_of(self, token):
        """Returns frequency of the token"""
        frequency_value_of_word = self._word_2_frequency.get(token)
        if not frequency_value_of_word:
            return 0
        return frequency_value_of_word

    def _known_in(self, words):
        """Returns the subset of words that appear in the vocabulary"""
        return set(word for word in words if self._word_2_frequency.get(word))

    @staticmethod
    def _one_edit_token_distances(token):
        """Returns the one edit distances of the token"""
        splitted_token_pairs = [(token[:i], token[i:]) for i in range(len(token) + 1)]
        deleted_distances = (
            left_split + right_split[1:] for left_split, right_split in splitted_token_pairs if right_split)
        inserted_variations = (
            left_split + insert_candidate + right_split for left_split, right_split in splitted_token_pairs for
            insert_candidate in SpellingCorrector._CHARACTERS)
        replaced_variations = (
            left_split + replace_candidate + right_split[1:] for left_split, right_split in splitted_token_pairs if
            right_split for replace_candidate in SpellingCorrector._CHARACTERS)
        transposed_variations = (
            left_split + right_split[1] + right_split[0] + right_split[2:] for left_split, right_split in
            splitted_token_pairs if len(right_split) > 1)
        return chain(inserted_variations, deleted_distances, replaced_variations, transposed_variations)

    @staticmethod
    def _two_edits_token_distances(token):
        """Returns the two edit distances of the token"""
        return [
            two_edits_distance_of_word for one_edit_distance_of_word in SpellingCorrector._one_edit_token_distances(
                token) for two_edits_distance_of_word in SpellingCorrector._one_edit_token_distances(
                    one_edit_distance_of_word)]

    def correct(self, utterance):
        """Tokenizes the utterance and corrects each token"""
        tokens = self._tokenizer(utterance.lower())
        corrected_tokens = [self._correct_token(token) for token in tokens]
        return self._retokenizer(corrected_tokens)
