"""Entry point for the v2rayN application."""

import sys


def main() -> int:
    """Main entry point for the v2rayN application.

    Returns:
        Exit code
    """
    try:
        from PySide6.QtWidgets import QApplication

        from v2rayn.manager.app_manager import AppManager
        from v2rayn.views.main_window import create_main_window

        app = QApplication(sys.argv)
        app.setApplicationName("v2rayN")
        app.setOrganizationName("v2rayN")

        # Initialize app manager
        manager = AppManager.get_instance()
        manager.initialize()

        # Create and show main window
        window = create_main_window()
        if window is None:
            print("Error: Failed to create main window. Ensure PySide6 is installed.")
            return 1

        window.show()
        return app.exec()

    except ImportError as e:
        print(f"Error: Missing dependency: {e}")
        print("Install required packages: pip install v2rayn[gui]")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
