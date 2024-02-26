import math
import statistics
from aleph_alpha_client import (
    Client,
    Prompt,
    SemanticEmbeddingRequest,
    SemanticRepresentation,
)

class Issue:
    """This class defines a IT Issue"""

    def __init__(
            self,
            client: Client,
            issue: str = "",
            category: str = "",
            description: str = "",
            solution: str = ""
    ):
        """Initialization of the issue object

            This function reads in all informations of an issue and
            embeds the texts using Aleph Alphas API
            Args:
                issue: The theme of an issue
                category: The category of an issue, single word
                description: The extensive description of an issue
                solution: The actions taken to resolve an issue
                client: The aleph alpha client
            Returns:
                Issue: An initialized issue object
        """
        self.issue = issue
        self.category = category
        self.description = description
        self.solution = solution
        self.client = client
        self.embeddings = self.embed_issues()


    def embed_issues(self) -> list:
        """Computes embeddings of an Issue object

            This function reads in all informations of an issue and
            embeds the texts using Aleph Alphas API
            Args:
                self: The issue object
            Returns:
                list: List of embeddings
        """
        return [self._embed(Prompt.from_text(prompt)) for prompt in [self.issue, self.category, self.description]]

    def _embed(self, prompt: Prompt):
        """Calls Aleph alphas API to compute embeddings


            Args:
                self: The issue object
                Prompt: An Promt object
            Returns:
                list: embedding vector
        """
        params = {
            "prompt": prompt,
            "representation": SemanticRepresentation.Symmetric,
            "compress_to_size": 128,
        }
        request = SemanticEmbeddingRequest(**params)
        response = self.client.semantic_embed(request=request, model="luminous-base")
        return response.embedding

    @staticmethod
    def compute_cosine_similarity(embedding_1: list, embedding_2: list)-> float:
        """Computes the cosine similarity of two embeddings

            Args:
                embedding_1: first embedding
                embedding_2: first embedding
            Returns:
                float: cosine similarity
        """
        sumxx, sumxy, sumyy = 0, 0, 0
        for i in range(len(embedding_1)):
            x = embedding_1[i]
            y = embedding_2[i]
            sumxx += x * x
            sumyy += y * y
            sumxy += x * y
        return sumxy / math.sqrt(sumxx * sumyy)

    def score_issue(self, issue2: "Issue") -> float:
        """Computes the similarity score of two Issues

            Based on the mean of the cosine similarity of each of the
            embedding vectors (Issue, Category, Description)
            a similarity score of two issues is computed.

            Args:
                self: first Issue
                input: Issue
            Returns:
                float: cosine similarity
        """
        embeddings = list(zip(self.embeddings, issue2.embeddings))
        # pdb.set_trace()
        scores = (
            self.compute_cosine_similarity(embedding_1, embedding_2)
            for embedding_1, embedding_2 in embeddings
        )
        return statistics.mean(scores)