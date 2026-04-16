"""Entry point for the v2rayN application."""

import sys


def main() -> None:
    """Main entry point for the v2rayN application."""
    from v2rayn.views.app import run_app

    sys.exit(run_app(sys.argv))


if __name__ == "__main__":
    main()
