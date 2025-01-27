from bims.tasks.collection_record import *  # noqa
from bims.tasks.search import *  # noqa
from bims.tasks.location_site import *  # noqa
from bims.tasks.chemical_record import *  # noqa
from bims.tasks.location_context import *  # noqa
from bims.tasks.source_reference import *  # noqa
from bims.tasks.taxa_upload import *  # noqa
from bims.tasks.collections_upload import *  # noqa
from bims.tasks.harvest_collections import *  # noqa
from bims.tasks.duplicate_records import *  # noqa
from bims.tasks.download_taxa_list import *  # noqa
from bims.tasks.taxon_extra_attribute import *  # noqa
from bims.tasks.clean_data import *  # noqa
from bims.tasks.email_csv import *  # noqa


@shared_task(name='bims.tasks.test_celery', queue='update')
def test_celery():
    print('testing')
