import os
import textwrap
from argparse import RawTextHelpFormatter

from django.conf import settings
from django.core.management.base import BaseCommand

from base.choices import FileReferencePrivacy


class Command(BaseCommand):
    help = textwrap.dedent(
        """
        Clear FileStore
    """
    )

    def create_parser(self, prog_name, subcommand):
        parser = super(Command, self).create_parser(prog_name, subcommand)
        parser.formatter_class = RawTextHelpFormatter
        return parser

    def add_arguments(self, parser):
        parser.add_argument(
            "storages", nargs="*", type=str, help="Specific media store."
        )
        parser.add_argument(
            "--empty-dir",
            action="store_true",
            dest="empty_dir",
            help="Delete empty directory in filestore and media stores.",
        )

    def handle(self, *args, **options):
        # Determine which apps to process
        storages = options["storages"]
        if not storages:
            storages = [item[0].lower() for item in FileReferencePrivacy.choices] + ['_filestore']

        # Remove empty directories
        if options["empty_dir"]:
            root_dir = settings.MEDIA_ROOT
            for storage in storages:
                self._remove_empty_directories(os.path.join(root_dir, storage), remove_root=False)

    # Utils

    def _remove_empty_directories(self, path, remove_root=False):
        if not os.path.isdir(path):
            return

        # remove empty subfolders
        files = os.listdir(path)
        if len(files):
            for f in files:
                fullpath = os.path.join(path, f)
                if os.path.isdir(fullpath):
                    self._remove_empty_directories(fullpath, remove_root=True)

        # if folder empty, delete it
        files = os.listdir(path)
        if len(files) == 0 and remove_root:
            os.rmdir(path)
