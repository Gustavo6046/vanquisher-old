import nox


@nox.session(python=['3.6', '3.7', '3.8', '3.9'])
def test(session):
    session.install("pytest")
    session.run("pytest")

@nox.session(python=['3.6', '3.7', '3.8', '3.9'])
def lint(session):
    session.install("pylint", "mypy", "isort", "black")
    session.run("pylint", "vanquisher")
    session.run("mypy", "vanquisher")
    session.run("isort", "-c", "vanquisher")
    session.run("black", "-c", "vanquisher")

