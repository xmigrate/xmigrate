import uuid

def unique_id_gen(name: str = "DEF") -> str:
    """
    creates a sha-1 encoded uuid with the name and returns it as a string.
    
    :param name: name for uuid creation
    """

    return(name + str(uuid.uuid5(uuid.uuid1(), name)))