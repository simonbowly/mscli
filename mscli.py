
import contextlib
import os

import appdirs
import click
from prompt_toolkit import prompt
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.history import FileHistory
from pygments.lexers.sql import SqlLexer
from pymssql import ProgrammingError
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from tabulate import tabulate


@click.command()
@click.option('--host', type=str)
@click.option('--port', type=int)
@click.option('--username', type=str)
@click.option('--password', type=str)
def cli(host, port, username, password):

    # Prompt configuration.
    sql_completer = WordCompleter([
        'SELECT', 'FROM', 'WHERE', 'ORDER BY', 'TOP',
        'INFORMATION_SCHEMA'
        ], ignore_case=True)
    config_dir = appdirs.user_config_dir('mscli')
    with contextlib.suppress(FileExistsError):
        os.makedirs(config_dir)
    history_file = os.path.join(config_dir, 'history.txt')
    prompt_kwargs = dict(
        history=FileHistory(history_file),
        auto_suggest=AutoSuggestFromHistory(),
        completer=sql_completer,
        lexer=SqlLexer,
        # multiline=True
        )

    # Connection configuration.
    engine = create_engine(f'mssql+pymssql://{username}:{password}@{host}:{port}/')

    # REPL.
    try:
        with engine.connect() as conn:
            try:
                while 1:
                    stmt = prompt('> ', **prompt_kwargs)
                    if stmt.strip() == '':
                        continue
                    try:
                        # Run query and display result.
                        result = conn.execute(stmt)
                        if result.returns_rows:
                            rows = list(result)
                            columns = result.keys()
                            output_str = str(tabulate(rows, columns, tablefmt='psql'))
                            if len(rows) > 10:
                                click.echo_via_pager(output_str)
                            else:
                                click.echo(output_str)
                        else:
                            click.echo('"result" does not return rows. Launching IPy to inspect ...')
                            from IPython import embed
                            embed()
                    except SQLAlchemyError as exec_error:
                        # Errors in the statement execution.
                        code, msg = exec_error.orig.args
                        msg = msg.decode()
                        click.echo(f'Error code {code}.\n{msg}')

            except (KeyboardInterrupt, EOFError) as bailout_error:
                click.echo('Exiting...')

        click.echo('Connection closed.')

    except SQLAlchemyError as connect_error:
        # Errors in establishing a connection at launch.
        code, msg = connect_error.orig.args[0]
        msg = msg.decode()
        click.echo(f'Error code {code}.\n{msg}')


if __name__ == '__main__':
    cli()
