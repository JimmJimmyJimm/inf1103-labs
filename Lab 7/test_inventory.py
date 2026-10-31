import contextlib
import io
import json
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest
from unittest.mock import patch

from can_be_shipped import CanBeShipped
from digital_product import DigitalProduct
from physical_product import PhysicalProduct
from product import Product
from inventory_manager import Inventory, load_inventory, save_inventory
import main


class ProductTests(unittest.TestCase):
    def test_abstract_contracts(self):
        with self.assertRaises(TypeError):
            Product('P', 'Name', 1, 2)
        with self.assertRaises(TypeError):
            CanBeShipped()

    def test_inheritance_and_shipping(self):
        for weight, cost in [(0, 0), (0.5, 2.5), (2, 10), (10, 50)]:
            with self.subTest(weight=weight):
                product = PhysicalProduct('P', 'Name', 1, 2, weight)
                self.assertIsInstance(product, Product)
                self.assertIsInstance(product, CanBeShipped)
                self.assertEqual(product.get_weight(), weight)
                self.assertEqual(product.calculate_shipping_cost(), cost)
                self.assertIn('shipping', product.get_fulfilment_info())
        product = DigitalProduct('D', 'File', 2, 3, 12)
        self.assertIsInstance(product, Product)
        self.assertEqual(product.get_download_size(), 12)
        self.assertNotIsInstance(product, CanBeShipped)
        self.assertFalse(hasattr(product, 'calculate_shipping_cost'))
        self.assertIn('digitally', product.get_fulfilment_info())

    def test_display_reuses_parent(self):
        for product, extra in [(PhysicalProduct('P', 'Box', 1, 2, 3), 'Weight: 3 kg'),
                               (DigitalProduct('P', 'Box', 1, 2, 3), 'Download size: 3 MB')]:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                product.display_information()
            self.assertIn('ID: P | Name: Box | Price: $1.00 | Stock: 2', output.getvalue())
            self.assertIn(extra, output.getvalue())
            with patch.object(Product, 'display_information') as parent:
                with contextlib.redirect_stdout(io.StringIO()):
                    product.display_information()
                parent.assert_called_once_with()

    def test_invalid_numbers(self):
        for value in [-1, float('nan'), float('inf'), -float('inf'), True, '2']:
            for factory in [PhysicalProduct, DigitalProduct]:
                with self.subTest(value=value, factory=factory):
                    with self.assertRaises(ValueError):
                        factory('P', 'Name', 1, 1, value)
                    with self.assertRaises(ValueError):
                        factory('P', 'Name', value, 1, 1)
        for stock in [-1, 1.5, True, '2']:
            with self.assertRaises(ValueError):
                DigitalProduct('P', 'Name', 1, stock, 1)
        for product_id, name in [('', 'Name'), ('P', ' ')]:
            with self.assertRaises(ValueError):
                DigitalProduct(product_id, name, 1, 1, 1)

    def test_oversized_numbers_are_validation_errors(self):
        for product_class in (PhysicalProduct, DigitalProduct):
            with self.subTest(product_class=product_class):
                with self.assertRaises(ValueError):
                    product_class('P', 'Large price', 10 ** 400, 1, 1)
                with self.assertRaises(ValueError):
                    product_class('P', 'Large measurement', 1, 1, 10 ** 400)
        with self.assertRaises(ValueError):
            PhysicalProduct('P', 'Shipping overflow', 1, 1, 1e308)

    def test_stock_validation(self):
        product = DigitalProduct('D', 'File', 2, 3, 12)
        for value in [-1, 1.5, True, '2']:
            self.assertFalse(product.update_stock(value))
            self.assertEqual(product.get_stock(), 3)
        self.assertTrue(product.update_stock(0))
        self.assertEqual(product.get_stock(), 0)


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / 'inventory.json'
        self.inventory = Inventory()
        self.inventory.add_product(PhysicalProduct('P', 'Box', 3, 4, 2))
        self.inventory.add_product(DigitalProduct('D', 'File', 5, 6, 100))
        self.output = io.StringIO()
        self.redirect = contextlib.redirect_stdout(self.output)
        self.redirect.__enter__()
        self.addCleanup(self.redirect.__exit__, None, None, None)

    def test_collection_operations(self):
        self.assertFalse(self.inventory.add_product(DigitalProduct('P', 'Other', 1, 1, 1)))
        self.assertIsNone(self.inventory.search_product('missing'))
        self.assertTrue(self.inventory.search_product('P').update_stock(10))
        self.inventory.get_products().clear()
        self.assertEqual(len(self.inventory.get_products()), 2)
        self.inventory.display_all()
        self.assertIn('Weight:', self.output.getvalue())
        self.assertIn('Download size:', self.output.getvalue())
        Inventory().display_all()
        self.assertIn('No products found.', self.output.getvalue())

    def test_round_trip(self):
        save_inventory(self.inventory, self.path)
        records = json.loads(self.path.read_text())
        self.assertEqual(records[0], dict(id='P', name='Box', price=3, stock=4, type='physical', weight=2))
        self.assertEqual(records[1], dict(id='D', name='File', price=5, stock=6, type='digital', download_size=100))
        loaded = load_inventory(self.path)
        self.assertIsInstance(loaded.search_product('P'), PhysicalProduct)
        self.assertEqual(loaded.search_product('P').get_weight(), 2)
        self.assertIsInstance(loaded.search_product('D'), DigitalProduct)
        self.assertEqual(loaded.search_product('D').get_download_size(), 100)

    def test_migration_preserves_records_and_backup(self):
        records = [dict(id='P', name='Original', price=2.5, stock=7), dict(id='D', name='Second', price=1, stock=0)]
        original = json.dumps(records).encode()
        self.path.write_bytes(original)
        with patch('builtins.input', side_effect=['invalid', '1', '-1', 'nan', '2', '2', '100']):
            loaded = load_inventory(self.path, main.classify_legacy_product)
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(self.path.with_name('inventory.json.bak').read_bytes(), original)
        save_inventory(loaded, self.path)
        for old, new in zip(records, json.loads(self.path.read_text())):
            self.assertEqual(old, {key: new[key] for key in old})
        self.assertIsInstance(load_inventory(self.path).search_product('D'), DigitalProduct)

    def test_cancelled_migration_preserves_original_and_existing_backup(self):
        original = json.dumps([dict(id='P', name='Original', price=2, stock=7)]).encode()
        self.path.write_bytes(original)
        backup = self.path.with_name('inventory.json.bak')
        backup.write_bytes(b'previous backup')
        with patch('builtins.input', side_effect=EOFError):
            with self.assertRaises(EOFError):
                load_inventory(self.path, main.classify_legacy_product)
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(backup.read_bytes(), b'previous backup')
        self.assertEqual(self.path.with_name('inventory.json.bak.1').read_bytes(), original)

    def test_invalid_files_are_not_changed(self):
        record = dict(id='P', name='Box', price=3, stock=4, type='physical', weight=2)
        invalid = ['{', '{}', '[null]', json.dumps([record, record]), json.dumps([dict(record, type='unknown')]),
                   json.dumps([dict(record, stock=2.5)]), '[{"id":"P"}]']
        for content in invalid:
            with self.subTest(content=content):
                self.path.write_text(content)
                with self.assertRaises(ValueError):
                    load_inventory(self.path)
                self.assertEqual(self.path.read_text(), content)

    def test_failed_save_preserves_original(self):
        self.path.write_text('original')
        with patch('inventory_manager.os.replace', side_effect=OSError('write failed')):
            with self.assertRaises(OSError):
                save_inventory(self.inventory, self.path)
        self.assertEqual(self.path.read_text(), 'original')
        self.assertEqual(list(self.path.parent.glob('*.tmp')), [])

    def test_missing_file(self):
        self.assertEqual(load_inventory(self.path).get_products(), [])

    def test_all_menu_options(self):
        responses = ['invalid', '1', '2', '2', '25', 'N', 'New', '2.5', '4', '3', 'N', '9', '4', 'N', '5', '6']
        with patch('builtins.input', side_effect=responses), patch('main.save_inventory') as save:
            main.display_menu(self.inventory)
        save.assert_called_once_with(self.inventory)
        self.assertEqual(self.inventory.search_product('N').get_stock(), 9)
        self.assertIn('Download size: 25.0 MB', self.output.getvalue())
        self.assertIn('Program terminated.', self.output.getvalue())

    def test_exit_does_not_save(self):
        save_inventory(self.inventory, self.path)
        original = self.path.read_bytes()
        with patch('main.load_inventory', return_value=load_inventory(self.path)), patch('main.save_inventory') as save:
            with patch('builtins.input', side_effect=['3', 'P', '100', '6']):
                main.main()
        save.assert_not_called()
        self.assertEqual(self.path.read_bytes(), original)

    def test_add_physical_and_invalid_common_input(self):
        for responses in [['1', '2', 'N', 'New', '3', '4'], ['1', '2', 'N', 'Duplicate', '3', '4'],
                          ['2', '3', 'X', 'Bad', 'nan', '2'], ['2', '3', 'X', 'Bad', '2', '1.5']]:
            with patch('builtins.input', side_effect=responses):
                main.add_product(self.inventory)
        self.assertIsInstance(self.inventory.search_product('N'), PhysicalProduct)
        self.assertEqual(len(self.inventory.get_products()), 3)
        self.assertIn('already exists', self.output.getvalue())

    def test_invalid_stock_and_missing_search(self):
        for responses in [['P', '-1'], ['P', 'abc'], ['missing']]:
            with patch('builtins.input', side_effect=responses):
                main.update_stock(self.inventory)
        with patch('builtins.input', return_value='missing'):
            main.search_product(self.inventory)
        self.assertEqual(self.inventory.search_product('P').get_stock(), 4)
        self.assertIn('Product not found.', self.output.getvalue())

    def test_save_failure_keeps_menu_available(self):
        with patch('main.save_inventory', side_effect=OSError('disk full')):
            with patch('builtins.input', side_effect=['5', '1', '6']):
                main.display_menu(self.inventory)
        self.assertIn('Unable to save inventory: disk full', self.output.getvalue())
        self.assertIn('Current Inventory', self.output.getvalue())
        self.assertIn('Program terminated.', self.output.getvalue())
        self.assertEqual(len(self.inventory.get_products()), 2)

    def test_startup_failure_does_not_open_menu(self):
        with patch('main.load_inventory', side_effect=ValueError('bad file')), patch('main.display_menu') as menu:
            main.main()
        menu.assert_not_called()


class CommandLineTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.inventory_path = Path(self.temporary_directory.name) / 'inventory.json'
        self.main_path = Path(__file__).resolve().with_name('main.py')

    def run_application(self, responses):
        result = subprocess.run(
            [sys.executable, str(self.main_path)],
            cwd=self.temporary_directory.name,
            input='\n'.join(responses) + '\n',
            capture_output=True,
            text=True,
            timeout=15,
            check=True
        )
        self.assertEqual(result.stderr, '')
        self.assertIn('Program terminated.', result.stdout)
        return result.stdout

    def test_menu_save_reload_and_exit_without_saving(self):
        self.inventory_path.write_text('[]')
        output = self.run_application([
            'invalid', '1',
            '2', 'invalid', '1', '-1', 'nan', '2', 'P', 'Box', '10', '3',
            '2', '2', '100', 'D', 'Download', '5', '8',
            '2', '1', '1', 'P', 'Duplicate', '1', '1',
            '3', 'P', 'bad', '3', 'P', '-1', '3', 'P', '7',
            '4', 'D', '4', 'missing', '1', '5', '6'
        ])
        for expected in [
            'Invalid option.', 'Choose physical or digital.', 'Invalid input:',
            'A product with that ID already exists.', 'Product not found.',
            'Weight: 2.0 kg', 'Shipping cost: $10.00',
            'Download size: 100.0 MB', 'Delivered digitally',
            'Stock must be a whole number.',
            'Stock quantity cannot be negative.', 'Inventory saved successfully!'
        ]:
            self.assertIn(expected, output)
        records = json.loads(self.inventory_path.read_text())
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]['type'], 'physical')
        self.assertEqual(records[0]['weight'], 2)
        self.assertEqual(records[0]['stock'], 7)
        self.assertEqual(records[1]['type'], 'digital')
        self.assertEqual(records[1]['download_size'], 100)
        self.assertNotIn('weight', records[1])
        saved_bytes = self.inventory_path.read_bytes()
        output = self.run_application(['1', '3', 'P', '99', '6'])
        self.assertIn('Weight: 2.0 kg', output)
        self.assertIn('Download size: 100.0 MB', output)
        self.assertNotIn('Inventory saved successfully!', output)
        self.assertEqual(self.inventory_path.read_bytes(), saved_bytes)
        output = self.run_application(['4', 'P', '6'])
        self.assertIn('Stock: 7', output)

    def test_oversized_json_number_does_not_crash_or_overwrite(self):
        record = dict(id='P', name='Too large', price=10 ** 400,
                      stock=1, type='physical', weight=1)
        original = json.dumps([record]).encode()
        self.inventory_path.write_bytes(original)
        result = subprocess.run(
            [sys.executable, str(self.main_path)],
            cwd=self.temporary_directory.name,
            input='', capture_output=True, text=True, timeout=15, check=True
        )
        self.assertEqual(result.stderr, '')
        self.assertIn('Unable to continue:', result.stdout)
        self.assertEqual(self.inventory_path.read_bytes(), original)

    def test_legacy_migration_save_and_reload(self):
        records = [
            dict(id='P', name='Original box', price=2.5, stock=4),
            dict(id='D', name='Original file', price=3, stock=8)
        ]
        original_bytes = json.dumps(records).encode()
        self.inventory_path.write_bytes(original_bytes)
        output = self.run_application(['1', '2', '2', '50', '5', '6'])
        self.assertIn('Migration validated.', output)
        backup_path = self.inventory_path.with_name('inventory.json.bak')
        self.assertEqual(backup_path.read_bytes(), original_bytes)
        saved_records = json.loads(self.inventory_path.read_text())
        self.assertEqual(len(saved_records), len(records))
        for original, saved in zip(records, saved_records):
            self.assertEqual(original, {key: saved[key] for key in original})
        output = self.run_application(['1', '6'])
        self.assertNotIn('Classify existing product:', output)
        self.assertIn('Weight: 2.0 kg', output)
        self.assertIn('Download size: 50.0 MB', output)


if __name__ == '__main__':
    unittest.main()
