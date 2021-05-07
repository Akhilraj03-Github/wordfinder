"""
function: This module is to evaluate cluster result
mainly based on an assumption that we don't know the
true labels of clusters .
date:4.2.2021
"""
from sklearn import metrics
from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import DBSCAN
import numpy as np


class Evaluator(object):
    def __init__(self, X):
        self.X = X

    def kmeans_strategy(self, n_clusters: int):
        """
        kmeans cluster
        @param: n_clusters
        """
        kmeans = KMeans(n_clusters=n_clusters, random_state=0)
        kmeans.fit(self.X)
        labels = kmeans.labels_
        return labels

    def agglomerative_strategy(self, n_clusters: int):
        """
        agglomerative cluster
        @param: n_clusters
        """
        best_score, best_labels = -1., None
        for metric in ["cosine", "euclidean", "cityblock"]:
            model = AgglomerativeClustering(n_clusters=n_clusters,
                                            linkage="average", affinity=metric)
            model.fit(self.X)
            labels = model.labels_
            score = self.higher_better_score(labels)
            if best_score < score:
                best_score = score
                best_labels = labels

        return best_labels

    def get_best_n_clusters(self):
        """
        noise label is -1
        """
        db = DBSCAN(eps=0.3, min_samples=2).fit(self.X)
        labels = db.labels_
        n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
        return labels, n_clusters_

    def higher_better_score(self, labels):
        """
        higher value means better cluster result
        """
        # only one cluster
        if labels.min() == labels.max():
            return 1.0
        # cluster count equals to len of X
        if len(np.unique(labels)) == len(self.X):
            return 1.0
        return metrics.silhouette_score(self.X, labels, metric='euclidean')

    def nearer_zero_better_score(self, labels):
        """
        nearer zero means better cluster result
        """
        return metrics.davies_bouldin_score(self.X, labels)