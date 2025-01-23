# memanggil berbagai library dan variabel yang dibutuhkan

import os
import sys
from typing import Text
 
from absl import logging
from tfx.orchestration import metadata, pipeline
from tfx.orchestration.beam.beam_dag_runner import BeamDagRunner
 
PIPELINE_NAME = "patient-stress-pipeline"
 
# pipeline inputs
DATA_ROOT = "data"
TRANSFORM_MODULE_FILE = "modules/patient_stress_transform.py"
TRAINER_MODULE_FILE = "modules/patient_stress_trainer.py"
# requirement_file = os.path.join(root, "requirements.txt")
 
# pipeline outputs
OUTPUT_BASE = "output"
serving_model_dir = os.path.join(OUTPUT_BASE, 'serving_model')
pipeline_root = os.path.join(OUTPUT_BASE, PIPELINE_NAME)
metadata_path = os.path.join(pipeline_root, "metadata.sqlite")

# menyatukan seluruh TFX component
# Fungsi di atas akan menghasilkan sebuah pipeline yang dijalankan menggunakan Apache Beam. Pipeline tersebut menggunakan mode multi processing dengan menyesuaikan jumlah CPU yang tersedia.

def init_local_pipeline(
    components, pipeline_root: Text
) -> pipeline.Pipeline:
    
    logging.info(f"Pipeline root set to: {pipeline_root}")
    beam_args = [
        "--direct_running_mode=multi_processing"
        # 0 auto-detect based on on the number of CPUs available 
        # during execution time.
        "----direct_num_workers=0" 
    ]
    
    return pipeline.Pipeline(
        pipeline_name=PIPELINE_NAME,
        pipeline_root=pipeline_root,
        components=components,
        enable_cache=True,
        metadata_connection_config=metadata.sqlite_metadata_connection_config(
            metadata_path
        ),
        eam_pipeline_args=beam_args
    )

# menjalankan pipeline
# membuat sebuah TFX component menggunakan fungsi init_components(). Selanjutnya, seluruh komponen tersebut disatukan menjadi sebuah machine learning pipeline dengan bantuan fungsi init_local_pipeline(). Pada bagian terakhir, pipeline tersebut dijalankan menggunakan Apache Beam sebagai pipeline orchestrator.
if __name__ == "__main__":
    logging.set_verbosity(logging.INFO)
    
    from modules.components import init_components
    
    components = init_components(
        DATA_ROOT,
        training_module=TRAINER_MODULE_FILE,
        transform_module=TRANSFORM_MODULE_FILE,
        training_steps=5000,
        eval_steps=1000,
        serving_model_dir=serving_model_dir,
    )
    
    pipeline = init_local_pipeline(components, pipeline_root)
    BeamDagRunner().run(pipeline=pipeline)

# Untuk menjalankan berkas local_pipeline.py, tulislah perintah berikut pada terminal atau windows PowerShell
# python .\local_pipeline.py 

#.\mlops-tfx-dev-ops\Scripts\activate
# where python
# "E:\ProgramData\anaconda3\envs\mlops-tfx-dev-ops\python.exe" local_pipeline.py