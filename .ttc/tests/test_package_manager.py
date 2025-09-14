import sys
import os
import tempfile
import shutil
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
from package_manager import PackageManager

class TestPackageManager(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.pm = PackageManager(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def test_init_project(self):
        """Test project initialization"""
        # Initialize project
        config = self.pm.init_project("test-project", "1.0.0", "A test project", "Test Author")
        
        # Check that config file was created
        config_file = os.path.join(self.test_dir, "tora.json")
        self.assertTrue(os.path.exists(config_file))
        
        # Check config content
        with open(config_file, 'r', encoding='utf-8') as f:
            saved_config = json.load(f)
        
        self.assertEqual(saved_config["name"], "test-project")
        self.assertEqual(saved_config["version"], "1.0.0")
        self.assertEqual(saved_config["description"], "A test project")
        self.assertEqual(saved_config["author"], "Test Author")
        self.assertEqual(saved_config["dependencies"], {})
        self.assertEqual(saved_config["devDependencies"], {})
    
    def test_install_package(self):
        """Test package installation"""
        # First initialize project
        self.pm.init_project("test-project")
        
        # Install a package
        self.pm.install_package("test-package", "1.0.0")
        
        # Check that package directory was created
        package_dir = os.path.join(self.test_dir, "tora_packages", "test-package")
        self.assertTrue(os.path.exists(package_dir))
        
        # Check that package files were created
        main_file = os.path.join(package_dir, "test-package.tora")
        self.assertTrue(os.path.exists(main_file))
        
        package_info_file = os.path.join(package_dir, "package.json")
        self.assertTrue(os.path.exists(package_info_file))
        
        # Check that config was updated
        config_file = os.path.join(self.test_dir, "tora.json")
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        self.assertIn("test-package", config["dependencies"])
        self.assertEqual(config["dependencies"]["test-package"], "1.0.0")
    
    def test_uninstall_package(self):
        """Test package uninstallation"""
        # First initialize project and install a package
        self.pm.init_project("test-project")
        self.pm.install_package("test-package", "1.0.0")
        
        # Uninstall the package
        self.pm.uninstall_package("test-package")
        
        # Check that package directory was removed
        package_dir = os.path.join(self.test_dir, "tora_packages", "test-package")
        self.assertFalse(os.path.exists(package_dir))
        
        # Check that config was updated
        config_file = os.path.join(self.test_dir, "tora.json")
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        self.assertNotIn("test-package", config["dependencies"])
    
    def test_list_packages(self):
        """Test listing packages"""
        # First initialize project and install packages
        self.pm.init_project("test-project")
        self.pm.install_package("package1", "1.0.0")
        self.pm.install_package("package2", "2.0.0", dev=True)
        
        # Check that packages are listed correctly
        config_file = os.path.join(self.test_dir, "tora.json")
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        dependencies = config.get("dependencies", {})
        dev_dependencies = config.get("devDependencies", {})
        
        self.assertIn("package1", dependencies)
        self.assertIn("package2", dev_dependencies)
    
    def test_clean_cache(self):
        """Test cache cleaning"""
        # First initialize project
        self.pm.init_project("test-project")
        
        # Check that cache directory exists
        cache_dir = os.path.join(self.test_dir, "tora_packages", ".cache")
        self.assertTrue(os.path.exists(cache_dir))
        
        # Clean cache
        self.pm.clean_cache()
        
        # Check that cache directory still exists but is empty
        self.assertTrue(os.path.exists(cache_dir))
        self.assertEqual(len(os.listdir(cache_dir)), 0)

if __name__ == '__main__':
    unittest.main()