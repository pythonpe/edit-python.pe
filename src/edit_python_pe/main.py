from .app import MemberApp


def main() -> None:
    app = MemberApp()
    app.run()


if __name__ == "__main__":  # pragma: no cover
    main()
