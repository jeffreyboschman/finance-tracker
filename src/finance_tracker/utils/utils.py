import functools
import hashlib
import json


def cache_result(arg_name: str):
    """
    Decorator to cache the result of a function based on the specified argument's data.

    Args:
        arg_name (str): The name of the argument to use as a cache key. If None, raise
            an error.
    """
    cache = {}

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Determine which argument to use for the cache key
            if arg_name:
                if arg_name in kwargs:
                    key = kwargs[arg_name]
                else:
                    arg_names = func.__code__.co_varnames
                    key = args[arg_names.index(arg_name)]

                print(f"Using {key} as the inside cache key")
            else:
                raise ValueError(
                    "Must provide an arg_name to be used as the cache key."
                )

            # Fetch or generate the data
            result = func(*args, **kwargs)

            data_hash = hashlib.md5(
                json.dumps(key, sort_keys=True).encode()
            ).hexdigest()

            # Check if the data has changed
            if key in cache and cache[key]["hash"] == data_hash:
                # Return the cached result if the data hasn't changed
                print("Data has not changed. Using cached data.")

                return cache[key]["result"]

            # Otherwise, update the cache with the new data
            cache[key] = {"hash": data_hash, "result": result}
            print(f"Updating cache for key: {key}")
            return result

        return wrapper

    return decorator
