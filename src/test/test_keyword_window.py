from typing import List


def keyword_window(sel_word: str, words_of_sentence: List, length=5) -> List[str]:
    """
    find the index of sel_word at sentence, then decide words of @length size
    by backward and forward of it.
    For example: I am very happy to this course of psd if sel_word is happy, then
    returning: [am, very, happy, to, this]

    if length is even, then returning [very, happy, to, this]

    remember: sel_word is lemmatized
    """
    if length <= 0:
        return words_of_sentence
    index = words_of_sentence.index(sel_word)
    if index == -1:
        return words_of_sentence
    # backward is not enough
    if index < length // 2:
        back_slice = words_of_sentence[:index]
        # forward is also not enough,
        # showing the sentence is too short compared to length parameter
        if (length - index) >= len(words_of_sentence):
            return words_of_sentence
        else:
            return back_slice + words_of_sentence[index: index + length - len(back_slice)]
    # forward is not enough
    if (index + length // 2) >= len(words_of_sentence):
        forward_slice = words_of_sentence[index:len(words_of_sentence)]
        # backward is also not enough,
        # showing the sentence is too short compared to length parameter
        if index - length <= 0:
            return words_of_sentence
        else:
            return words_of_sentence[index - (length - len(forward_slice)):index] + forward_slice

    return words_of_sentence[index - length // 2: index + length // 2 + 1] if length % 2 \
        else words_of_sentence[index - length // 2 + 1: index + length // 2 + 1]


if __name__ == '__main__':
    words = ['I', 'am', 'very', 'happy', 'to', 'this', 'course', 'of', 'psd']
    res = keyword_window('happy', words, length=5)
    assert res == ['am', 'very', 'happy', 'to', 'this']
    res = keyword_window('to', words, length=4)
    assert res == ['happy', 'to', 'this', 'course']
    res = keyword_window('am', words, length=5)
    assert res == ['I', 'am', 'very', 'happy', 'to']
    res = keyword_window('of', words, length=5)
    assert res == ['to', 'this', 'course', 'of', 'psd']
    res = keyword_window('I', words, length=5)
    assert res == ['I', 'am', 'very', 'happy', 'to']
    res = keyword_window('am', words, length=5)
    assert res == ['I', 'am', 'very', 'happy', 'to']
    res = keyword_window('am', words, length=8)
    assert res == ['I', 'am', 'very', 'happy', 'to', 'this', 'course', 'of']
    res = keyword_window('am', words, length=9)
    assert res == words
    res = keyword_window('am', words, length=10)
    assert res == words
    res = keyword_window('psd', words, length=5)
    assert res == ['to', 'this', 'course', 'of', 'psd']
    res = keyword_window('psd', words, length=1)
    assert res == ['psd']
    res = keyword_window('psd', words, length=10)
    assert res == words
    res = keyword_window('psd', words, length=0)
    assert res == words
