# def test_deepl(self):
#     testPerLine = False

#     self.tolang = 'FR'
#     self.fromlang = 'EN'

#     to_translate1 = [
#         "I've even had guys move closer to me.",
#         "Sorry, I forgot my textbook.",
#         "And starting next month, I'll be...",
#         "A high school girl!",
#         "The most popular period in anyone's life...",
#         "Three years when flags are set \\N even if I don't do anything,",
#         "and hormones run wild!",
#         "In girls' dating sims, I've already been \\N a high school girl for fifty years",
#         "and dated a hundred boys of all kinds.",
#         "I've been very thorough in my simulations!"
#     ]

#     to_translate2 = [
#         'This is a story only \\N she and I know about.',
#         'The story of the \\N secret of this world.',
#         'It was like a pool of light.',
#         'She ran out of the hospital.',
#         'Praying with all her heart,',
#         'she crossed the torii gate.',
#         'Fish?',
#         'Now I wonder if what I saw \\N that day was just a dream.',
#         'But it wasn\'t a dream.',
#         'That summer day, up in the sky,',
#         'we changed the shape of the world.'
#     ]

#     to_translate3 = [
#         'Being ambivalent is \\N the worst thing for a man.',
#         'Really?',
#         'It\'s the basics to be clear before you \\N start dating, and be ambiguous later.',
#         'Can I call you Nagi-senpai?',
#         'sis has been working \\N all the time since Mom died.',
#         'She\'s been doing it for me, \\N because I’m still a kid.',
#         'So, I want sis to do \\N more teenage-like stuff.',
#         'I don\'t know if you\'re the \\N right guy, though.',
#         'Thank you very much.',
#         'Uhm, do you think she\'ll like it?'
#     ]

#     to_translate4 = [
#         'You should treat me with respect.',
#         'Are you hungry, Hodaka?',
#         'Sit there and relax.',
#         'How do you like living in Tokyo?',
#         'Come to think of it,',
#         'I don\'t feel breathless anymore.',
#         'Happy to hear that.',
#         'I\'m in love with this job. \\N This sunshine girl job.',
#         'Thank you, Hodaka.',
#         '-Wait! \\N -Someone got onto the tracks.',
#         '-Who\'s that? \\N -Hey, you!',
#         'It\'s dangerous!'
#     ]

#     to_translate5 = [
#         'I was beginning to struggle a lot,',
#         'when she came to me and said:',
#         '"I am no longer free my love"'
#     ]

#     to_translate = [
#         to_translate4,
#         to_translate1,
#         to_translate3,
#         to_translate2,
#         to_translate5
#     ]

#     if testPerLine:
#         to_translateSentence = to_translate[3]
#         if isinstance(to_translateSentence, list):
#             for sentence in to_translateSentence:
#                 print(self.deepltranslate(sentence).text)
#     else:
#         if isinstance(to_translate, list):
#             for to_translateInnerList in to_translate:
#                 print(self.deepltranslate(to_translateInnerList))
