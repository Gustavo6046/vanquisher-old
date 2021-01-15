import nox
import nox_poetry.patch


@nox.session(python=['3.6', '3.7', '3.8', '3.9'])
def test(session: nox.sessions.Session):
    """
    Execute Pytest unit tests.
    """

    session.install(".") # dependencies

    session.install("pytest")
    session.run("pytest")

@nox.session(python=['3.6', '3.7', '3.8', '3.9'])
def lint(session: nox.sessions.Session):
    """
    Execute several linting checks: pylint, mypy, isort, and black.
    """

    session.install(".") # dependencies

    session.install("pylint", "mypy", "isort", "black")

    session.run("pylint", "vanquisher")
    session.run("mypy", "vanquisher")
    session.run("isort", "-c", "vanquisher")
    session.run("black", "-c", "vanquisher")
