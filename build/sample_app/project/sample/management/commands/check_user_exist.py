# -*- coding:utf-8 -*-
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Confirm existence of user'

    def add_arguments(self, parser):
        parser.add_argument('username', nargs='+', type=str)

    def handle(self, *args, **options):
        for username in options['username']:
            try:
                User.objects.get(username=username)
                print('True')
            except User.DoesNotExist:
                print('False')
