import time


def find_duplicates(addresses):
    """Return the addresses that appear more than once."""
    seen = set()
    duplicates = set()
    for address in addresses:
        if address in seen:
            if address not in duplicates:
                duplicates.add(address)
        else:
            seen.add(address)
    return duplicates


def make_addresses(unique_count):
    """Build a list where every address appears twice."""
    unique = [f"10.{i // 65025}.{(i // 255) % 255}.{i % 255}" for i in range(unique_count)]
    return unique + unique


if __name__ == "__main__":
    addresses = make_addresses(8000)
    print("Checking", len(addresses), "addresses...")

    start = time.perf_counter()
    result = find_duplicates(addresses)
    elapsed = time.perf_counter() - start

    print("Duplicates found:", len(result))
    print(f"Time taken: {elapsed:.2f} seconds")
