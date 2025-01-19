import logging
import os
import time
import traceback
from typing import cast

from deepl import deepl
from googletrans import Translator

logger = logging.getLogger(__name__)


class Translated(object):
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
        return cast(
            list[Translated], translator.translate(to_translate, dest=self.tolang)
        )

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
            logger.debug("Next request in " + str(self.deeplsleeptime) + " seconds...")
            time.sleep(self.deeplsleeptime)
        except Exception as e:
            logger.debug("deeplcli:")
            logger.debug(e)
            logger.debug(
                "Retrying to translate in " + str(self.sleeptime) + " seconds..."
            )
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
            max_value = 0
            i = self.batch_size
            while i < len(to_translate):
                if max_value == i:
                    break

                y = i
                if self.api == "deepl":
                    char_count = -1
                    while char_count < 0 or char_count >= self.deeplcharlimit:
                        char_count = self.count_characters(
                            self.deeplcli_formatted_input(to_translate[max_value:y])
                        )
                        y = y - 1
                    i = y
                else:
                    char_count = self.count_characters(to_translate[max_value:y])

                logger.info(
                    f"Processing line <{max_value}> to <{i}> (Characters: {char_count})",
                )
                translations += self.translate_sentence(to_translate[max_value:i])
                self.append_lines_file(translations)
                max_value = i
                i += self.batch_size
            remainder = max_value + len(to_translate) % self.batch_size
            if remainder == 0:
                remainder = max_value + self.batch_size
            logger.info(
                f"Processing line <{max_value}> to <{remainder}>",
            )
            translations += self.translate_sentence(to_translate[max_value:remainder])
            self.append_lines_file(translations)
        return translations

    def extract_string(self, lines: list[str]) -> list[str]:
        to_translate: list[str] = []
        for line in lines:
            pos = self.find_nth(line, ",", 9) + 1
            subline = line[pos:]
            self.find_special_chars(subline)
            subline = self.encode_special_chars(subline)
            subline = subline.replace("\\N", " ")
            if "deepl" in self.api:
                # subline = subline.replace('\\N', ' 0x00 <x>0x00</x> ')
                subline = subline.replace(" -", " 0x00 <x>0x00</x> ")
            # elif self.api == 'google':
            #     subline = subline.replace('\\N', ' \\N ')
            to_translate += [subline]

        return to_translate

    def add_carriage_return(self, original_subline: str) -> str:
        subline = " ".join(original_subline.split())
        next_br = False
        index = 0
        last_dash_index = 0
        ponctuation_separator = [" ", ",", ";", ".", "!", "?"]
        for char in subline:
            if (
                char == "-"
                and index + 1 < len(subline)
                and subline[index + 1] != "-"
                and index > 0
                and subline[index - 1] in ponctuation_separator
            ):
                subline = subline[:index] + "\\N" + subline[index:]
                index += 2
                last_dash_index = index
            if index - last_dash_index > 37:
                next_br = True
            if (
                next_br
                and index + 1 < len(subline)
                and len(subline[index + 1 :]) > 0
                and subline[index + 1] not in ponctuation_separator
                and char in ponctuation_separator
            ):
                subline = subline[: index + 1] + "\\N" + subline[index + 1 :]
                index += 2
                last_dash_index = index
                next_br = False
            index += 1
        return subline

    def recombine(
        self, translations: list[Translated], lines_to_translate: list[str]
    ) -> list[str]:
        new_lines = []
        try:
            for _ in lines_to_translate:
                if self.index_recombine >= len(translations):
                    break

                if "deepl" in self.api:
                    translations[self.index_recombine].text = translations[
                        self.index_recombine
                    ].text.replace(" 0x00 <x>0x00</x> ", " -")
                    translations[self.index_recombine].text = translations[
                        self.index_recombine
                    ].text.replace(" 0x00 <x>0x00</x>", " -")
                    translations[self.index_recombine].text = translations[
                        self.index_recombine
                    ].text.replace("0x00 <x>0x00</x>", " -")
                # elif self.api == 'google':
                #     translations[self.index_recombine].text = translations[self.index_recombine].text.replace('\ n', '\\N')

                # If its people singing, skip it and leave the original lyrics
                if "♪" in lines_to_translate[self.index_recombine]:
                    new_lines += [lines_to_translate[self.index_recombine]]
                    self.index_recombine += 1
                    continue

                logger.debug(translations[self.index_recombine].text)
                logger.debug(lines_to_translate[self.index_recombine])

                translations[self.index_recombine].text = self.decode_special_chars(
                    translations[self.index_recombine].text
                )
                translations[self.index_recombine].text = self.add_carriage_return(
                    translations[self.index_recombine].text
                )

                pos = (
                    self.find_nth(lines_to_translate[self.index_recombine], ",", 9) + 1
                )
                subline = "".join(
                    (
                        lines_to_translate[self.index_recombine][:pos],
                        translations[self.index_recombine].text,
                    )
                )
                new_lines += [subline]
                self.index_recombine += 1
        except Exception as err:
            logger.warning(f"Recombine failed: {err}")
            traceback.print_exc()
            pass
        return new_lines

    def add_header(
        self,
        start_line: int,
        raw_lines: list[str],
        translated_lines: list[str],
        append: bool,
    ) -> list[str]:
        header = []
        if not append:
            header = raw_lines[:start_line]
        full_ass = header + translated_lines
        return full_ass

    def write_file(self, full_ass: list[str], append: bool) -> None:
        filename = self.file.replace(".ass", "_[" + self.tolang + "].ass")
        if not append:
            fp = open(filename, "w", encoding="utf-8")
        else:
            fp = open(filename, "a", encoding="utf-8")
        for line in full_ass:
            fp.write(line + "\n")
        fp.close()

    def append_lines_file(self, translated_lines: list[Translated]) -> None:
        append = False
        if self.index_recombine > 0:
            append = True
        translated_dialogue = self.recombine(translated_lines, self.lines_to_translate)
        full_ass = self.add_header(
            self.start_line, self.raw_lines, translated_dialogue, append
        )
        self.write_file(full_ass, append)

    def run(self) -> None:
        if not os.path.exists(self.file):
            raise Exception(f"File <{self.file}> does not exist!")

        self.raw_lines = self.get_lines()
        self.lines_to_translate, self.start_line = self.extract_lines(
            self.raw_lines
        )  # Returns the lines that need to be translated
        self.to_translate = self.extract_string(self.lines_to_translate)
        self.translate(self.to_translate)
