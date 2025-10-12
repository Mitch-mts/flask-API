import os
import pathlib
from pathlib import Path

class DatasetConfig:
    """Centralized configuration for dataset paths"""
    
    def __init__(self):
        self._base_data_dir = self._get_base_data_directory()
        self._athletes_file = "Athletes.xlsx"
        self._student_file = "StudentPerformance.csv"
        self._coaches_file = "Coaches.xlsx"
        self._entries_gender_file = "EntriesGender.xlsx"
        self._medals_file = "Medals.xlsx"
        self._teams_file = "Teams.xlsx"
    
    def _get_base_data_directory(self):
        """
        Get the base data directory from environment variable or use default.
        Priority:
        1. DATA_DIR environment variable
        2. /opt/app/data (common for production deployments)
        3. /usr/local/share/app/data (system-wide data directory)
        4. ./data (current working directory - fallback)
        """
        # Check for environment variable first
        data_dir = os.environ.get('DATA_DIR')
        if data_dir and os.path.exists(data_dir):
            return data_dir
        
        # Try common system directories
        system_dirs = [
            '/opt/app/data',           # Common for containerized apps
            '/usr/local/share/app/data',  # System-wide data directory
            '/var/lib/app/data',       # Alternative system data directory
            '/home/app/data',          # User-specific data directory
        ]
        
        for dir_path in system_dirs:
            if os.path.exists(dir_path):
                return dir_path
        
        # Fallback to relative path in current working directory
        current_dir = os.getcwd()
        fallback_dir = os.path.join(current_dir, 'data')
        return fallback_dir
    
    @property
    def base_data_dir(self):
        """Get the base data directory path"""
        return self._base_data_dir
    
    @property
    def athletes_dataset_path(self):
        """Get the full path to the athletes dataset"""
        return os.path.join(self._base_data_dir, self._athletes_file)
    
    @property
    def student_dataset_path(self):
        """Get the full path to the student dataset"""
        return os.path.join(self._base_data_dir, self._student_file)
    
    @property
    def coaches_dataset_path(self):
        """Get the full path to the coaches dataset"""
        return os.path.join(self._base_data_dir, self._coaches_file)
    
    @property
    def entries_gender_dataset_path(self):
        """Get the full path to the entries gender dataset"""
        return os.path.join(self._base_data_dir, self._entries_gender_file)
    
    @property
    def medals_dataset_path(self):
        """Get the full path to the medals dataset"""
        return os.path.join(self._base_data_dir, self._medals_file)
    
    @property
    def teams_dataset_path(self):
        """Get the full path to the teams dataset"""
        return os.path.join(self._base_data_dir, self._teams_file)
    
    def get_dataset_path(self, dataset_name):
        """
        Get the full path for any dataset by name
        
        Args:
            dataset_name (str): Name of the dataset (e.g., 'athletes', 'student', etc.)
            
        Returns:
            str: Full path to the dataset file
            
        Raises:
            ValueError: If dataset_name is not recognized
        """
        dataset_mapping = {
            'athletes': self.athletes_dataset_path,
            'student': self.student_dataset_path,
            'coaches': self.coaches_dataset_path,
            'entries_gender': self.entries_gender_dataset_path,
            'medals': self.medals_dataset_path,
            'teams': self.teams_dataset_path,
        }
        
        if dataset_name not in dataset_mapping:
            raise ValueError(f"Unknown dataset: {dataset_name}. Available datasets: {list(dataset_mapping.keys())}")
        
        return dataset_mapping[dataset_name]
    
    def validate_data_directory(self):
        """
        Validate that the data directory exists and contains expected files
        
        Returns:
            dict: Validation results with status and missing files
        """
        validation_result = {
            'valid': True,
            'base_directory': self._base_data_dir,
            'exists': os.path.exists(self._base_data_dir),
            'missing_files': [],
            'available_files': []
        }
        
        if not validation_result['exists']:
            validation_result['valid'] = False
            return validation_result
        
        # Check for each dataset file
        expected_files = [
            self._athletes_file,
            self._student_file,
            self._coaches_file,
            self._entries_gender_file,
            self._medals_file,
            self._teams_file
        ]
        
        for filename in expected_files:
            filepath = os.path.join(self._base_data_dir, filename)
            if os.path.exists(filepath):
                validation_result['available_files'].append(filename)
            else:
                validation_result['missing_files'].append(filename)
        
        if validation_result['missing_files']:
            validation_result['valid'] = False
        
        return validation_result

# Create a global instance for use throughout the application
dataset_config = DatasetConfig()
