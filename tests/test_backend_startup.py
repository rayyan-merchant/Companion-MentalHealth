import importlib
import unittest


class BackendStartupTests(unittest.TestCase):
    def test_backend_imports_cleanly(self):
        module = importlib.import_module("backend.main")
        self.assertEqual(module.app.title, "Mental Health KRR System")


if __name__ == "__main__":
    unittest.main()
