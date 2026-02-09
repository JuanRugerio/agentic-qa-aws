from pinecone import Pinecone
from pinecone.exceptions import NotFoundException

#Connects with pc via api key, verfies whether index exists, creates if not. And returns it.
def init_pinecone(api_key: str, index_name: str, dim: int):
    """
    Initialize Pinecone client and return an index handle.
    Creates the index if it does not exist.
    """
    pc = Pinecone(api_key=api_key)

    try:
        index = pc.Index(index_name)
        # Touch index to confirm it exists
        index.describe_index_stats()
    except NotFoundException:
        pc.create_index(
            name=index_name,
            dimension=dim,
            metric="cosine"
        )
        index = pc.Index(index_name)

    return index
