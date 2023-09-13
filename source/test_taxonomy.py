import unittest
from taxonomy import *

class Test(unittest.TestCase):
    tax_id_list = ['9606', '8860', '1']
    test_hash = [{'scientific_name': 'root', 'tag': '', 'tax_division': 'UNC', 'tax_id': '1'},
                 {'scientific_name': 'Chloephaga melanoptera',
                  'tag': 'marine;marine_low_confidence;coastal_brackish;coastal_brackish_low_confidence;freshwater;freshwater_low_confidence;terrestrial;terrestrial_low_confidence',
                  'tax_division': 'VRT',
                  'tax_id': '8860'},
                 {'scientific_name': 'Homo sapiens',
                  'tag': '',
                  'tax_division': 'HUM',
                  'tax_id': '9606'}]
    portal_hit_hash = do_portal_api_tax_call("taxon", ['9606', '8860', '1'],
                                             ['tax_id', 'tax_division', 'tag', 'scientific_name'])

    def test_create_taxonomy_hash(self):
        hit_hash = create_taxonomy_hash(self.tax_id_list)
        self.assertListEqual(hit_hash, self.test_hash)

    def test_do_portal_api_tax_call(self):
        self.assertListEqual(self.portal_hit_hash, self.test_hash)

    def test_taxon_collection(self):

        taxon_collection_obj = taxon_collection(self.portal_hit_hash)
        taxon_obj = taxon_collection_obj.get_taxon_obj_by_id('8860')
        self.assertEqual(taxon_obj.tax_id,'8860')

    def test_get_all_taxon_obj_list(self):
        taxon_collection_obj = taxon_collection(self.portal_hit_hash)
        self.assertEqual(len(taxon_collection_obj.get_all_taxon_obj_list()), 3)

    def test_scientific_name(self):
        taxon_collection_obj = taxon_collection(self.portal_hit_hash)
        taxon_obj = taxon_collection_obj.get_taxon_obj_by_id('8860')
        self.assertEqual(taxon_obj.scientific_name,'Chloephaga melanoptera')

    def test_tag_status(self):
        taxon_collection_obj = taxon_collection(self.portal_hit_hash)
        taxon_obj = taxon_collection_obj.get_taxon_obj_by_id('8860')

        self.assertEqual(taxon_obj.isTerrestrial, False)
        self.assertEqual(taxon_obj.isMarine, False)
        self.assertEqual(taxon_obj.isCoastal, False)
        self.assertEqual(taxon_obj.isFreshwater, False)

if __name__ == '__main__':
    unittest.main()
