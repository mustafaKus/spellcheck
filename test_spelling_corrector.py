"""Implements the test class for the spelling corrector"""

import json
import logging
import os
import sys
import unittest
from unittest import TestCase

from spelling_corrector import NorvigCorrector, SymmetricDeleteCorrector


class SpellingCorrectorTest(TestCase):
    """Implements the test class for the spelling corrector"""

    def test_norvig_corrector(self):
        """Tests the norvig corrector"""
        current_working_directory = os.path.abspath(os.getcwd())
        tests_directory = os.path.join(current_working_directory, "tests")
        logging.info("Tests the norvig corrector")
        logging.info("Tests directory is %s" % tests_directory)
        for test_directory_name in os.listdir(tests_directory):
            logging.info("Testing in %s directory" % test_directory_name)
            test_directory_path = os.path.join(tests_directory, test_directory_name)
            dictionary_path = os.path.join(test_directory_path, "dictionary.txt")
            test_input_2_expected_output_path = os.path.join(test_directory_path, "input_2_expected_output.json")
            word_2_frequency = {}
            with open(dictionary_path, "r") as dictionary_file:
                logging.info("Reading the dictionary %s" % test_directory_name)
                dictionary_lines = dictionary_file.readlines()
                for _, line in enumerate(dictionary_lines):
                    word, frequency_value = line.strip().split()
                    word_2_frequency[word.lower()] = int(frequency_value)
            spelling_corrector = NorvigCorrector(word_2_frequency)
            with open(test_input_2_expected_output_path) as input_2_expected_output_file:
                logging.info("Reading the test data")
                input_2_expected_output = json.load(input_2_expected_output_file)
                for input_, expected_output in input_2_expected_output.items():
                    logging.info("Expected output for the input '%s' is '%s'" % (input_, expected_output))
                    self.assertEqual(expected_output, spelling_corrector.correct(input_))

    def test_symmetric_delete_corrector(self):
        """Tests the symmetric delete corrector"""
        current_working_directory = os.path.abspath(os.getcwd())
        tests_directory = os.path.join(current_working_directory, "tests")
        logging.info("Tests the symmetric delete corrector")
        logging.info("Tests directory is %s" % tests_directory)
        for test_directory_name in os.listdir(tests_directory):
            logging.info("Testing in %s directory" % test_directory_name)
            test_directory_path = os.path.join(tests_directory, test_directory_name)
            dictionary_path = os.path.join(test_directory_path, "dictionary.txt")
            test_input_2_expected_output_path = os.path.join(test_directory_path, "input_2_expected_output.json")
            word_2_frequency = {}
            with open(dictionary_path, "r") as dictionary_file:
                logging.info("Reading the dictionary %s" % test_directory_name)
                dictionary_lines = dictionary_file.readlines()
                for _, line in enumerate(dictionary_lines):
                    word, frequency_value = line.strip().split()
                    word_2_frequency[word.lower()] = int(frequency_value)
            spelling_corrector = SymmetricDeleteCorrector(word_2_frequency)
            with open(test_input_2_expected_output_path) as input_2_expected_output_file:
                logging.info("Reading the test data")
                input_2_expected_output = json.load(input_2_expected_output_file)
                for input_, expected_output in input_2_expected_output.items():
                    logging.info("Expected output for the input '%s' is '%s'" % (input_, expected_output))
                    self.assertEqual(expected_output, spelling_corrector.correct(input_))


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    unittest.main()
