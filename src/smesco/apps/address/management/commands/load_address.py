from humanize import naturaltime
from datetime import timedelta, datetime

from django.core.management import BaseCommand
from django.utils.timezone import now
from django.utils import timezone

from apps.address.models import State, District, Subdistrict, Village

LEVEL = {
    'Kab': 'district',
    'Kota': 'city'
}

ID = 'ID'


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--json-file',
            help='json file that contain address data',
        )

    def report_progress(self, iteration: int, total: int, starting_time: datetime):
        bar_size = 20
        percent = "{0:.1f}".format(100 * (iteration / float(total)))
        filled_length = int(bar_size * iteration // total)
        bar = '█' * filled_length + '-' * (bar_size - filled_length)

        runtime = ''
        if starting_time:
            runtime = naturaltime(now() - starting_time)

        ending_time = ''
        if starting_time:
            seconds_from_start = (now() - starting_time).total_seconds()
            per_second = int(iteration / seconds_from_start)
            try:
                ending_time = naturaltime(timedelta(seconds=(-1 * ((total - iteration) / per_second))))
            except (TypeError, ZeroDivisionError):
                ending_time = '???'

        self.stdout.write(
            f'\r |{bar}| {percent}% (Dump Rate: {per_second}/s) [Started: {runtime} - Done: {ending_time}]',
            ending="\r"
        )

        # Print New Line on Complete
        if iteration == total:
            self.stdout.write('\n')

    def handle(self, *args, **options):
        import json

        try:
            start = timezone.now()
            with open(options.get('json_file'), encoding='utf-8') as data_file:
                addresses = json.loads(data_file.read())

            total_address = len(addresses)
            self.stdout.write(f'Preparing dump {total_address} Address with their state data into Database')

            starting_time = now()

            for number, address in enumerate(addresses):
                state, state_created = State.objects.get_or_create(name=address.get('state'), country_id=ID)
                self.load_address(state, address)
                self.report_progress(number, total_address, starting_time)

            end = timezone.now()
            self.stdout.write(
                f"DONE, Address data already dumped into database. It took {(end - start).seconds} SECONDS")

        except Exception as e:
            raise e

    def load_address(self, state, address):
        district, district_created = District.objects.get_or_create(name=address.get('district'),
                                                                    state=state)
        self.load_district_address(address, district)

    def load_district_address(self, address, district):
        sub_district, sub_district_created = Subdistrict.objects.get_or_create(
            name=address.get('subdistrict'),
            district=district)
        if sub_district_created:
            village, created = Village.objects.get_or_create(name=address.get('village'),
                                                             subdistrict=sub_district)
            village.postcode = address.get('postcode')
            village.save()
        else:
            village, created = Village.objects.get_or_create(name=address.get('village'),
                                                             subdistrict=sub_district)
            village.postcode = address.get('postcode')
            village.save()
