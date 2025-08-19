"""Discovery mechanisms for TorahBench evaluations and implementations."""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import importlib.util
from dataclasses import dataclass


@dataclass
class EvaluationInfo:
    """Information about an available evaluation."""
    name: str
    path: Path
    description: str
    version: str


@dataclass
class ImplementationInfo:
    """Information about an available implementation."""
    name: str
    evaluation: str
    path: Path
    description: str
    version: str


class TorahBenchDiscovery:
    """Discovers available evaluations and implementations."""
    
    def __init__(self, base_path: Optional[Path] = None):
        if base_path is None:
            # Default to the packages directory relative to this file
            base_path = Path(__file__).parent.parent.parent / "packages"
        self.base_path = base_path
    
    def discover_evaluations(self) -> List[EvaluationInfo]:
        """Discover all available evaluation packages."""
        evaluations = []
        evals_dir = self.base_path / "evals"
        
        if not evals_dir.exists():
            return evaluations
        
        for eval_dir in evals_dir.iterdir():
            if eval_dir.is_dir() and (eval_dir / "pyproject.toml").exists():
                try:
                    info = self._load_evaluation_info(eval_dir)
                    if info:
                        evaluations.append(info)
                except Exception:
                    # Skip invalid packages
                    continue
        
        return evaluations
    
    def discover_implementations(self, evaluation_name: Optional[str] = None) -> List[ImplementationInfo]:
        """Discover all available implementation packages."""
        implementations = []
        impl_dir = self.base_path / "implementations"
        
        if not impl_dir.exists():
            return implementations
        
        for service_dir in impl_dir.iterdir():
            if not service_dir.is_dir():
                continue
            
            for eval_impl_dir in service_dir.iterdir():
                if not eval_impl_dir.is_dir() or not (eval_impl_dir / "pyproject.toml").exists():
                    continue
                
                # Skip if we're filtering by evaluation name
                if evaluation_name and eval_impl_dir.name != evaluation_name:
                    continue
                
                try:
                    info = self._load_implementation_info(service_dir.name, eval_impl_dir)
                    if info:
                        implementations.append(info)
                except Exception:
                    # Skip invalid packages
                    continue
        
        return implementations
    
    def find_implementation(self, evaluation: str, implementation: str) -> Optional[ImplementationInfo]:
        """Find a specific implementation for an evaluation."""
        impl_path = self.base_path / "implementations" / implementation / evaluation
        
        if not impl_path.exists() or not (impl_path / "pyproject.toml").exists():
            return None
        
        try:
            return self._load_implementation_info(implementation, impl_path)
        except Exception:
            return None
    
    def load_evaluation_module(self, evaluation_name: str):
        """Dynamically load an evaluation module."""
        eval_path = self.base_path / "evals" / evaluation_name
        
        if not eval_path.exists():
            raise ImportError(f"Evaluation '{evaluation_name}' not found")
        
        # Add the evaluation src directory to Python path
        src_path = eval_path / "src"
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        try:
            module = importlib.import_module(evaluation_name)
            return module
        except ImportError as e:
            raise ImportError(f"Failed to import evaluation '{evaluation_name}': {e}")
    
    def load_implementation_module(self, evaluation: str, implementation: str):
        """Dynamically load an implementation module."""
        impl_path = self.base_path / "implementations" / implementation / evaluation
        
        if not impl_path.exists():
            raise ImportError(f"Implementation '{implementation}' for '{evaluation}' not found")
        
        # Add the implementation src directory to Python path
        src_path = impl_path / "src"
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        try:
            module_name = f"{evaluation}_{implementation.replace('-', '_')}"
            module = importlib.import_module(module_name)
            return module
        except ImportError as e:
            raise ImportError(f"Failed to import implementation '{implementation}' for '{evaluation}': {e}")
    
    def _load_evaluation_info(self, eval_dir: Path) -> Optional[EvaluationInfo]:
        """Load information about an evaluation from its pyproject.toml."""
        pyproject_path = eval_dir / "pyproject.toml"
        
        if not pyproject_path.exists():
            return None
        
        # Simple TOML parsing - in a real implementation you'd use tomllib or toml
        content = pyproject_path.read_text()
        
        # Extract basic info (simplified parsing)
        name = eval_dir.name
        description = "Evaluation package"
        version = "0.1.0"
        
        # Look for project section
        if 'description = "' in content:
            desc_start = content.find('description = "') + len('description = "')
            desc_end = content.find('"', desc_start)
            if desc_end > desc_start:
                description = content[desc_start:desc_end]
        
        if 'version = "' in content:
            ver_start = content.find('version = "') + len('version = "')
            ver_end = content.find('"', ver_start)
            if ver_end > ver_start:
                version = content[ver_start:ver_end]
        
        return EvaluationInfo(
            name=name,
            path=eval_dir,
            description=description,
            version=version
        )
    
    def _load_implementation_info(self, service_name: str, impl_dir: Path) -> Optional[ImplementationInfo]:
        """Load information about an implementation from its pyproject.toml."""
        pyproject_path = impl_dir / "pyproject.toml"
        
        if not pyproject_path.exists():
            return None
        
        content = pyproject_path.read_text()
        
        # Extract basic info
        evaluation = impl_dir.name
        description = f"{service_name} implementation for {evaluation}"
        version = "0.1.0"
        
        if 'description = "' in content:
            desc_start = content.find('description = "') + len('description = "')
            desc_end = content.find('"', desc_start)
            if desc_end > desc_start:
                description = content[desc_start:desc_end]
        
        if 'version = "' in content:
            ver_start = content.find('version = "') + len('version = "')
            ver_end = content.find('"', ver_start)
            if ver_end > ver_start:
                version = content[ver_start:ver_end]
        
        return ImplementationInfo(
            name=service_name,
            evaluation=evaluation,
            path=impl_dir,
            description=description,
            version=version
        )
