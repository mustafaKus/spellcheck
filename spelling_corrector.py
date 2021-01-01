"""Implements the spell checking with Peter Norvig's approach with more than one dictionary
    see the blog post here https://norvig.com/spell-correct.html"""

from itertools import chain
from string import ascii_lowercase, digits, punctuation
from abc import ABC, abstractmethod
from collections import defaultdict


class AbstractSpellingCorrector(ABC):

    """Implements the spelling corrector interface"""

    _CHARACTERS = ascii_lowercase + digits + punctuation + " "

    def __init__(self, word_2_frequency, retokenizer=None, tokenizer=None):
        self._word_2_frequency = word_2_frequency
        self._tokenizer = tokenizer or (lambda utterance: utterance.split())
        self._retokenizer = retokenizer or (lambda tokens: " ".join(tokens))

    @abstractmethod
    def _candidates(self, token):
        """Returns candidate words from the dictionaries by looking at the edit distances"""

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

    def correct(self, utterance):
        """Tokenizes the utterance and corrects each token"""
        tokens = self._tokenizer(utterance.lower())
        corrected_tokens = [self._correct_token(token) for token in tokens]
        return self._retokenizer(corrected_tokens)


class NorvigCorrector(AbstractSpellingCorrector):

    """Implements the spell checking with Peter Norvig's approach see the blog post here
    https://norvig.com/spell-correct.html"""


    def _candidates(self, token):
        """Returns candidate words from the dictionaries by looking at the edit distances"""
        token_as_list = [token]
        token_1_edits = NorvigCorrector._one_edit_token_distances(token)
        token_2_edits = NorvigCorrector._two_edits_token_distances(token)
        return (
            self._known_in(token_as_list) or self._known_in(token_1_edits) or self._known_in(token_2_edits) or
            token_as_list)

    @staticmethod
    def _one_edit_token_distances(token):
        """Returns the one edit distances of the token"""
        splitted_token_pairs = [(token[:i], token[i:]) for i in range(len(token) + 1)]
        deleted_distances = (
            left_split + right_split[1:] for left_split, right_split in splitted_token_pairs if right_split)
        inserted_variations = (
            left_split + insert_candidate + right_split for left_split, right_split in splitted_token_pairs for
            insert_candidate in NorvigCorrector._CHARACTERS)
        replaced_variations = (
            left_split + replace_candidate + right_split[1:] for left_split, right_split in splitted_token_pairs if
            right_split for replace_candidate in NorvigCorrector._CHARACTERS)
        transposed_variations = (
            left_split + right_split[1] + right_split[0] + right_split[2:] for left_split, right_split in
            splitted_token_pairs if len(right_split) > 1)
        return chain(inserted_variations, deleted_distances, replaced_variations, transposed_variations)

    @staticmethod
    def _two_edits_token_distances(token):
        """Returns the two edit distances of the token"""
        return (
            two_edits_distance_of_word for one_edit_distance_of_word in NorvigCorrector._one_edit_token_distances(
                token) for two_edits_distance_of_word in NorvigCorrector._one_edit_token_distances(
                    one_edit_distance_of_word))


class SymmetricDeleteCorrector(AbstractSpellingCorrector):

    """Implements the spell checking with the symmetric delete spelling correction algorithm see
    https://wolfgarbe.medium.com/1000x-faster-spelling-correction-algorithm-2012-8701fcd87a5f"""

    def __init__(self, word_2_frequency, retokenizer=None, tokenizer=None):
        super(SymmetricDeleteCorrector, self).__init__(word_2_frequency, retokenizer, tokenizer)
        self._deleted_variation_2_dictionary_words = self._create_deleted_variation_2_dictionary_words()

    def _candidates(self, token):
        """Returns candidate words from the dictionaries by looking at the edit distances"""
        token_as_list = [token]
        token_1_edits = SymmetricDeleteCorrector._one_edit_deleted_variations(token)
        token_2_edits = SymmetricDeleteCorrector._two_edits_deleted_variations(token)
        return (
            self._known_in(token_as_list) or
            self._deleted_variation_2_dictionary_words[token] or
            set(
                chain.from_iterable(
                    self._deleted_variation_2_dictionary_words[token_1_edit] for token_1_edit in token_1_edits)) or
            set(
                chain.from_iterable(
                    self._deleted_variation_2_dictionary_words[token_2_edit] for token_2_edit in token_2_edits)))

    def _create_deleted_variation_2_dictionary_words(self):
        """Creates the deleted variation to dictionary words"""
        deleted_variation_2_dictionary_words = defaultdict(set)
        for word in self._word_2_frequency.keys():
            deleted_variations = chain(self._one_edit_deleted_variations(word), self._two_edits_deleted_variations(word))
            for deleted_variation in deleted_variations:
                deleted_variation_2_dictionary_words[deleted_variation].add(word)
        return deleted_variation_2_dictionary_words

    @staticmethod
    def _one_edit_deleted_variations(token):
        """Returns the one edit deleted variations of the token"""
        splitted_token_pairs = [(token[:i], token[i:]) for i in range(len(token) + 1)]
        return (left_split + right_split[1:] for left_split, right_split in splitted_token_pairs if right_split)

    @staticmethod
    def _two_edits_deleted_variations(token):
        """Returns the two edit deleted variations of the token"""
        return (
            two_edits_distance_of_word for one_edit_distance_of_word in
            SymmetricDeleteCorrector._one_edit_deleted_variations(token) for two_edits_distance_of_word in
            SymmetricDeleteCorrector._one_edit_deleted_variations(one_edit_distance_of_word))





