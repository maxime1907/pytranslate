import logging
import os
import time
import traceback
from typing import cast

from deepl import deepl
from googletrans import Translator

from pytranslate.utils import add_carriage_return

logger = logging.getLogger(__name__)


class Translated:
    """Translate result object
    :param text: translated text
    """

    def __init__(self, *, text: str):
        self.text = text

    def __str__(self) -> str:
        return self.__unicode__()

    def __unicode__(self) -> str:
        return f"Translated(text={self.text})"


class ASSTranslator:
    def __init__(self, *, file: str, tolang: str, fromlang: str, api: str):
        self.file = file
        self.fromlang = fromlang
        self.tolang = tolang
        self.api = api

        self.headeradded = False
        self.sleeptime = 10
        self.deeplsleeptime = 3
        self.deeplcharlimit = 1500
        self.index_recombine = 0
        self.batch_size = 50

        self.special_characters: list[list[str]] = []
        # self.add_special_char('\\N')

    def googletranslate(self, to_translate: list[str]) -> list[Translated]:
        translator = Translator()
        return cast(list[Translated], translator.translate(to_translate, dest=self.tolang))

    def deeplcli_formatted_input(self, to_translate: list[str] | str) -> str:
        my_to_translate: str = ""
        if isinstance(to_translate, list):
            my_to_translate = "\n".join(to_translate)
        return my_to_translate

    def deeplcli_formatted_output(self, translated: str) -> list[str]:
        return translated.split("\n")

    def deeplcli(self, to_translate: list[str] | str) -> list[Translated]:
        translated: list[Translated] = []

        try:
            deepl_client = deepl.DeepLCLI(self.fromlang.lower(), self.tolang.lower())
            my_to_translate = self.deeplcli_formatted_input(to_translate)
            my_translated: str = deepl_client.translate(my_to_translate)
            my_translated_list = self.deeplcli_formatted_output(my_translated)
            for my_translated_str in my_translated_list:
                translated.append(Translated(text=my_translated_str))
            logger.debug(f"Next request in {self.deeplsleeptime} seconds...")
            time.sleep(self.deeplsleeptime)
        except Exception as e:
            logger.debug(f"deeplcli error: {e}, retrying in {self.sleeptime} seconds...")
            time.sleep(self.sleeptime)
            return self.deeplcli(to_translate)
        return translated

    def translate_sentence(self, to_translate: list[str]) -> list[Translated]:
        if self.api == "google":
            return self.googletranslate(to_translate)
        elif self.api == "deepl":
            return self.deeplcli(to_translate)

        raise Exception(f"API <{self.api}> is not supported")

    def find_nth(self, haystack: str, needle: str, n: int) -> int:
        start = haystack.find(needle)
        while start >= 0 and n > 1:
            start = haystack.find(needle, start + len(needle))
            n -= 1
        return start

    def get_lines(self) -> list[str]:
        with open(self.file, encoding="utf-8") as file_pointer:
            lines_string = file_pointer.read()
            lines = lines_string.split("\n")
        return lines

    def extract_lines(self, lines: list[str]) -> tuple[list[str], int]:
        start_line = 0
        while lines[start_line][0:8] != "Dialogue":
            start_line += 1

        return lines[start_line:], start_line

    def add_special_char(self, char: str) -> None:
        size = len(self.special_characters)
        self.special_characters.append([char, "0x" + str(size + 1)])

    def find_special_chars(self, line: str) -> None:
        if "{" in line:
            start = line.find("{")
            end = line.find("}")
            self.add_special_char(line[start : end + 1])
            line = line[end + 1 :]
            self.find_special_chars(line)

    def encode_special_chars(self, line: str) -> str:
        for special_char in self.special_characters:
            if special_char[0] in line:
                line = line.replace(special_char[0], " " + special_char[1] + " ")
        return line

    def decode_special_chars(self, line: str) -> str:
        for special_char in self.special_characters:
            if special_char[1] in line:
                line = line.replace(" " + special_char[1] + " ", special_char[0])
                line = line.replace(special_char[1], special_char[0])
        return line

    def count_characters(self, strings: list[str] | str) -> int:
        return sum(len(s) for s in strings)

    def translate(self, to_translate: list[str]) -> list[Translated]:
        translations: list[Translated] = []

        if len(to_translate) < self.batch_size:
            translations += self.translate_sentence(to_translate)
            self.append_lines_file(translations)
        else:
            self.process_batches(to_translate, translations)

        return translations

    def process_batches(self, to_translate: list[str], translations: list[Translated]) -> None:
        max_value = 0
        i = self.batch_size
        while i < len(to_translate):
            if max_value == i:
                break

            y = self.process_batch(to_translate, max_value, i)
            translations += self.translate_sentence(to_translate[max_value:y])
            self.append_lines_file(translations)
            max_value = y
            i += self.batch_size

        self.process_remainder(to_translate, translations, max_value)

    def process_batch(self, to_translate: list[str], max_value: int, i: int) -> int:
        y = i
        if self.api == "deepl":
            char_count = -1
            while char_count < 0 or char_count >= self.deeplcharlimit:
                char_count = self.count_characters(self.deeplcli_formatted_input(to_translate[max_value:y]))
                y = y - 1
        else:
            char_count = self.count_characters(to_translate[max_value:y])

        logger.info(f"Processing line <{max_value}> to <{y}> (Characters: {char_count})")
        return y

    def process_remainder(self, to_translate: list[str], translations: list[Translated], max_value: int) -> None:
        remainder = max_value + len(to_translate) % self.batch_size
        if remainder == 0:
            remainder = max_value + self.batch_size
        logger.info(f"Processing line <{max_value}> to <{remainder}>")
        translations += self.translate_sentence(to_translate[max_value:remainder])
        self.append_lines_file(translations)

    def extract_string(self, lines: list[str]) -> list[str]:
        to_translate: list[str] = []
        for line in lines:
            subline = self.extract_subline(line)
            subline = self.process_subline(subline)
            to_translate.append(subline)
        return to_translate

    def extract_subline(self, line: str) -> str:
        pos = self.find_nth(line, ",", 9) + 1
        return line[pos:]

    def process_subline(self, subline: str) -> str:
        self.find_special_chars(subline)
        subline = self.encode_special_chars(subline)
        subline = subline.replace("\\N", " ")

        if "deepl" in self.api:
            subline = subline.replace(" -", " 0x00 <x>0x00</x> ")

        return subline

    def recombine(self, translated_lines: list[Translated], lines_to_translate: list[str]) -> list[str]:
        combined_lines = []
        try:
            for line in lines_to_translate:
                if self.index_recombine >= len(translated_lines):
                    break

                current_translation = translated_lines[self.index_recombine]

                if "deepl" in self.api:
                    current_translation.text = self.clean_deepl_text(current_translation.text)

                if "♪" in line:
                    combined_lines.append(line)
                    self.index_recombine += 1
                    continue

                logger.debug(current_translation.text)
                logger.debug(line)

                current_translation.text = self.process_translation(current_translation.text)

                comma_position = self.find_nth(line, ",", 9) + 1
                combined_subline = line[:comma_position] + current_translation.text

                combined_lines.append(combined_subline)
                self.index_recombine += 1
        except Exception as err:
            logger.warning(f"Recombine failed: {err}")
            traceback.print_exc()

        return combined_lines

    def clean_deepl_text(self, text: str) -> str:
        return (
            text.replace(" 0x00 <x>0x00</x> ", " -")
            .replace(" 0x00 <x>0x00</x>", " -")
            .replace("0x00 <x>0x00</x>", " -")
        )

    def process_translation(self, text: str) -> str:
        text = self.decode_special_chars(text)
        return add_carriage_return(text)

    def add_header(
        self,
        start_line: int,
        raw_lines: list[str],
        translated_lines: list[str],
        append: bool,
    ) -> list[str]:
        header = raw_lines[:start_line] if not append else []
        return header + translated_lines

    def write_file(self, full_ass: list[str], append: bool) -> None:
        filename = self.file.replace(".ass", f"_[{self.tolang}].ass")
        mode = "a" if append else "w"
        with open(filename, mode, encoding="utf-8") as fp:
            fp.writelines(f"{line}\n" for line in full_ass)

    def append_lines_file(self, translated_lines: list[Translated]) -> None:
        append = self.index_recombine > 0
        translated_dialogue = self.recombine(translated_lines, self.lines_to_translate)
        full_ass = self.add_header(self.start_line, self.raw_lines, translated_dialogue, append)
        self.write_file(full_ass, append)

    def run(self) -> None:
        if not os.path.exists(self.file):
            raise FileNotFoundError(f"File <{self.file}> does not exist!")

        self.raw_lines = self.get_lines()
        self.lines_to_translate, self.start_line = self.extract_lines(self.raw_lines)
        self.to_translate = self.extract_string(self.lines_to_translate)
        self.translate(self.to_translate)
