"""Importe uniquement les valeurs d'un dump phpMyAdmin dans une base vide.

Sans --apply, analyse le fichier sans ouvrir de connexion. Les instructions
CREATE, ALTER, DROP, USE et SET du dump ne sont jamais exécutées.
"""
import argparse
from collections import Counter
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

SCHEMA = {
    "users": ("id", "username", "nom", "prenom", "telephone", "email", "password", "role"),
    "owners": ("id", "nom", "prenom", "matricule", "marque", "immatriculation", "telephone", "code_barre", "couleur", "statut"),
    "historique": ("id", "date", "owner_id", "etat", "heure"),
}
INSERT = re.compile(r"^INSERT INTO `([^`]+)`\s*\(([^)]+)\)\s+VALUES\s*(.*?);\s*$", re.M | re.S)
ESCAPES = {"0": "\0", "b": "\b", "n": "\n", "r": "\r", "t": "\t", "Z": "\x1a"}


def parse_values(text, width):
    """Lit seulement des chaînes MySQL, des entiers et NULL, jamais du code SQL."""
    position = 0

    def skip_space():
        nonlocal position
        while position < len(text) and text[position].isspace():
            position += 1

    def expect(character):
        nonlocal position
        skip_space()
        if position >= len(text) or text[position] != character:
            raise ValueError("Structure des valeurs SQL non prise en charge.")
        position += 1

    def value():
        nonlocal position
        skip_space()
        if position < len(text) and text[position] == "'":
            position += 1
            result = []
            while position < len(text):
                character = text[position]
                position += 1
                if character == "\\":
                    if position >= len(text):
                        break
                    escaped = text[position]
                    position += 1
                    result.append(ESCAPES.get(escaped, escaped))
                elif character == "'":
                    if position < len(text) and text[position] == "'":
                        result.append("'")
                        position += 1
                    else:
                        return "".join(result)
                else:
                    result.append(character)
            raise ValueError("Chaîne SQL non terminée.")
        match = re.match(r"NULL|-?\d+", text[position:])
        if not match:
            raise ValueError("Le dump contient une valeur autre qu'un littéral autorisé.")
        position += len(match[0])
        return None if match[0] == "NULL" else int(match[0])

    rows = []
    while True:
        expect("(")
        row = []
        for index in range(width):
            if index:
                expect(",")
            row.append(value())
        expect(")")
        rows.append(tuple(row))
        skip_space()
        if position == len(text):
            return rows
        expect(",")


def read_dump(path):
    text = path.read_text(encoding="utf-8-sig")
    data = {table: [] for table in SCHEMA}
    matches = list(INSERT.finditer(text))
    if not matches or len(matches) != len(re.findall(r"^INSERT INTO ", text, re.M)):
        raise ValueError("Format INSERT du dump non reconnu.")
    for match in matches:
        table, columns_text, values = match.groups()
        columns = tuple(column.strip().strip('`') for column in columns_text.split(','))
        if table not in SCHEMA or columns != SCHEMA[table]:
            raise ValueError(f"Table ou colonnes inattendues : {table}.")
        data[table].extend(parse_values(values, len(columns)))
    for table, rows in data.items():
        ids = [row[0] for row in rows]
        if len(ids) != len(set(ids)):
            raise ValueError(f"Identifiants dupliqués dans {table}.")
    owners = {row[0] for row in data['owners']}
    if any(row[2] not in owners for row in data['historique']):
        raise ValueError("Des historiques référencent un propriétaire absent du dump.")
    return data


def import_data(data):
    from app.database import Bdonnee

    db = Bdonnee()
    with db._connecter() as connection:
        try:
            with connection.cursor() as cursor:
                # Préserver les anciennes dates nulles, uniquement dans cette session.
                # Garder le mode strict pour refuser les troncatures et conversions.
                cursor.execute("SET SESSION sql_mode = 'STRICT_ALL_TABLES,NO_AUTO_VALUE_ON_ZERO,NO_ENGINE_SUBSTITUTION'")
                for table in SCHEMA:
                    cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
                    if cursor.fetchone()[0]:
                        raise ValueError(f"Import arrêté : {table} contient déjà des données.")
                for table in ('owners', 'users', 'historique'):
                    columns = ', '.join(f'`{column}`' for column in SCHEMA[table])
                    placeholders = ', '.join(['%s'] * len(SCHEMA[table]))
                    query = f"INSERT INTO `{table}` ({columns}) VALUES ({placeholders})"
                    for offset in range(0, len(data[table]), 500):
                        cursor.executemany(query, data[table][offset:offset + 500])
                    cursor.execute(f"SELECT {columns} FROM `{table}` ORDER BY id")
                    actual = cursor.fetchall()
                    expected = sorted(data[table], key=lambda row: row[0])
                    # MySQL convertit les DATE et TIME ; vérifier les valeurs reçues.
                    if len(actual) != len(expected) or [row[0] for row in actual] != [row[0] for row in expected]:
                        raise ValueError(f"Vérification des identifiants échouée : {table}.")
                    if table != 'historique' and list(actual) != expected:
                        raise ValueError(f"Vérification du contenu échouée : {table}.")
                    if table == 'historique':
                        for source, stored in zip(expected, actual):
                            stored_date = stored[1].isoformat() if hasattr(stored[1], 'isoformat') else stored[1]
                            hours, minutes, seconds = map(int, source[4].split(':'))
                            if (source[1] != stored_date or source[2:4] != stored[2:4]
                                    or stored[4].total_seconds() != hours * 3600 + minutes * 60 + seconds):
                                raise ValueError("Vérification du contenu échouée : historique.")
            connection.commit()
        except Exception:
            connection.rollback()
            raise
    print(f"Import validé dans {db.db_name} sur {db.host}:{db.port}.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dump', type=Path)
    parser.add_argument('--apply', action='store_true', help='Importer dans la base vide configurée.')
    args = parser.parse_args()
    data = read_dump(args.dump)
    for table, rows in data.items():
        print(f'{table}: {len(rows)} lignes')
    zero_dates = Counter(row[1] for row in data['historique'])['0000-00-00']
    print(f'Dates inconnues conservées (0000-00-00): {zero_dates}')
    if args.apply:
        import_data(data)
    else:
        print('Analyse uniquement : aucune donnée importée. Utiliser --apply pour importer.')


if __name__ == '__main__':
    main()
