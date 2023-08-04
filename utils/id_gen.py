import uuid


def unique_id_gen() -> str:
    """
    creates a sha-1 encoded uuid and returns it as a string.
    """

    return str(uuid.uuid5(uuid.uuid1(), "DEFAULT"))