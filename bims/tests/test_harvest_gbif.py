import json
import os
import mock
import requests
from django.test import TestCase
from urllib3.exceptions import ProtocolError

from bims.models import Survey
from bims.tests.model_factories import (
    BiologicalCollectionRecordF,
    TaxonomyF, BiologicalCollectionRecord
)
from bims.scripts.import_gbif_occurrences import import_gbif_occurrences

test_data_directory = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'data')

def mocked_gbif_data(url):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    response_file = 'gbif_occurrences.json'
    response_path = os.path.join(
        test_data_directory, response_file)
    if os.path.exists(response_path):
        response_data = open(response_path)
        json_data = response_data.read()
        response_data.close()
        return MockResponse(json.loads(json_data), 200)
    return ''


def mocked_request_protocol_error(url):
    raise ProtocolError('Connection broken')


def mocked_request_http_error(url):
    e = requests.HTTPError('error')
    e.response = mock.MagicMock()
    e.response.status_code = 404
    e.response.content = 'Error Code'
    e.message = 'error message'
    raise e


class TestHarvestGbif(TestCase):
    def setUp(self) -> None:
        self.taxonomy = TaxonomyF.create(
            gbif_key=1
        )

    def tearDown(self) -> None:
        BiologicalCollectionRecord.objects.filter(
            taxonomy=self.taxonomy
        ).delete()
        self.taxonomy.delete()

    @mock.patch('requests.get', mock.Mock(
        side_effect=mocked_gbif_data))
    def test_harvest_gbif(self):
        status = import_gbif_occurrences(self.taxonomy)
        self.assertEqual(status, 'Finish')
        self.assertEqual(
            BiologicalCollectionRecord.objects.filter(
                owner__username='GBIF',
                taxonomy=self.taxonomy,
                source_reference__source_name='Global Biodiversity '
                                              'Information Facility (GBIF)'
            ).count(), 5
        )
        self.assertTrue(
            Survey.objects.filter(
                owner__username='GBIF',
                biological_collection_record__taxonomy=self.taxonomy,
                validated=True
            ).exists()
        )

    @mock.patch('requests.get', mock.Mock(
        side_effect=mocked_gbif_data))
    def test_harvest_gbif_multiple_objects_returned(self):
        BiologicalCollectionRecordF.create(
            upstream_id="2563631087",
            taxonomy=self.taxonomy,
        )
        BiologicalCollectionRecordF.create(
            upstream_id="2563631087",
            taxonomy=self.taxonomy
        )
        status = import_gbif_occurrences(self.taxonomy)
        self.assertEqual(status, 'Finish')
        self.assertEqual(
            BiologicalCollectionRecord.objects.filter(
                owner__username='GBIF',
                taxonomy=self.taxonomy,
                source_reference__source_name='Global Biodiversity '
                                              'Information Facility (GBIF)'
            ).count(), 5
        )

    @mock.patch('requests.get', mock.Mock(
        side_effect=mocked_request_http_error
    ))
    def test_harvest_gbif_http_error(self):
        status = import_gbif_occurrences(self.taxonomy)
        self.assertEqual(status, 'error message')

    @mock.patch('requests.get', mock.Mock(
        side_effect=mocked_request_protocol_error))
    def test_harvest_gbif_protocol_error(self):
        status = import_gbif_occurrences(self.taxonomy)
        self.assertEqual(status, 'Connection broken')
