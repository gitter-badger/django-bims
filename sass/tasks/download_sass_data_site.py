# coding=utf-8
import csv
import logging
from celery import shared_task
from django.db.models import (
    Case, When, F, Count, Sum, FloatField, Q, Value, CharField
)
from django.db.models.functions import Cast, Concat
from sass.models.site_visit import SiteVisit

from bims.api_views.search import CollectionSearch
from sass.models import SiteVisitTaxon, SassTaxon
from geonode.people.models import Profile
from bims.models.location_context import LocationContext
from bims.download.csv_download import send_csv_via_email
from sass.serializers.sass_data_serializer import SassDataSerializer, SassTaxonDataSerializer
from sass.serializers.sass_data_serializer import SassSummaryDataSerializer

logger = logging.getLogger('bims')


@shared_task(name='sass.tasks.download_sass_data_site', queue='update')
def download_sass_data_site_task(
        filename, filters, path_file, user_id, send_email = False):
    from bims.utils.celery import memcache_lock

    user = Profile.objects.get(id=user_id)

    lock_id = '{0}-lock-{1}'.format(
        filename,
        len(filters)
    )
    oid = '{0}'.format(filename)

    with memcache_lock(lock_id, oid) as acquired:
        if acquired:
            search = CollectionSearch(filters)
            context = {
                'filters': filters
            }
            collection_records = search.process_search()
            site_visit_taxon = SiteVisitTaxon.objects.filter(
                id__in=collection_records
            ).order_by('site_visit__site_visit_date')
            serializer = SassDataSerializer(
                site_visit_taxon,
                many=True,
                context=context
            )
            headers = serializer.data[0].keys()
            rows = serializer.data

            formatted_headers = []
            # Rename headers
            for header in headers:
                formatted_headers.append(header.replace('_', ' ').capitalize())

            with open(path_file, 'w') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=formatted_headers)
                writer.writeheader()
                writer.fieldnames = headers
                for row in rows:
                    try:
                        writer.writerow(row)
                    except ValueError:
                        writer.fieldnames = row.keys()
                        writer.writerow(row)

            if send_email:
                send_csv_via_email(
                    user=user,
                    csv_file=path_file,
                    file_name=filters.get('csvName', 'SASS-Data'),
                    download_request_id=filters.get(
                        'downloadRequestId', ''
                    )
                )

            return
    logger.info(
        'Csv %s is already being processed by another worker',
        filename)


@shared_task(name='sass.tasks.download_sass_summary_data', queue='update')
def download_sass_summary_data_task(
        filename, filters, path_file, user_id, send_email = False):
    from bims.utils.celery import memcache_lock
    from bims.models.source_reference import SourceReference
    import random

    user = Profile.objects.get(id=user_id)

    lock_id = '{0}-lock-{1}'.format(
        filename,
        len(filters)
    )
    oid = random.randint(1, 101)
    with memcache_lock(lock_id, oid) as acquired:
        if acquired:
            search = CollectionSearch(filters)
            context = {
                'filters': filters
            }

            collection_records = search.process_search()
            collection_ids = list(
                collection_records.values_list('id', flat=True))
            # Get SASS data
            site_visit_taxa = SiteVisitTaxon.objects.filter(
                id__in=collection_ids
            )
            summary = site_visit_taxa.annotate(
                date=F('site_visit__site_visit_date'),
            ).values('date').annotate(
                count=Count('sass_taxon'),
                sampling_date=F('site_visit__site_visit_date'),
                full_name=Concat(
                    'survey__owner__first_name',
                    Value(' '),
                    'survey__owner__last_name',
                    output_field=CharField()
                )
            ).values('count', 'sampling_date', 'full_name').annotate(
                sass_score=Sum(Case(
                    When(
                        condition=Q(site_visit__sass_version=5,
                                    sass_taxon__sass_5_score__isnull=False),
                        then='sass_taxon__sass_5_score'),
                    default='sass_taxon__score'
                )),
                sass_id=F('site_visit__id'),
                FBIS_site_code=Case(
                    When(site_visit__location_site__site_code__isnull=False,
                         then='site_visit__location_site__site_code'),
                    default='site_visit__location_site__name'
                ),
                site_id=F('site_visit__location_site__id'),
                sass_version=F('site_visit__sass_version'),
                site_description=F(
                    'site_visit__location_site__site_description'),
                river_name=Case(
                    When(site_visit__location_site__river__isnull=False,
                         then='site_visit__location_site__river__name'),
                    default=Value('-')
                ),
                latitude=F('site_visit__location_site__latitude'),
                longitude=F('site_visit__location_site__longitude'),
                source_reference=F('source_reference'),
                ecological_category=F('site_visit__'
                                      'sitevisitecologicalcondition__'
                                      'ecological_condition__category')
            ).annotate(
                aspt=Cast(F('sass_score'), FloatField()) / Cast(F('count'),
                                                                FloatField()),
            ).order_by('sampling_date')
            context['location_contexts'] = LocationContext.objects.filter(
                site__in=site_visit_taxa.values('site_visit__location_site')
            )
            context['default_source_reference'] = (
                SourceReference.objects.filter(
                    sourcereferencedatabase__source__name__icontains=
                    'rivers database'
                ).first()
            )

            serializer = SassSummaryDataSerializer(
                summary,
                many=True,
                context=context
            )
            headers = serializer.data[0].keys()
            rows = serializer.data
            formatted_headers = []

            # Rename headers
            for header in headers:
                header_split = [
                    word[0].upper() + word[1:] for word in header.split('_')
                ]
                header = ' '.join(header_split)
                formatted_headers.append(header)

            with open(path_file, 'w') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=formatted_headers)
                writer.writeheader()
                writer.fieldnames = headers
                for row in rows:
                    try:
                        writer.writerow(row)
                    except ValueError:
                        writer.fieldnames = row.keys()
                        writer.writerow(row)

            if send_email:
                send_csv_via_email(
                    user=user,
                    csv_file=path_file,
                    file_name=filters.get('csvName', 'SASS-Summary'),
                    download_request_id=filters.get(
                        'downloadRequestId', ''
                    )
                )

            return
    logger.info(
        'Csv %s is already being processed by another worker',
        filename)


@shared_task(name='sass.tasks.download_sass_taxon_data', queue='update')
def download_sass_taxon_data_task(
        location_site_id,
        filename,
        filters,
        path_file,
        user_id,
        send_email=False):
    from bims.utils.celery import memcache_lock

    user = Profile.objects.get(id=user_id)

    lock_id = '{0}-lock'.format(
        filename
    )
    oid = '{0}'.format(filename)

    with memcache_lock(lock_id, oid) as acquired:
        if acquired:
            sass_site_visits = SiteVisit.objects.filter(
                location_site_id=location_site_id
            ).order_by('-site_visit_date')
            location_site = sass_site_visits.first().location_site
            sass_taxa = SassTaxon.objects.filter(
                sass_5_score__isnull=False
            ).order_by(
                'display_order_sass_5'
            )

            site_code = (
                location_site.site_code
                if location_site.site_code else
                '-'
            )
            river = (
                location_site.river.name
                if location_site.river else
                '-'
            )
            sampling_dates = ['Sampling date']
            taxon_data = []
            sass_score = ['SASS SCORE']
            number_of_taxa = ['NUMBER OF TAXA']
            aspt = ['ASPT']

            for sass_taxon in sass_taxa:
                taxon_data.append(
                    [sass_taxon.taxon_sass_4 if
                     sass_taxon.taxon_sass_4 else sass_taxon.taxon_sass_5])

            for sass_site_visit in sass_site_visits:
                sampling_dates.append(
                    sass_site_visit.site_visit_date
                )
                _number_of_taxa = 0
                _sass_score = 0
                for index in range(len(taxon_data)):
                    sass_taxon = sass_taxa[index]
                    site_visit_taxa = SiteVisitTaxon.objects.filter(
                        site_visit=sass_site_visit,
                        sass_taxon=sass_taxon
                    )
                    if site_visit_taxa.count() > 0:
                        taxon_abundance = (
                          site_visit_taxa.first().taxon_abundance.abc
                        )
                        _number_of_taxa += 1
                        _sass_score += sass_taxon.sass_5_score
                    else:
                        taxon_abundance = ''
                    taxon_data[index].append(taxon_abundance)

                number_of_taxa.append(_number_of_taxa)
                sass_score.append(_sass_score)
                try:
                    aspt_score = round(_sass_score/_number_of_taxa, 2)
                except:  # noqa
                    aspt_score = 0
                aspt.append(aspt_score)

            site_codes = [
                'Site Code',
                *[site_code for _ in range(len(sampling_dates)-1)]
            ]
            rivers = [
                'River',
                *[river for _ in range(len(sampling_dates)-1)]
            ]

            with open(path_file, 'w') as csv_file:
                writer = csv.writer(
                    csv_file,
                    delimiter=',')
                for row in [
                    site_codes, sampling_dates, rivers,
                    *taxon_data, sass_score, number_of_taxa, aspt]:
                    writer.writerow(row)

            if send_email:
                send_csv_via_email(
                    user=user,
                    csv_file=path_file,
                    file_name=filters.get('csvName', 'SASS-Data'),
                    download_request_id=filters.get(
                        'downloadRequestId', ''
                    )
                )

            return
    logger.info(
        'Csv %s is already being processed by another worker',
        filename)
