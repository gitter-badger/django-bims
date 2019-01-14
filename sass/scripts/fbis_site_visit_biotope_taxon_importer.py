from sass.models import (
    SiteVisitBiotopeTaxon,
    SiteVisit,
    TaxonAbundance,
    SassTaxon
)
from bims.models import Taxonomy, Biotope
from sass.scripts.fbis_importer import FbisImporter
from datetime import datetime


class FbisSiteVisitBiotopeTaxonImporter(FbisImporter):

    content_type_model = SiteVisitBiotopeTaxon
    table_name = 'SiteVisitBiotopeTaxon'

    def process_row(self, row, index):
        site_visit = self.get_object_from_uuid(
            column='SiteVisitID',
            model=SiteVisit
        )
        sass_taxon = self.get_object_from_uuid(
            column='TaxonID',
            model=SassTaxon
        )
        biotope = self.get_object_from_uuid(
            column='SassBiotopeID',
            model=Biotope
        )
        taxon_abundance = self.get_object_from_uuid(
            column='TaxonAbundanceID',
            model=TaxonAbundance
        )
        date = datetime.strptime(
            self.get_row_value('DateFrom'),
            '%m/%d/%y %H:%M:%S'
        )

        (
            site_visit_biotope,
            created,
        ) = SiteVisitBiotopeTaxon.objects.get_or_create(
            site_visit=site_visit,
            taxon=sass_taxon.taxon,
            biotope=biotope,
            taxon_abundance=taxon_abundance,
            date=date
        )
        self.save_uuid(
            uuid=self.get_row_value('SiteVisitBiotopeTaxonID'),
            object_id=site_visit_biotope.id
        )
