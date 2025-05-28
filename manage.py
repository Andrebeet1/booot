#!/usr/bin/env python
import os
import sys

def main():
    """Point d'entrée pour les commandes de gestion Django."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aviatorbot.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Impossible d'importer Django. Assure-toi qu'il est installé "
            "et que ton environnement virtuel est activé."
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
