#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Vit Novotny <witiko@mail.muni.cz>
# Licensed under the GNU LGPL v2.1 - http://www.gnu.org/licenses/lgpl.html

"""
This module provides a namespace for functions that use the Levenshtein distance.
"""

import logging

# If python-Levenshtein is available, import it.
# If python-Levenshtein is unavailable, ImportError will be raised in levsim.
try:
    from Levenshtein import distance
    LEVENSHTEIN_EXT = True
except ImportError:
    LEVENSHTEIN_EXT = False

from gensim.similarities.termsim import TermSimilarityIndex

logger = logging.getLogger(__name__)


def levsim(t1, t2, alpha=1.8, beta=5.0):
    """Get the Levenshtein similarity between two terms.

    Return the Levenshtein similarity between two terms. The similarity is a
    number between <0.0, 1.0>, higher is more similar.

    Parameters
    ----------
    t1 : {bytes, str, unicode}
        The first compared term.
    t2 : {bytes, str, unicode}
        The second compared term.
    alpha : float
        The multiplicative factor alpha defined by Charlet and Damnati (2017).
    beta : float
        The exponential factor beta defined by Charlet and Damnati (2017).

    Returns
    -------
    float
        The Levenshtein similarity between `t1` and `t2`.

    Notes
    -----
    This notion of Levenshtein similarity was first defined in section 2.2 of
    `Delphine Charlet and Geraldine Damnati, "SimBow at SemEval-2017 Task 3:
    Soft-Cosine Semantic Similarity between Questions for Community Question
    Answering", 2017 <http://www.aclweb.org/anthology/S/S17/S17-2051.pdf>`__.

    """
    if not LEVENSHTEIN_EXT:
        raise ImportError("Please install python-Levenshtein Python package to compute the Levenshtein distance.")
    return alpha * (1 - distance(t1, t2) * 1.0 / max(len(t1), len(t2)))**beta


class LevenshteinSimilarityIndex(TermSimilarityIndex):
    """
    Computes Levenshtein similarities between terms and retrieves most similar
    terms for a given term.

    Notes
    -----
    This is a naive implementation that iteratively computes pointwise Levenshtein similarities
    between individual terms. Using this implementation to compute the similarity of all terms in
    real-world dictionaries such as the English Wikipedia will take years.

    Parameters
    ----------
    dictionary : :class:`~gensim.corpora.dictionary.Dictionary`
        A dictionary that specifies the considered terms.
    alpha : float, optional
        The multiplicative factor alpha defined by Charlet and Damnati (2017).
    beta : float, optional
        The exponential factor beta defined by Charlet and Damnati (2017).
    threshold : float, optional
        Only terms more similar than `threshold` are considered when retrieving
        the most similar terms for a given term.

    See Also
    --------
    :func:`gensim.similarities.levenshtein.levsim`
        The Levenshtein similarity.
    :class:`~gensim.similarities.termsim.SparseTermSimilarityMatrix`
        Build a term similarity matrix and compute the Soft Cosine Measure.

    """
    def __init__(self, dictionary, alpha=1.8, beta=5.0, threshold=0.0):
        self.dictionary = dictionary
        self.alpha = alpha
        self.beta = beta
        self.threshold = threshold
        super(LevenshteinSimilarityIndex, self).__init__()

    def most_similar(self, t1, topn=10):
        for _, (t2, similarity) in zip(range(topn), (
                (t2, similarity) for similarity, t2 in sorted(
                    (
                        (levsim(t1, t2, self.alpha, self.beta), t2)
                        for t2 in self.dictionary.values() if t1 != t2
                    ), reverse=True)
                if similarity > self.threshold)):
            yield (t2, similarity)
