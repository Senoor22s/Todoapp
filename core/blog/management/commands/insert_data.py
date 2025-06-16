from django.core.management.base import BaseCommand
from faker import Faker
from ...models import Task
from accounts.models import User,Profile
import random

class Command(BaseCommand):

    def __init__(self,*args,**kwargs):
        super(BaseCommand,self).__init__(*args,**kwargs)
        self.fake=Faker()

    def handle(self,*args,**options):
        user=User.objects.create_user(email=self.fake.email(),password='mxgyuirt22ali')
        profile=Profile.objects.get(user=user)
        profile.first_name=self.fake.first_name()
        profile.last_name=self.fake.last_name()
        profile.description=self.fake.paragraph(nb_sentences=5)
        profile.save()

        for _ in range(5):
            Task.objects.create(
                user=user,
                title=self.fake.paragraph(nb_sentences=1),
                description=self.fake.paragraph(nb_sentences=5),
                is_done=random.choice([True,False]),
            )
