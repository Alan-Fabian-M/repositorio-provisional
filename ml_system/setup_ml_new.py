#!/usr/bin/env python3
"""
Complete ML System Setup Script
Orchestrates the setup of the entire ML system
"""

import os
import sys
import subprocess
from pathlib import Path
import logging
import argparse

# Configure logging with console and file output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ml_setup.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MLSystemSetup:
    def __init__(self, project_root=None):
        # Set up paths
        if project_root is None:
            self.project_root = Path(__file__).parent.parent
        else:
            self.project_root = Path(project_root)
        
        self.ml_system_dir = self.project_root / "ml_system"
        self.scripts_dir = self.ml_system_dir / "scripts"
        self.data_dir = self.ml_system_dir / "data"
        self.models_dir = self.ml_system_dir / "modelos"
        self.tests_dir = self.ml_system_dir / "tests"
        
        # Ensure all directories exist
        self.data_dir.mkdir(exist_ok=True, parents=True)
        self.models_dir.mkdir(exist_ok=True, parents=True)
        self.tests_dir.mkdir(exist_ok=True, parents=True)
    
    def install_dependencies(self):
        """Install required ML dependencies"""
        logger.info("📦 Installing ML dependencies...")
        
        dependencies = [
            "pandas>=1.5.0",
            "numpy>=1.21.0",
            "scikit-learn>=1.0.0",
            "joblib>=1.1.0",
            "psycopg2-binary>=2.9.0"
        ]
        
        for dep in dependencies:
            try:
                logger.info(f"Installing {dep}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
                logger.info(f"✅ {dep} installed successfully")
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Failed to install {dep}: {e}")
                return False
        
        return True
    
    def extract_data(self):
        """Extract data from PostgreSQL database"""
        logger.info("🗃️ Extracting data from database...")
        
        extractor_path = self.scripts_dir / "standalone_data_extractor.py"
        
        if not extractor_path.exists():
            logger.error(f"❌ Data extractor not found at {extractor_path}")
            return False
        
        try:
            # First check if data already exists
            if (self.data_dir / "students_data.csv").exists() and \
               (self.data_dir / "courses_data.csv").exists() and \
               (self.data_dir / "enrollments_data.csv").exists():
                logger.info("✅ Data files already exist, skipping extraction")
                return True
            
            logger.info("Running data extractor...")
            process = subprocess.Popen(
                [sys.executable, str(extractor_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                logger.info("✅ Data extraction successful")
                logger.info(f"Output: {stdout}")
                return True
            else:
                logger.error(f"❌ Data extraction failed: {stderr}")
                return False
        
        except Exception as e:
            logger.error(f"❌ Error running data extractor: {e}")
            return False
    
    def train_models(self):
        """Train all ML models"""
        logger.info("🧠 Training ML models...")
        
        trainer_path = self.scripts_dir / "train_models_new.py"
        
        if not trainer_path.exists():
            logger.error(f"❌ Model trainer not found at {trainer_path}")
            return False
        
        try:
            # Check if models already exist
            if (self.models_dir / "enrollment_prediction_model.pkl").exists() and \
               (self.models_dir / "course_recommendation_model.pkl").exists() and \
               (self.models_dir / "performance_prediction_model.pkl").exists():
                logger.info("✅ Model files already exist, skipping training")
                return True
            
            logger.info("Running model trainer...")
            process = subprocess.Popen(
                [sys.executable, str(trainer_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                logger.info("✅ Model training successful")
                logger.info(f"Output: {stdout}")
                return True
            else:
                logger.error(f"❌ Model training failed: {stderr}")
                return False
        
        except Exception as e:
            logger.error(f"❌ Error training models: {e}")
            return False
    
    def run_integration_test(self):
        """Run integration tests"""
        logger.info("🧪 Running integration tests...")
        
        test_path = self.tests_dir / "ml_integration_test.py"
        
        if not test_path.exists():
            logger.error(f"❌ Integration test not found at {test_path}")
            return False
        
        try:
            logger.info("Running integration test...")
            process = subprocess.Popen(
                [sys.executable, str(test_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                logger.info("✅ Integration test successful")
                logger.info(stdout)
                return True
            else:
                logger.error(f"❌ Integration test failed: {stderr}")
                return False
        
        except Exception as e:
            logger.error(f"❌ Error running integration test: {e}")
            return False
    
    def setup_complete_pipeline(self):
        """Run the complete ML setup pipeline"""
        logger.info("🚀 Starting ML system setup...")
        
        steps = [
            ("Installing dependencies", self.install_dependencies),
            ("Extracting data", self.extract_data),
            ("Training models", self.train_models),
            ("Running integration tests", self.run_integration_test)
        ]
        
        all_successful = True
        for step_name, step_func in steps:
            logger.info(f"\n===== {step_name} =====")
            if step_func():
                logger.info(f"✅ {step_name} completed successfully")
            else:
                logger.error(f"❌ {step_name} failed")
                all_successful = False
                break
        
        if all_successful:
            logger.info("\n🎉 ML SYSTEM SETUP COMPLETED SUCCESSFULLY!")
            logger.info("\nYou can now use the ML system through the Flask API:")
            logger.info("1. Run the Flask server: python run.py")
            logger.info("2. Access ML endpoints at http://localhost:5000/ml/")
            logger.info("3. Test prediction with: curl -X POST http://localhost:5000/ml/predict/performance -H 'Content-Type: application/json' -d '{\"edad\": 16}'")
            return True
        else:
            logger.error("\n❌ ML SYSTEM SETUP FAILED")
            logger.error("Please check the logs above for errors")
            return False

def main():
    """Main function to run the setup script"""
    parser = argparse.ArgumentParser(description='ML System Setup Script')
    parser.add_argument('--project-root', help='Root directory of the project')
    parser.add_argument('--skip-deps', action='store_true', help='Skip installing dependencies')
    parser.add_argument('--skip-data', action='store_true', help='Skip data extraction')
    parser.add_argument('--skip-train', action='store_true', help='Skip model training')
    parser.add_argument('--skip-test', action='store_true', help='Skip integration tests')
    
    args = parser.parse_args()
    
    setup = MLSystemSetup(project_root=args.project_root)
    
    steps = []
    if not args.skip_deps:
        steps.append(("Installing dependencies", setup.install_dependencies))
    if not args.skip_data:
        steps.append(("Extracting data", setup.extract_data))
    if not args.skip_train:
        steps.append(("Training models", setup.train_models))
    if not args.skip_test:
        steps.append(("Running integration tests", setup.run_integration_test))
    
    all_successful = True
    for step_name, step_func in steps:
        logger.info(f"\n===== {step_name} =====")
        if step_func():
            logger.info(f"✅ {step_name} completed successfully")
        else:
            logger.error(f"❌ {step_name} failed")
            all_successful = False
            break
    
    if all_successful:
        logger.info("\n🎉 ML SYSTEM SETUP COMPLETED SUCCESSFULLY!")
        sys.exit(0)
    else:
        logger.error("\n❌ ML SYSTEM SETUP FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()
