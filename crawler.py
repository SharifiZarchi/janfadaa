import requests
import json
import os

URL = "https://janfadaa.ir/ajax"
OUTPUT_FILE = "janfadaa_comments_chain.jsonl"
POINTER_FILE = "janfadaa_pointer.txt"
BROKEN_POINTERS_FILE = "broken_pointers.txt"

USE_PROXY = False
PROXIES = {"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"}


def log_broken_pointer(pointer):
    """Append a real broken pointer to the text file."""
    with open(BROKEN_POINTERS_FILE, "a") as f:
        f.write(str(pointer) + "\n")


def main():
    print("==================================================")
    print("JANFADAA CRAWLER - VERIFIED/GUESSED POINTER")
    print("==================================================")

    # (1) pointer = 0 (or the value in janfada_pointer.txt if exists)
    pointer = "0"
    if os.path.exists(POINTER_FILE):
        with open(POINTER_FILE, "r") as f:
            content = f.read().strip()
            if content:
                pointer = content
                print(f"[*] Resuming from previous pointer: {pointer}")

    session = requests.Session()
    if USE_PROXY:
        session.proxies.update(PROXIES)
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "identity",
        }
    )

    # We assume the starting pointer is VERIFIED.
    is_verified_pointer = True

    while True:
        attempts = 0
        success = False
        result = {}

        # Prepare POST data
        data = {"action": "getComments"}
        if str(pointer) != "0":
            data["pointer"] = str(pointer)

        print(
            f"\n[*] Processing pointer: {pointer} (Type: {'VERIFIED' if is_verified_pointer else 'GUESSED'})"
        )

        max_attempts = 20 if is_verified_pointer else 1

        # (2) Try max_attempts times without pause, each time 1000 ms timeout
        while attempts < max_attempts:
            attempts += 1
            print(f"    - Attempt {attempts}/{max_attempts} ...", end=" ", flush=True)

            try:
                response = session.post(URL, data=data, timeout=1.0)

                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        success = True
                        print("SUCCESS")
                        break
                    else:
                        print("API returned success=false")
                else:
                    print(f"HTTP {response.status_code}")
            except Exception as e:
                # Catch timeout or network drop without crashing
                print("FAILED (timeout or network error)")

        # (3) If response received
        if success:
            comments = result.get("data", {}).get("all", [])
            next_pointer = result.get("data", {}).get("next", 0)

            # Add it to output json file
            # Reverting back to line-by-line append (.jsonl) to completely bypass the f.read(10) corruption crash you saw
            with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                for comment in comments:
                    f.write(json.dumps(comment, ensure_ascii=False) + "\n")

            print(f"  ✓ Saved {len(comments)} comments.")

            if str(next_pointer) == str(pointer) or next_pointer == 0:
                print("[*] Reached end of comments chain. Done!")
                break

            # Update pointer and go back to (2) with new pointer
            pointer = str(next_pointer)
            is_verified_pointer = (
                True  # The new pointer came from the server, so it's VERIFIED
            )

            # Save the new real pointer
            with open(POINTER_FILE, "w") as f:
                f.write(pointer)

        # (4) If response not received in max_attempts
        else:
            print(f"[!] Exhausted {max_attempts} attempts for pointer {pointer}.")

            # if the pointer value is verified add it to broken_pointers.txt
            if is_verified_pointer:
                print(f"    -> Pointer is VERIFIED. Adding to {BROKEN_POINTERS_FILE}")
                log_broken_pointer(pointer)

            # then reduce the pointer value by 100 and mark it as guessed and continue from (2)
            try:
                new_ptr = int(pointer) - 100
                if new_ptr < 0:
                    new_ptr = 0
                pointer = str(new_ptr)
                is_verified_pointer = False
                print(
                    f"    -> Pointer reduced by 100. New pointer: {pointer} (Type: GUESSED)"
                )

                # Save this fake pointer state just in case the script is killed
                with open(POINTER_FILE, "w") as f:
                    f.write(pointer)
            except ValueError:
                print("[!] Pointer is not an integer. Cannot reduce. Stopping.")
                break


if __name__ == "__main__":
    main()
