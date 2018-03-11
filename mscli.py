
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


__version__ = '0.1.0'


def get_all_tables(conn):
    databases = [
        entry[0] for entry in
        conn.execute('SELECT name FROM sys.databases')]
    query = ' union all '.join(
        f'SELECT * FROM {database}.INFORMATION_SCHEMA.tables'
        for database in databases
        if database not in {'master', 'tempdb', 'model', 'msdb'})
    run_query(conn, query)


def run_query(conn, stmt):
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
        # Error in the statement execution.
        code, msg = exec_error.orig.args
        msg = msg.decode()
        click.echo(f'Error code {code}.\n{msg}')


def process_input(conn, stmt):
    stmt = stmt.strip()
    if stmt == '':
        return
    elif stmt.startswith('\\'):
        command, *args = stmt[1:].split()
        if command == 'databases':
            query = 'SELECT name FROM sys.databases'
            click.echo(query)
            run_query(conn, query)
        elif command == 'tables':
            if len(args) == 0:
                get_all_tables(conn)
            else:
                database = args[0]
                query = f'SELECT * FROM {database}.INFORMATION_SCHEMA.tables'
                click.echo(query)
                run_query(conn, query)
        else:
            click.echo(f'Unknown command: {stmt}')
    else:
        run_query(conn, stmt)


@click.command()
@click.option('--host', type=str, prompt=True)
@click.option('--port', type=int, prompt=True)
@click.option('--username', type=str, prompt=True)
@click.option('--password', type=str, prompt=True, hide_input=True)
def cli(host, port, username, password):

    # Prompt configuration.
    sql_completer = WordCompleter([
        'SELECT', 'TOP' 'FROM', 'WHERE', 'ORDER BY',
        '\\databases', '\\tables',
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
        multiline=True,
        )

    # Connect and start REPL.
    try:
        engine = create_engine(
            f'mssql+pymssql://{username}:{password}@{host}:{port}/')
        with engine.connect() as conn:
            try:
                while 1:
                    stmt = prompt('> ', **prompt_kwargs)
                    process_input(conn, stmt)
            except (KeyboardInterrupt, EOFError) as bailout_error:
                click.echo('Exiting...')
        click.echo('Connection closed.')
    except SQLAlchemyError as connect_error:
        # Error in establishing a connection at launch.
        code, msg = connect_error.orig.args[0]
        msg = msg.decode()
        click.echo(f'Error code {code}.\n{msg}')


if __name__ == '__main__':
    cli()
