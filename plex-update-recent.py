import sys
from datetime import datetime, timedelta
from typing import Any

from plexapi.server import PlexServer

# Configure Variables
BASEURL = ""  # Enter your Plex server URL here, e.g. http://localhost:32400
TOKEN = ""  # Enter your Plex token here.  You can find your Plex token by following the instructions here: https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/
MAX_ATTEMPTS = 3  # Number of attempts to update metadata for each item before giving up


def _retry_update(item: Any, new_date: int, label: str, max_attempts: int) -> bool:
    """Attempt to update an item's addedAt date, retrying on failure.

    Returns True if the update succeeded, False if all attempts were exhausted.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            item.editAddedAt(new_date)
            if attempt > 1:
                print(f"Successfully updated metadata for {label} on retry {attempt}")
            else:
                print(f"Successfully updated metadata for {label}")
            return True
        except Exception as e:
            print(f"Attempt {attempt} failed for {label}: {e}")
            if attempt < max_attempts:
                print(f"Retrying ({attempt}/{max_attempts})...")
    print(f"Giving up on {label} after {max_attempts} attempts.")
    return False


def choose_media_type() -> tuple[str, str]:
    """Prompt the user to choose between TV Show and Movie."""
    while True:
        print("What type of media?")
        print("  1. TV Show")
        print("  2. Movie")
        choice = input("\nEnter number: ").strip()
        if choice == "1":
            return "show", "TV Shows"
        elif choice == "2":
            return "movie", "Movies"
        else:
            print("Invalid choice. Please enter 1 or 2.")


def find_title(plex: PlexServer, library: str) -> Any:
    """Prompt the user for a title and resolve it to a Plex media item."""
    while True:
        search_term = input("Enter title: ")
        results = plex.library.section(library).search(search_term)
        if not results:
            if (
                input(
                    f"No titles found matching '{search_term}'. Try again? (y/n): "
                ).lower()
                == "y"
            ):
                continue
            sys.exit("Exiting.")
        break

    # Try exact match first (case-insensitive)
    exact = [r for r in results if r.title.lower() == search_term.lower()]

    if len(exact) == 1:
        return exact[0]

    # If multiple exact matches, prompt user to select from exact matches
    if len(exact) > 1:
        candidates = exact
        header = "\nMultiple exact matches found:"
    else:
        candidates = results
        header = "\nNo exact match found. Partial matches:"

    while True:
        print(header)
        for i, result in enumerate(candidates, start=1):
            print(f"  {i}. {result.title} ({result.year})")
        if candidates is exact:
            prompt = "\nEnter number to select: "
        else:
            prompt = "\nEnter number to select, or 0 to exit: "
        try:
            choice = int(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue

        if candidates is not exact and choice == 0:
            sys.exit("Exiting.")
        if choice < 1 or choice > len(candidates):
            if input("Invalid selection. Try again? (y/n): ").lower() != "y":
                sys.exit("Exiting.")
            continue
        return candidates[choice - 1]


def get_days() -> int:
    """Prompt the user for a number of days in the past."""
    while True:
        try:
            value = int(input("Enter number of days in the past: "))
            if value <= 0:
                print("Please enter a positive integer.")
                continue
        except ValueError:
            print("Invalid input. Please enter a valid integer.")
            continue
        return value


def connect_to_plex(baseurl: str, token: str) -> PlexServer:
    """Connect to a Plex server and return a PlexServer instance."""
    try:
        return PlexServer(baseurl, token)
    except Exception as e:
        sys.exit(f"Failed to connect to Plex server: {e}")


def update_media(media: Any, media_type: str, new_date: int, max_attempts: int) -> None:
    """Update the addedAt date for a media item and its episodes (if a show)."""
    label = f"{media_type} '{media.title}'"

    if not _retry_update(media, new_date, label, max_attempts):
        return

    if media_type != "show":
        return

    # Update the addedAt.value for each episode of the show
    for episode in media.episodes():
        ep_label = f"episode S{episode.parentIndex:02d}xE{episode.index:02d}: '{episode.title}'"
        _retry_update(episode, new_date, ep_label, max_attempts)


# Main execution
if __name__ == "__main__":
    try:
        # Connect to Plex server
        plex = connect_to_plex(BASEURL, TOKEN)

        # Get user inputs
        chosen_type, library = choose_media_type()
        media = find_title(plex, library)
        num_days = get_days()

        # Calculate date
        parse_date = datetime.now() - timedelta(days=num_days)
        new_date = int(parse_date.timestamp())

        if chosen_type == "movie":
            print(
                f"\nUpdating metadata for '{media.title}' to {parse_date.strftime('%Y-%m-%d %H:%M:%S')}..."
            )
            confirm = input("Proceed? (y/n): ").lower()
            if confirm != "y":
                sys.exit("Process cancelled by user.")
            update_media(media, chosen_type, new_date, MAX_ATTEMPTS)
        else:
            episodes = media.episodes()
            print(
                f"\nUpdating metadata for '{media.title}' and {len(episodes)} episodes to {parse_date.strftime('%Y-%m-%d %H:%M:%S')}..."
            )
            confirm = input("Proceed? (y/n): ").lower()
            if confirm != "y":
                sys.exit("Process cancelled by user.")
            update_media(media, chosen_type, new_date, MAX_ATTEMPTS)

    except KeyboardInterrupt:
        sys.exit("\nProcess interrupted by user.")

    except SystemExit:
        raise

    except Exception as e:
        sys.exit(f"Unexpected error: {e}")
