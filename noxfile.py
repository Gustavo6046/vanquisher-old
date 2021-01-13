import nox

@nox.session
def tests(session):
    session.install('pytest')
    session.run('pytest')

@nox.session
def lint(session):
    session.install('flake8', 'pylint', 'mypy')
    session.run('flake8', 'vanquisher')
    session.run('pylint', 'vanquisher')
    session.run('mypy', 'vanquisher')
