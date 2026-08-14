

def find_key_rec(obj, key):
    SENTINAL = object()

    def find_key_rec2(obj):
        if isinstance(obj, dict):
            if key in obj:
                return [], (obj.get(key, SENTINAL) or SENTINAL)

            for k, v in obj.items():
                if (answer := find_key_rec2(v)) is not None:
                    p, a = answer
                    return ([k] + p), a

        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                if (answer := find_key_rec2(v)) is not None:
                    p, a = answer
                    return ([i] + p), a
        return None

    return find_key_rec2(obj=obj)

def find_keys_rec(obj, key, with_path=False):
    assert isinstance(key, str)
    result = []
    stack = []

    def foo(obj):
        if isinstance(obj, dict):
            if key in obj:
                # Create a new list
                result.append((stack + [key], obj[key]) if with_path else obj[key])
            for k, v in obj.items():
                stack.append(k)
                foo(v)
                stack.pop()
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                stack.append(i)
                foo(v)
                stack.pop()
        elif obj == key:
            result.append((stack.copy(), key) if with_path else key)

    foo(obj)
    return result
