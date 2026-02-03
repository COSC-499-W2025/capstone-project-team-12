from typing import Any, Dict, List
import pytest
from datetime import datetime
from imports_extractor import ImportsExtractor


def create_mock_project_with_imports(
    repo_name: str = "TestRepo",
    commits: List[Dict[str, Any]] = None,
    status: str = "success"
) -> Dict[str, Any]:
    """helper to create mock project data with import information"""
    if commits is None:
        commits = []
    
    return {
        'status': status,
        'repository_name': repo_name,
        'user_commits': commits,
        'error_message': 'Test error' if status != 'success' else None
    }


class TestImportsExtractor:
    
    def test_initialization(self):
        """Test that ImportsExtractor initializes with noise filter"""
        extractor = ImportsExtractor()
        assert 'utils' in extractor.likely_noise
        assert 'components' in extractor.likely_noise
        assert len(extractor.likely_noise) > 0
    
    # Python Import Tests
    
    def test_extract_python_imports_basic(self):
        """Test basic Python import extraction"""
        extractor = ImportsExtractor()
        code = "import os\nimport sys\nfrom datetime import datetime"
        imports = extractor.extract_python_imports(code)
        assert 'os' in imports
        assert 'sys' in imports
        assert 'datetime' in imports
    
    def test_extract_python_imports_nested_packages(self):
        """Test Python imports with nested packages"""
        extractor = ImportsExtractor()
        code = "from os.path import join\nimport numpy.random"
        imports = extractor.extract_python_imports(code)
        assert 'os' in imports
        assert 'numpy' in imports
    
    def test_extract_python_imports_with_aliases(self):
        """Test Python imports with aliases"""
        extractor = ImportsExtractor()
        code = "import numpy as np\nfrom pandas import DataFrame as df"
        imports = extractor.extract_python_imports(code)
        assert 'numpy' in imports
        assert 'pandas' in imports
    
    def test_extract_python_imports_syntax_error_fallback(self):
        """Test Python import extraction falls back to regex on syntax error"""
        extractor = ImportsExtractor()
        code = "import os\nthis is invalid python syntax\nimport sys"
        imports = extractor.extract_python_imports(code)
        # Should still extract what it can via regex fallback
        assert 'os' in imports
        assert 'sys' in imports
    
    def test_extract_python_imports_empty_code(self):
        """Test Python import extraction with empty code"""
        extractor = ImportsExtractor()
        imports = extractor.extract_python_imports("")
        assert len(imports) == 0
    
    # JavaScript/TypeScript Import Tests
    
    def test_extract_js_imports_es6(self):
        """Test ES6 import extraction"""
        extractor = ImportsExtractor()
        code = "import React from 'react';\nimport { useState } from 'react';"
        imports = extractor.extract_js_imports(code)
        assert 'react' in imports
    
    def test_extract_js_imports_require(self):
        """Test CommonJS require extraction"""
        extractor = ImportsExtractor()
        code = "const express = require('express');\nconst fs = require('fs');"
        imports = extractor.extract_js_imports(code)
        assert 'express' in imports
        assert 'fs' in imports
    
    def test_extract_js_imports_scoped_packages(self):
        """Test scoped package import extraction"""
        extractor = ImportsExtractor()
        code = "import { Component } from '@angular/core';"
        imports = extractor.extract_js_imports(code)
        assert 'angular' in imports
    
    def test_extract_js_imports_ignores_relative(self):
        """Test that relative imports are ignored"""
        extractor = ImportsExtractor()
        code = "import MyComponent from './components/MyComponent';\nimport utils from '../utils';"
        imports = extractor.extract_js_imports(code)
        assert len(imports) == 0
    
    def test_extract_js_imports_nested_paths(self):
        """Test nested package paths"""
        extractor = ImportsExtractor()
        code = "import lodash from 'lodash/fp';"
        imports = extractor.extract_js_imports(code)
        assert 'lodash' in imports
    
    # Java Import Tests
    
    def test_extract_java_imports_basic(self):
        """Test basic Java import extraction"""
        extractor = ImportsExtractor()
        code = "import java.util.List;\nimport java.io.File;"
        imports = extractor.extract_java_imports(code)
        assert 'java.util' in imports
        assert 'java.io' in imports
    
    def test_extract_java_imports_firebase(self):
        """Test Firebase import extraction (com.google.firebase)"""
        extractor = ImportsExtractor()
        code = "import com.google.firebase.auth.FirebaseAuth;\nimport com.google.firebase.database.DatabaseReference;"
        imports = extractor.extract_java_imports(code)
        assert 'firebase' in imports
    
    def test_extract_java_imports_androidx(self):
        """Test androidx import extraction"""
        extractor = ImportsExtractor()
        code = "import androidx.appcompat.app.AppCompatActivity;\nimport androidx.recyclerview.widget.RecyclerView;"
        imports = extractor.extract_java_imports(code)
        assert 'androidx.appcompat' in imports
        assert 'androidx.recyclerview' in imports
    
    def test_extract_java_imports_static(self):
        """Test static imports"""
        extractor = ImportsExtractor()
        code = "import static org.junit.Assert.assertEquals;"
        imports = extractor.extract_java_imports(code)
        assert 'junit.Assert' in imports
    
    def test_extract_java_imports_wildcard(self):
        """Test wildcard imports"""
        extractor = ImportsExtractor()
        code = "import java.util.*;"
        imports = extractor.extract_java_imports(code)
        assert 'java.util' in imports
    
    # C# Import Tests
    
    def test_extract_csharp_imports_system(self):
        """Test C# System namespace imports"""
        extractor = ImportsExtractor()
        code = "using System.Collections.Generic;\nusing System.Linq;"
        imports = extractor.extract_csharp_imports(code)
        assert 'System.Collections' in imports
        assert 'System.Linq' in imports
    
    def test_extract_csharp_imports_microsoft(self):
        """Test Microsoft namespace imports"""
        extractor = ImportsExtractor()
        code = "using Microsoft.EntityFrameworkCore;\nusing Microsoft.AspNetCore.Mvc;"
        imports = extractor.extract_csharp_imports(code)
        assert 'EntityFrameworkCore' in imports
        assert 'AspNetCore' in imports
    
    def test_extract_csharp_imports_third_party(self):
        """Test third-party C# imports"""
        extractor = ImportsExtractor()
        code = "using Newtonsoft.Json;\nusing AutoMapper;"
        imports = extractor.extract_csharp_imports(code)
        assert 'Newtonsoft' in imports
        assert 'AutoMapper' in imports
    
    def test_extract_csharp_imports_static(self):
        """Test static using statements"""
        extractor = ImportsExtractor()
        code = "using static System.Math;"
        imports = extractor.extract_csharp_imports(code)
        assert 'System.Math' in imports
    
    # Other Languages Tests
    
    def test_extract_go_imports(self):
        """Test Go import extraction"""
        extractor = ImportsExtractor()
        code = 'import "fmt"\nimport "github.com/gorilla/mux"'
        imports = extractor.extract_go_imports(code)
        assert 'fmt' in imports
        assert 'gorilla/mux' in imports
    
    def test_extract_go_imports_block(self):
        """Test Go import block"""
        extractor = ImportsExtractor()
        code = '''import (
            "fmt"
            "net/http"
            "github.com/gin-gonic/gin"
        )'''
        imports = extractor.extract_go_imports(code)
        assert 'fmt' in imports
        assert 'http' in imports
        assert 'gin-gonic/gin' in imports
    
    def test_extract_rust_imports(self):
        """Test Rust use statements"""
        extractor = ImportsExtractor()
        code = "use std::collections::HashMap;\nuse serde::Serialize;"
        imports = extractor.extract_rust_imports(code)
        assert 'std::collections' in imports
        assert 'serde' in imports
    
    def test_extract_ruby_imports(self):
        """Test Ruby require statements"""
        extractor = ImportsExtractor()
        code = "require 'rails'\nrequire 'active_record'"
        imports = extractor.extract_ruby_imports(code)
        assert 'rails' in imports
        assert 'active_record' in imports
    
    def test_extract_ruby_imports_ignores_relative(self):
        """Test Ruby ignores relative requires"""
        extractor = ImportsExtractor()
        code = "require './lib/helper'\nrequire 'rails'"
        imports = extractor.extract_ruby_imports(code)
        assert 'rails' in imports
        assert len(imports) == 1
    
    def test_extract_php_imports(self):
        """Test PHP use statements"""
        extractor = ImportsExtractor()
        code = "use Illuminate\\Support\\Facades\\DB;\nuse App\\Models\\User;"
        imports = extractor.extract_php_imports(code)
        assert 'Illuminate' in imports
        assert 'App' in imports
    
    def test_extract_swift_imports(self):
        """Test Swift imports"""
        extractor = ImportsExtractor()
        code = "import UIKit\nimport Foundation"
        imports = extractor.extract_swift_imports(code)
        assert 'UIKit' in imports
        assert 'Foundation' in imports
    
    def test_extract_kotlin_imports(self):
        """Test Kotlin imports"""
        extractor = ImportsExtractor()
        code = "import com.google.firebase.auth.FirebaseAuth\nimport androidx.appcompat.app.AppCompatActivity"
        imports = extractor.extract_kotlin_imports(code)
        assert 'firebase' in imports
        assert 'androidx.appcompat' in imports
    
    def test_extract_c_imports(self):
        """Test C/C++ include statements"""
        extractor = ImportsExtractor()
        code = '#include <iostream>\n#include "myheader.h"'
        imports = extractor.extract_c_imports(code)
        assert 'iostream' in imports
        assert 'myheader' in imports
    
    def test_extract_c_imports_nested_paths(self):
        """Test C++ includes with paths"""
        extractor = ImportsExtractor()
        code = '#include <boost/algorithm/string.hpp>'
        imports = extractor.extract_c_imports(code)
        assert 'string' in imports
    
    # General extract_imports Tests
    
    def test_extract_imports_by_extension(self):
        """Test that correct extractor is called based on file extension"""
        extractor = ImportsExtractor()
        
        # Python
        py_imports = extractor.extract_imports("import os", "py")
        assert 'os' in py_imports
        
        # JavaScript
        js_imports = extractor.extract_imports("import React from 'react'", "js")
        assert 'react' in js_imports
        
        # Java
        java_imports = extractor.extract_imports("import java.util.List;", "java")
        assert 'java.util' in java_imports
    
    def test_extract_imports_filters_noise(self):
        """Test that noise imports are filtered out"""
        extractor = ImportsExtractor()
        code = "import utils\nimport components\nimport os"
        imports = extractor.extract_imports(code, "py")
        assert 'os' in imports
        assert 'utils' not in imports
        assert 'components' not in imports
    
    def test_extract_imports_empty_code(self):
        """Test extraction with empty source code"""
        extractor = ImportsExtractor()
        imports = extractor.extract_imports("", "py")
        assert len(imports) == 0
        
        imports = extractor.extract_imports(None, "py")
        assert len(imports) == 0
    
    def test_extract_imports_unknown_extension(self):
        """Test extraction with unknown file extension"""
        extractor = ImportsExtractor()
        imports = extractor.extract_imports("import something", "unknown")
        assert len(imports) == 0
    
    # extract_repo_import_stats Tests
    
    def test_extract_repo_import_stats_basic(self):
        """Test basic import stats extraction from a repo"""
        extractor = ImportsExtractor()
        commits = [
            {
                'date': '2024-01-01T00:00:00',
                'modified_files': [
                    {'filename': 'main.py', 'source_code': 'import os\nimport sys'}
                ]
            }
        ]
        project = create_mock_project_with_imports(commits=commits)
        
        stats = extractor.extract_repo_import_stats(project)
        assert 'os' in stats
        assert 'sys' in stats
        assert stats['os']['frequency'] == 1
        assert stats['os']['start_date'] == '2024-01-01T00:00:00'
    
    def test_extract_repo_import_stats_frequency_tracking(self):
        """Test that frequency is tracked across multiple commits"""
        extractor = ImportsExtractor()
        commits = [
            {
                'date': '2024-01-01T00:00:00',
                'modified_files': [
                    {'filename': 'a.py', 'source_code': 'import os'}
                ]
            },
            {
                'date': '2024-01-05T00:00:00',
                'modified_files': [
                    {'filename': 'b.py', 'source_code': 'import os\nimport sys'}
                ]
            }
        ]
        project = create_mock_project_with_imports(commits=commits)
        
        stats = extractor.extract_repo_import_stats(project)
        assert stats['os']['frequency'] == 2
        assert stats['sys']['frequency'] == 1
    
    def test_extract_repo_import_stats_date_range(self):
        """Test that start and end dates are tracked correctly"""
        extractor = ImportsExtractor()
        commits = [
            {
                'date': '2024-01-01T00:00:00',
                'modified_files': [
                    {'filename': 'a.py', 'source_code': 'import os'}
                ]
            },
            {
                'date': '2024-01-15T00:00:00',
                'modified_files': [
                    {'filename': 'b.py', 'source_code': 'import os'}
                ]
            },
            {
                'date': '2024-01-10T00:00:00',
                'modified_files': [
                    {'filename': 'c.py', 'source_code': 'import os'}
                ]
            }
        ]
        project = create_mock_project_with_imports(commits=commits)
        
        stats = extractor.extract_repo_import_stats(project)
        assert stats['os']['start_date'] == '2024-01-01T00:00:00'
        assert stats['os']['end_date'] == '2024-01-15T00:00:00'
        assert stats['os']['duration_days'] == 14
    
    def test_extract_repo_import_stats_duration_calculation(self):
        """Test duration_days calculation"""
        extractor = ImportsExtractor()
        commits = [
            {
                'date': '2024-01-01T00:00:00',
                'modified_files': [
                    {'filename': 'a.py', 'source_code': 'import numpy'}
                ]
            },
            {
                'date': '2024-01-31T00:00:00',
                'modified_files': [
                    {'filename': 'b.py', 'source_code': 'import numpy'}
                ]
            }
        ]
        project = create_mock_project_with_imports(commits=commits)
        
        stats = extractor.extract_repo_import_stats(project)
        assert stats['numpy']['duration_days'] == 30
    
    def test_extract_repo_import_stats_same_day_usage(self):
        """Test that same-day usage results in 0 duration"""
        extractor = ImportsExtractor()
        commits = [
            {
                'date': '2024-01-01T00:00:00',
                'modified_files': [
                    {'filename': 'a.py', 'source_code': 'import os'}
                ]
            },
            {
                'date': '2024-01-01T12:00:00',
                'modified_files': [
                    {'filename': 'b.py', 'source_code': 'import os'}
                ]
            }
        ]
        project = create_mock_project_with_imports(commits=commits)
        
        stats = extractor.extract_repo_import_stats(project)
        assert stats['os']['duration_days'] == 0
    
    def test_extract_repo_import_stats_skips_invalid_dates(self):
        """Test that commits with invalid dates are skipped"""
        extractor = ImportsExtractor()
        commits = [
            {
                'date': '2024-01-01T00:00:00',
                'modified_files': [
                    {'filename': 'a.py', 'source_code': 'import os'}
                ]
            },
            {
                'date': None,
                'modified_files': [
                    {'filename': 'b.py', 'source_code': 'import sys'}
                ]
            },
            {
                'date': 'invalid-date',
                'modified_files': [
                    {'filename': 'c.py', 'source_code': 'import json'}
                ]
            }
        ]
        project = create_mock_project_with_imports(commits=commits)
        
        stats = extractor.extract_repo_import_stats(project)
        assert 'os' in stats
        assert 'sys' not in stats
        assert 'json' not in stats
    
    def test_extract_repo_import_stats_skips_empty_source(self):
        """Test that files with empty source code are skipped"""
        extractor = ImportsExtractor()
        commits = [
            {
                'date': '2024-01-01T00:00:00',
                'modified_files': [
                    {'filename': 'a.py', 'source_code': ''},
                    {'filename': 'b.py', 'source_code': '   '},
                    {'filename': 'c.py', 'source_code': 'import os'}
                ]
            }
        ]
        project = create_mock_project_with_imports(commits=commits)
        
        stats = extractor.extract_repo_import_stats(project)
        assert len(stats) == 1
        assert 'os' in stats
    
    def test_extract_repo_import_stats_multiple_languages(self):
        """Test extraction across multiple programming languages"""
        extractor = ImportsExtractor()
        commits = [
            {
                'date': '2024-01-01T00:00:00',
                'modified_files': [
                    {'filename': 'main.py', 'source_code': 'import os'},
                    {'filename': 'app.js', 'source_code': "import React from 'react'"},
                    {'filename': 'Main.java', 'source_code': 'import java.util.List;'}
                ]
            }
        ]
        project = create_mock_project_with_imports(commits=commits)
        
        stats = extractor.extract_repo_import_stats(project)
        assert 'os' in stats
        assert 'react' in stats
        assert 'java.util' in stats
    
    def test_extract_repo_import_stats_empty_commits(self):
        """Test with no commits"""
        extractor = ImportsExtractor()
        project = create_mock_project_with_imports(commits=[])
        
        stats = extractor.extract_repo_import_stats(project)
        assert len(stats) == 0
    

    # get_all_repo_import_stats Tests
    
    def test_get_all_repo_import_stats_success(self):
        """Test getting stats for multiple successful repos"""
        extractor = ImportsExtractor()
        commits = [
            {
                'date': '2024-01-01T00:00:00',
                'modified_files': [
                    {'filename': 'main.py', 'source_code': 'import os'}
                ]
            }
        ]
        
        projects = [
            create_mock_project_with_imports("Repo1", commits),
            create_mock_project_with_imports("Repo2", commits)
        ]
        
        results = extractor.get_all_repo_import_stats(projects)
        assert len(results) == 2
        assert results[0]['repository_name'] == 'Repo1'
        assert 'os' in results[0]['imports_summary']
        assert results[1]['repository_name'] == 'Repo2'
    
    def test_get_all_repo_import_stats_with_errors(self):
        """Test handling repos with error status"""
        extractor = ImportsExtractor()
        projects = [
            create_mock_project_with_imports("GoodRepo", [
                {
                    'date': '2024-01-01T00:00:00',
                    'modified_files': [
                        {'filename': 'main.py', 'source_code': 'import os'}
                    ]
                }
            ]),
            create_mock_project_with_imports("BadRepo", [], status='error')
        ]
        
        results = extractor.get_all_repo_import_stats(projects)
        assert len(results) == 2
        assert 'os' in results[0]['imports_summary']
        assert 'error' in results[1]
        assert results[1]['imports_summary'] == {}
    
    def test_get_all_repo_import_stats_exception_handling(self):
        """Test that exceptions during extraction are caught"""
        extractor = ImportsExtractor()
        
        bad_project = {
            'status': 'success',
            'repository_name': 'BadRepo',
            'user_commits': [
                {
                    'date': '2024-01-01T00:00:00',
                    'modified_files': None  # will cause an error
                }
            ]
        }
        
        results = extractor.get_all_repo_import_stats([bad_project])
        assert len(results) == 1
        assert 'error' in results[0]
        assert results[0]['imports_summary'] == {}
    
    def test_get_all_repo_import_stats_empty_list(self):
        """Test with empty project list"""
        extractor = ImportsExtractor()
        results = extractor.get_all_repo_import_stats([])
        assert len(results) == 0
    
    # Sorting Tests
    
    def test_sort_repo_imports_in_chronological_order(self):
        """Test sorting imports within a single repo chronologically"""
        extractor = ImportsExtractor()
        repo_summary = {
            "repository_name": "TestRepo",
            "imports_summary": {
                "os": {"start_date": "2024-01-05T00:00:00", "frequency": 1},
                "sys": {"start_date": "2024-01-10T00:00:00", "frequency": 2},
                "json": {"start_date": "2024-01-01T00:00:00", "frequency": 3}
            }
        }
        
        sorted_repo = extractor.sort_repo_imports_in_chronological_order(repo_summary)
        import_keys = list(sorted_repo["imports_summary"].keys())
        
        assert import_keys == ["sys", "os", "json"]  
    
    def test_sort_repo_imports_handles_missing_dates(self):
        """Test sorting handles imports with missing start dates"""
        extractor = ImportsExtractor()
        repo_summary = {
            "repository_name": "TestRepo",
            "imports_summary": {
                "os": {"start_date": "2024-01-05T00:00:00"},
                "sys": {"start_date": None},
                "json": {"start_date": "2024-01-10T00:00:00"}
            }
        }
        
        sorted_repo = extractor.sort_repo_imports_in_chronological_order(repo_summary)
        import_keys = list(sorted_repo["imports_summary"].keys())
        
        assert import_keys[0] == "json"
        assert import_keys[-1] == "sys"
    
    def test_sort_all_repo_imports_chronologically(self):
        """Test sorting all imports across multiple repos"""
        extractor = ImportsExtractor()
        summaries = [
            {
                "repository_name": "Repo1",
                "imports_summary": {
                    "os": {
                        "start_date": "2024-01-05T00:00:00",
                        "end_date": "2024-01-05T00:00:00",
                        "frequency": 1,
                        "duration_days": 0
                    },
                    "sys": {
                        "start_date": "2024-01-15T00:00:00",
                        "end_date": "2024-01-15T00:00:00",
                        "frequency": 2,
                        "duration_days": 0
                    }
                }
            },
            {
                "repository_name": "Repo2",
                "imports_summary": {
                    "numpy": {
                        "start_date": "2024-01-10T00:00:00",
                        "end_date": "2024-01-10T00:00:00",
                        "frequency": 3,
                        "duration_days": 0
                    }
                }
            }
        ]
        
        sorted_imports = extractor.sort_all_repo_imports_chronologically(summaries)
        
        assert len(sorted_imports) == 3
        assert sorted_imports[0]["import"] == "sys"  
        assert sorted_imports[1]["import"] == "numpy"
        assert sorted_imports[2]["import"] == "os" 
        
        assert "start_dt" not in sorted_imports[0]
    
    def test_sort_all_repo_imports_handles_missing_dates(self):
        """Test sorting across repos handles missing dates"""
        extractor = ImportsExtractor()
        summaries = [
            {
                "repository_name": "Repo1",
                "imports_summary": {
                    "os": {
                        "start_date": "2024-01-05T00:00:00",
                        "frequency": 1
                    },
                    "sys": {
                        "start_date": None,
                        "frequency": 2
                    }
                }
            }
        ]
        
        sorted_imports = extractor.sort_all_repo_imports_chronologically(summaries)
        
        assert len(sorted_imports) == 2
        # Import with valid date should come before none date
        assert sorted_imports[0]["import"] == "os"
        assert sorted_imports[1]["import"] == "sys"
    
    def test_sort_all_repo_imports_preserves_metadata(self):
        """Test that all metadata is preserved during sorting"""
        extractor = ImportsExtractor()
        summaries = [
            {
                "repository_name": "TestRepo",
                "imports_summary": {
                    "os": {
                        "start_date": "2024-01-01T00:00:00",
                        "end_date": "2024-01-10T00:00:00",
                        "frequency": 5,
                        "duration_days": 9
                    }
                }
            }
        ]
        
        sorted_imports = extractor.sort_all_repo_imports_chronologically(summaries)
        
        assert sorted_imports[0]["repository_name"] == "TestRepo"
        assert sorted_imports[0]["frequency"] == 5
        assert sorted_imports[0]["duration_days"] == 9
        assert sorted_imports[0]["start_date"] == "2024-01-01T00:00:00"
        assert sorted_imports[0]["end_date"] == "2024-01-10T00:00:00"
    
    def test_sort_all_repo_imports_empty_summaries(self):
        """Test sorting with empty summaries"""
        extractor = ImportsExtractor()
        sorted_imports = extractor.sort_all_repo_imports_chronologically([])
        assert len(sorted_imports) == 0