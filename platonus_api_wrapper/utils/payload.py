

def generate_payload(exclude_list=[], **kwargs):
    exclude_list.append("self")

    return {key: value for key, value in kwargs.items() if
            key not in exclude_list
            #and value
            and not key.startswith('_')}

