#!/usr/bin/env python
"""
Automated verification script for Django Todo Project
Run this from your project root directory: python verify_project.py
"""

import os
import re
import sys
import ast
import subprocess

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def check_mark(status):
    return f"{Colors.GREEN}✓{Colors.END}" if status else f"{Colors.RED}✗{Colors.END}"

def print_header(title):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{title:^60}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")

def check_file_exists(filepath):
    """Check if a file exists"""
    return os.path.exists(filepath)

def check_directory_structure():
    """Verify the project directory structure"""
    print_header("Directory Structure Verification")
    
    required_structure = {
        'todo_app': {
            'files': ['__init__.py', 'admin.py', 'apps.py', 'forms.py', 
                     'models.py', 'urls.py', 'views.py'],
            'dirs': ['migrations', 'templates/todo_app']
        },
        'todo_project': {
            'files': ['__init__.py', 'settings.py', 'urls.py', 'wsgi.py'],
            'dirs': []
        },
        'root': {
            'files': ['.gitignore', 'Procfile', 'requirements.txt', 'README.md',
                     'design.md', 'testing.md', 'code_quality.md'],
            'dirs': []
        }
    }
    
    all_good = True
    
    # Check root files
    for file in required_structure['root']['files']:
        exists = check_file_exists(file)
        print(f"{check_mark(exists)} {file}")
        if not exists:
            all_good = False
    
    # Check app directories
    for app, structure in [('todo_app', required_structure['todo_app']), 
                           ('todo_project', required_structure['todo_project'])]:
        print(f"\n{Colors.YELLOW}{app}/{Colors.END}")
        for file in structure['files']:
            filepath = os.path.join(app, file)
            exists = check_file_exists(filepath)
            print(f"  {check_mark(exists)} {file}")
            if not exists:
                all_good = False
                
        for dir_path in structure['dirs']:
            full_path = os.path.join(app, dir_path)
            exists = os.path.isdir(full_path)
            print(f"  {check_mark(exists)} {dir_path}/")
            if not exists:
                all_good = False
    
    # Check templates
    templates_path = 'todo_app/templates/todo_app'
    if os.path.isdir(templates_path):
        print(f"\n{Colors.YELLOW}Templates:{Colors.END}")
        template_files = ['base.html', 'task_list.html', 'task_detail.html', 
                         'task_form.html', 'task_confirm_delete.html']
        for template in template_files:
            filepath = os.path.join(templates_path, template)
            exists = check_file_exists(filepath)
            print(f"  {check_mark(exists)} {template}")
            if not exists:
                all_good = False
    
    return all_good

def check_model_fields():
    """Verify the Task model has all required fields"""
    print_header("Model Fields Verification")
    
    models_file = 'todo_app/models.py'
    if not check_file_exists(models_file):
        print(f"{Colors.RED}models.py not found!{Colors.END}")
        return False
    
    with open(models_file, 'r') as f:
        content = f.read()
    
    # Required fields
    required_fields = {
        'title': r'title\s*=\s*models\.CharField.*max_length\s*=\s*200',
        'description': r'description\s*=\s*models\.TextField.*blank\s*=\s*True',
        'completed': r'completed\s*=\s*models\.BooleanField.*default\s*=\s*False',
        'created_at': r'created_at\s*=\s*models\.DateTimeField.*auto_now_add\s*=\s*True',
        'due_date': r'due_date\s*=\s*models\.DateField.*null\s*=\s*True.*blank\s*=\s*True'
    }
    
    all_good = True
    for field, pattern in required_fields.items():
        found = bool(re.search(pattern, content, re.DOTALL))
        print(f"{check_mark(found)} Task.{field}")
        if not found:
            all_good = False
    
    # Check for __str__ method
    has_str = '__str__' in content
    print(f"{check_mark(has_str)} __str__ method")
    
    # Check for is_overdue method
    has_overdue = 'is_overdue' in content
    print(f"{check_mark(has_overdue)} is_overdue() method")
    
    return all_good

def check_views():
    """Verify all required views exist"""
    print_header("Views Verification")
    
    views_file = 'todo_app/views.py'
    if not check_file_exists(views_file):
        print(f"{Colors.RED}views.py not found!{Colors.END}")
        return False
    
    with open(views_file, 'r') as f:
        content = f.read()
    
    required_views = [
        'task_list',
        'task_detail',
        'task_create',
        'task_update',
        'task_delete',
        'task_toggle_complete'
    ]
    
    all_good = True
    for view in required_views:
        # Check if function exists
        pattern = f'def {view}\\s*\\('
        found = bool(re.search(pattern, content))
        print(f"{check_mark(found)} {view} view")
        if not found:
            all_good = False
    
    # Check for proper imports
    imports_to_check = [
        ('get_object_or_404', 'from django.shortcuts import.*get_object_or_404'),
        ('messages', 'from django.contrib import messages'),
        ('redirect', 'from django.shortcuts import.*redirect')
    ]
    
    print(f"\n{Colors.YELLOW}Required Imports:{Colors.END}")
    for import_name, pattern in imports_to_check:
        found = bool(re.search(pattern, content))
        print(f"{check_mark(found)} {import_name}")
    
    return all_good

def check_urls():
    """Verify URL patterns"""
    print_header("URL Patterns Verification")
    
    urls_file = 'todo_app/urls.py'
    if not check_file_exists(urls_file):
        print(f"{Colors.RED}urls.py not found!{Colors.END}")
        return False
    
    with open(urls_file, 'r') as f:
        content = f.read()
    
    required_patterns = [
        ("task_list", r"path\(['\"]'['\"],.*name\s*=\s*['\"]task_list['\"]"),
        ("task_detail", r"path\(['\"]task/<int:pk>/['\"],.*name\s*=\s*['\"]task_detail['\"]"),
        ("task_create", r"path\(['\"]task/create/['\"],.*name\s*=\s*['\"]task_create['\"]"),
        ("task_update", r"path\(['\"]task/<int:pk>/update/['\"],.*name\s*=\s*['\"]task_update['\"]"),
        ("task_delete", r"path\(['\"]task/<int:pk>/delete/['\"],.*name\s*=\s*['\"]task_delete['\"]"),
        ("task_toggle_complete", r"path\(['\"]task/<int:pk>/toggle/['\"],.*name\s*=\s*['\"]task_toggle_complete['\"]")
    ]
    
    all_good = True
    for name, pattern in required_patterns:
        found = bool(re.search(pattern, content))
        print(f"{check_mark(found)} {name} URL pattern")
        if not found:
            all_good = False
    
    return all_good

def check_forms():
    """Verify form implementation"""
    print_header("Forms Verification")
    
    forms_file = 'todo_app/forms.py'
    if not check_file_exists(forms_file):
        print(f"{Colors.RED}forms.py not found!{Colors.END}")
        return False
    
    with open(forms_file, 'r') as f:
        content = f.read()
    
    checks = [
        ("TaskForm class", r'class TaskForm.*\(.*ModelForm.*\):'),
        ("Meta class", r'class Meta:'),
        ("model = Task", r'model\s*=\s*Task'),
        ("fields definition", r'fields\s*=\s*\['),
        ("clean_title method", r'def clean_title\('),
        ("clean_due_date method", r'def clean_due_date\('),
        ("ValidationError import", r'from django.*ValidationError')
    ]
    
    all_good = True
    for check_name, pattern in checks:
        found = bool(re.search(pattern, content, re.DOTALL))
        print(f"{check_mark(found)} {check_name}")
        if not found:
            all_good = False
    
    return all_good

def check_security_settings():
    """Verify security configurations"""
    print_header("Security Settings Verification")
    
    settings_file = 'todo_project/settings.py'
    if not check_file_exists(settings_file):
        print(f"{Colors.RED}settings.py not found!{Colors.END}")
        return False
    
    with open(settings_file, 'r') as f:
        content = f.read()
    
    security_checks = [
        ("SECRET_KEY from environment", r"SECRET_KEY\s*=\s*os\.environ\.get\(['\"](SECRET_KEY|DJANGO_SECRET_KEY)['\"]"),
        ("DEBUG from environment", r"DEBUG\s*=\s*os\.environ\.get\(['\"]DEBUG['\"]"),
        ("ALLOWED_HOSTS configuration", r"ALLOWED_HOSTS\s*="),
        ("CSRF middleware", r"django\.middleware\.csrf\.CsrfViewMiddleware"),
        ("Security middleware", r"django\.middleware\.security\.SecurityMiddleware")
    ]
    
    all_good = True
    for check_name, pattern in security_checks:
        found = bool(re.search(pattern, content))
        print(f"{check_mark(found)} {check_name}")
        if not found:
            all_good = False
    
    # Check .gitignore
    gitignore_file = '.gitignore'
    if check_file_exists(gitignore_file):
        with open(gitignore_file, 'r') as f:
            gitignore_content = f.read()
        
        print(f"\n{Colors.YELLOW}.gitignore checks:{Colors.END}")
        gitignore_patterns = ['.env', '*.pyc', 'db.sqlite3', '__pycache__']
        for pattern in gitignore_patterns:
            found = pattern in gitignore_content
            print(f"{check_mark(found)} {pattern}")
    
    return all_good

def check_requirements():
    """Verify requirements.txt has necessary packages"""
    print_header("Requirements File Verification")
    
    req_file = 'requirements.txt'
    if not check_file_exists(req_file):
        print(f"{Colors.RED}requirements.txt not found!{Colors.END}")
        return False
    
    with open(req_file, 'r') as f:
        content = f.read().lower()
    
    required_packages = [
        'django',
        'gunicorn',
        'dj-database-url',
        'psycopg2'
    ]
    
    all_good = True
    for package in required_packages:
        found = package in content
        print(f"{check_mark(found)} {package}")
        if not found:
            all_good = False
    
    return all_good

def run_pep8_check():
    """Run PEP8 compliance check"""
    print_header("PEP8 Compliance Check")
    
    try:
        # Try flake8 first
        result = subprocess.run(
            ['flake8', '.', '--exclude=migrations,venv,env', '--max-line-length=88', '--count'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"{Colors.GREEN}✓ No PEP8 violations found!{Colors.END}")
            return True
        else:
            print(f"{Colors.RED}✗ PEP8 violations found:{Colors.END}")
            print(result.stdout)
            return False
            
    except FileNotFoundError:
        print(f"{Colors.YELLOW}! flake8 not installed. Install with: pip install flake8{Colors.END}")
        return None

def main():
    """Run all verification checks"""
    print(f"{Colors.BLUE}{'*'*60}{Colors.END}")
    print(f"{Colors.BLUE}{'Django Todo Project Verification Script':^60}{Colors.END}")
    print(f"{Colors.BLUE}{'*'*60}{Colors.END}")
    
    # Check if we're in the right directory
    if not check_file_exists('manage.py'):
        print(f"\n{Colors.RED}Error: manage.py not found!{Colors.END}")
        print("Please run this script from your project root directory.")
        sys.exit(1)
    
    results = {
        'Directory Structure': check_directory_structure(),
        'Model Fields': check_model_fields(),
        'Views': check_views(),
        'URL Patterns': check_urls(),
        'Forms': check_forms(),
        'Security Settings': check_security_settings(),
        'Requirements': check_requirements(),
        'PEP8 Compliance': run_pep8_check()
    }
    
    # Summary
    print_header("Verification Summary")
    
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)
    
    for check, result in results.items():
        if result is True:
            status = f"{Colors.GREEN}PASSED{Colors.END}"
        elif result is False:
            status = f"{Colors.RED}FAILED{Colors.END}"
        else:
            status = f"{Colors.YELLOW}SKIPPED{Colors.END}"
        print(f"{check:.<40} {status}")
    
    print(f"\n{Colors.BLUE}Total:{Colors.END} {passed} passed, {failed} failed, {skipped} skipped")
    
    if failed == 0:
        print(f"\n{Colors.GREEN}🎉 Congratulations! Your project passes all verification checks!{Colors.END}")
    else:
        print(f"\n{Colors.YELLOW}⚠️  Some checks failed. Please review the output above.{Colors.END}")

if __name__ == "__main__":
    main()
