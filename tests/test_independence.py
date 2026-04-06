"""
Tests for Framework Independence

These tests verify that claw-rl maintains framework independence
as per ADR-008. They check that:

1. Core modules have no external framework dependencies
2. Protocols are pure abstractions
3. Adapters are in separate, optional directories
4. No neoclaw-specific imports in core code

This file is critical for maintaining the architectural integrity
of claw-rl as a framework-agnostic learning module.
"""

import pytest
import ast
import subprocess
from pathlib import Path


class TestFrameworkIndependence:
    """Tests for framework independence."""
    
    @pytest.fixture
    def src_path(self):
        """Get the source path."""
        return Path(__file__).parent.parent / "src" / "claw_rl"
    
    def test_no_neoclaw_imports_in_core(self, src_path):
        """Verify no neoclaw imports in core modules."""
        core_path = src_path / "core"
        
        if not core_path.exists():
            pytest.skip("core directory not found")
        
        for py_file in core_path.glob("*.py"):
            content = py_file.read_text()
            
            # Check for neoclaw imports
            assert "from neoclaw" not in content, f"Found 'from neoclaw' in {py_file}"
            assert "import neoclaw" not in content, f"Found 'import neoclaw' in {py_file}"
    
    def test_no_neoclaw_imports_in_protocols(self, src_path):
        """Verify no neoclaw imports in protocol modules."""
        protocols_path = src_path / "protocols"
        
        if not protocols_path.exists():
            pytest.skip("protocols directory not found")
        
        for py_file in protocols_path.glob("*.py"):
            content = py_file.read_text()
            
            assert "from neoclaw" not in content, f"Found 'from neoclaw' in {py_file}"
            assert "import neoclaw" not in content, f"Found 'import neoclaw' in {py_file}"
    
    def test_no_neoclaw_imports_in_learning(self, src_path):
        """Verify no neoclaw imports in learning modules."""
        learning_path = src_path / "learning"
        
        if not learning_path.exists():
            pytest.skip("learning directory not found")
        
        for py_file in learning_path.glob("*.py"):
            content = py_file.read_text()
            
            assert "from neoclaw" not in content, f"Found 'from neoclaw' in {py_file}"
            assert "import neoclaw" not in content, f"Found 'import neoclaw' in {py_file}"
    
    def test_no_neoclaw_imports_in_feedback(self, src_path):
        """Verify no neoclaw imports in feedback modules."""
        feedback_path = src_path / "feedback"
        
        if not feedback_path.exists():
            pytest.skip("feedback directory not found")
        
        for py_file in feedback_path.glob("*.py"):
            content = py_file.read_text()
            
            assert "from neoclaw" not in content, f"Found 'from neoclaw' in {py_file}"
            assert "import neoclaw" not in content, f"Found 'import neoclaw' in {py_file}"
    
    def test_no_neoclaw_imports_in_pattern(self, src_path):
        """Verify no neoclaw imports in pattern modules."""
        pattern_path = src_path / "pattern"
        
        if not pattern_path.exists():
            pytest.skip("pattern directory not found")
        
        for py_file in pattern_path.glob("*.py"):
            content = py_file.read_text()
            
            assert "from neoclaw" not in content, f"Found 'from neoclaw' in {py_file}"
            assert "import neoclaw" not in content, f"Found 'import neoclaw' in {py_file}"
    
    def test_no_neoclaw_imports_in_context(self, src_path):
        """Verify no neoclaw imports in context modules."""
        context_path = src_path / "context"
        
        if not context_path.exists():
            pytest.skip("context directory not found")
        
        for py_file in context_path.glob("*.py"):
            content = py_file.read_text()
            
            assert "from neoclaw" not in content, f"Found 'from neoclaw' in {py_file}"
            assert "import neoclaw" not in content, f"Found 'import neoclaw' in {py_file}"
    
    def test_protocols_are_pure_abstractions(self, src_path):
        """Verify protocols are pure abstractions (no implementations)."""
        protocols_path = src_path / "protocols"
        
        if not protocols_path.exists():
            pytest.skip("protocols directory not found")
        
        for py_file in protocols_path.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            
            content = py_file.read_text()
            
            # Parse the AST
            tree = ast.parse(content)
            
            # Check for Protocol classes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if it inherits from Protocol
                    is_protocol = any(
                        (isinstance(base, ast.Name) and base.id == "Protocol")
                        or (isinstance(base, ast.Attribute) and base.attr == "Protocol")
                        for base in node.bases
                    )
                    
                    if is_protocol:
                        # Protocol classes should only have method signatures
                        # (ellipsis bodies or pass statements)
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                # Method should have ellipsis body
                                has_ellipsis = any(
                                    isinstance(stmt, ast.Expr) and
                                    isinstance(stmt.value, ast.Constant) and
                                    stmt.value.value is ...
                                    for stmt in item.body
                                )
                                
                                # Or just pass
                                has_pass = any(
                                    isinstance(stmt, ast.Pass)
                                    for stmt in item.body
                                )
                                
                                assert has_ellipsis or has_pass, \
                                    f"Protocol method {node.name}.{item.name} should have ellipsis or pass body"
    
    def test_adapters_in_separate_directory(self, src_path):
        """Verify adapters are in a separate directory."""
        adapters_path = src_path / "adapters"
        
        assert adapters_path.exists(), "adapters directory should exist"
        assert adapters_path.is_dir(), "adapters should be a directory"
    
    def test_protocols_in_separate_directory(self, src_path):
        """Verify protocols are in a separate directory."""
        protocols_path = src_path / "protocols"
        
        assert protocols_path.exists(), "protocols directory should exist"
        assert protocols_path.is_dir(), "protocols should be a directory"
    
    def test_pyproject_no_required_external_deps(self):
        """Verify pyproject.toml has no required external framework dependencies."""
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        
        if not pyproject_path.exists():
            pytest.skip("pyproject.toml not found")
        
        content = pyproject_path.read_text()
        
        # Check that neoclaw is not a required dependency
        assert "neoclaw" not in content.lower() or "optional" in content.lower(), \
            "neoclaw should not be a required dependency"
    
    def test_core_modules_importable_without_adapters(self, src_path):
        """Verify core modules can be imported without adapters."""
        import sys
        
        # Try importing core modules
        try:
            from claw_rl.core import CPALoop, CPALoopConfig
            from claw_rl.learning import KnowledgeBase
            from claw_rl.feedback import BinaryRLJudge
            from claw_rl.pattern import PatternRecognitionEngine
            
            # If we get here, core modules are importable
            assert True
        except ImportError as e:
            pytest.fail(f"Core module import failed: {e}")
    
    def test_protocols_importable_without_adapters(self, src_path):
        """Verify protocols can be imported without adapters."""
        try:
            from claw_rl.protocols import (
                ObserverProtocol,
                DecisionMakerProtocol,
                ExecutorProtocol,
                SignalAdapterProtocol,
            )
            
            assert True
        except ImportError as e:
            pytest.fail(f"Protocol import failed: {e}")
    
    def test_adapters_use_protocols(self, src_path):
        """Verify adapters implement protocols."""
        adapters_path = src_path / "adapters"
        
        if not adapters_path.exists():
            pytest.skip("adapters directory not found")
        
        # Check base_adapter.py
        base_adapter = adapters_path / "base_adapter.py"
        if base_adapter.exists():
            content = base_adapter.read_text()
            
            # Should import from protocols
            assert "from ..protocols" in content or "from claw_rl.protocols" in content, \
                "base_adapter should import from protocols"
    
    def test_no_external_framework_classes_in_core(self, src_path):
        """Verify no external framework class references in core."""
        core_path = src_path / "core"
        
        if not core_path.exists():
            pytest.skip("core directory not found")
        
        # List of known external framework class names to avoid
        forbidden_classes = [
            "NeoClawAgent",
            "NeoClawBridge",
            "NeoClawConfig",
        ]
        
        for py_file in core_path.glob("*.py"):
            content = py_file.read_text()
            
            for forbidden in forbidden_classes:
                assert forbidden not in content, \
                    f"Found forbidden class '{forbidden}' in {py_file}"


class TestDirectoryStructure:
    """Tests for directory structure compliance."""
    
    def test_protocols_directory_exists(self):
        """Verify protocols directory exists."""
        protocols_path = Path(__file__).parent.parent / "src" / "claw_rl" / "protocols"
        assert protocols_path.exists()
        assert protocols_path.is_dir()
    
    def test_adapters_directory_exists(self):
        """Verify adapters directory exists."""
        adapters_path = Path(__file__).parent.parent / "src" / "claw_rl" / "adapters"
        assert adapters_path.exists()
        assert adapters_path.is_dir()
    
    def test_core_directory_exists(self):
        """Verify core directory exists."""
        core_path = Path(__file__).parent.parent / "src" / "claw_rl" / "core"
        assert core_path.exists()
        assert core_path.is_dir()
    
    def test_learning_directory_exists(self):
        """Verify learning directory exists."""
        learning_path = Path(__file__).parent.parent / "src" / "claw_rl" / "learning"
        assert learning_path.exists()
        assert learning_path.is_dir()
    
    def test_feedback_directory_exists(self):
        """Verify feedback directory exists."""
        feedback_path = Path(__file__).parent.parent / "src" / "claw_rl" / "feedback"
        assert feedback_path.exists()
        assert feedback_path.is_dir()
    
    def test_pattern_directory_exists(self):
        """Verify pattern directory exists."""
        pattern_path = Path(__file__).parent.parent / "src" / "claw_rl" / "pattern"
        assert pattern_path.exists()
        assert pattern_path.is_dir()


class TestDependencyIndependence:
    """Tests for dependency independence."""
    
    def test_core_has_minimal_imports(self):
        """Verify core modules have minimal imports."""
        from claw_rl.core import CPALoop
        
        # CPALoop should only import from protocols and stdlib
        # Check that it doesn't have heavy dependencies
        import sys
        initial_modules = set(sys.modules.keys())
        
        # Import CPALoop
        from claw_rl.core.cpa_loop import CPALoop
        
        # Check that no heavy external modules were loaded
        # (This is a heuristic check)
        new_modules = set(sys.modules.keys()) - initial_modules
        
        # Filter out expected modules
        expected_prefixes = ['claw_rl', 'typing', 'dataclasses', 'datetime', 'enum', 'time']
        unexpected = [
            m for m in new_modules
            if not any(m.startswith(p) for p in expected_prefixes)
        ]
        
        # We expect some stdlib modules, but no external frameworks
        external_frameworks = ['neoclaw', 'torch', 'tensorflow', 'numpy', 'pandas']
        for module in unexpected:
            for framework in external_frameworks:
                assert framework not in module.lower(), \
                    f"Unexpected external dependency: {module}"
