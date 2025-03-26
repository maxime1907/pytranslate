import unittest

from pytranslate.utils import add_carriage_return


class TestAddCarriageReturn(unittest.TestCase):
    def test_basic_sentence(self):
        self.assertEqual(add_carriage_return("This is a test sentence."), "This is a test sentence.")

    def test_sentence_with_hyphen(self):
        self.assertEqual(add_carriage_return("Well - structured text."), "Well \\N- structured text.")

    def test_long_sentence(self):
        self.assertEqual(
            add_carriage_return("This is a very long sentence that should eventually break into a new line somewhere."),
            "This is a very long sentence that should \\Neventually break into a new line somewhere.",
        )

    def test_sentence_with_punctuation(self):
        self.assertEqual(
            add_carriage_return("Hello, world! How are you today?"),
            "Hello, world! How are you today?",
        )

    def test_multiple_hyphens(self):
        self.assertEqual(
            add_carriage_return("This - is - a - test."),
            "This \\N- is \\N- a \\N- test.",
        )

    def test_hesitating(self):
        self.assertEqual(add_carriage_return("I--"), "I--")

    def test_normal(self):
        self.assertEqual(
            add_carriage_return("- I would like to apologise - Well that's nothing darling"),
            "- I would like to apologise \\N- Well that's nothing darling",
        )

    def test_normal2(self):
        self.assertEqual(
            add_carriage_return("- I would like to apologise    - Well that's nothing darling"),
            "- I would like to apologise \\N- Well that's nothing darling",
        )


if __name__ == "__main__":
    unittest.main()
