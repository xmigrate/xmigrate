import uuid

def unique_id_gen(name: str = "default") -> str:
    """
    creates a sha-1 encoded uuid with the name and returns it as a string.
    
    :param name: name for uuid creation
    """

    return str(uuid.uuid5(uuid.uuid1(), name))