# Memanggil berbagai library dan variabel yang dibutuhkan
import os
import sys
from typing import Text
from absl import logging
from tfx.orchestration import metadata, pipeline
from tfx.orchestration.beam.beam_dag_runner import BeamDagRunner

# Nama pipeline
PIPELINE_NAME = "patient-stress-pipeline"

# Pipeline inputs
DATA_ROOT = "data"  # Folder tempat data input berada
TRANSFORM_MODULE_FILE = "modules/patient_stress_transform.py"  # Transform module
TRAINER_MODULE_FILE = "modules/patient_stress_trainer.py"  # Trainer module

# Pipeline outputs
OUTPUT_BASE = "output"  # Root folder untuk output pipeline
SERVING_MODEL_DIR = os.path.join(OUTPUT_BASE, "serving_model")
PIPELINE_ROOT = os.path.join(OUTPUT_BASE, PIPELINE_NAME)
METADATA_PATH = os.path.join(PIPELINE_ROOT, "metadata.sqlite")


# Fungsi untuk membuat TFX pipeline
def init_local_pipeline(components, pipeline_root: Text) -> pipeline.Pipeline:
    """
    Fungsi untuk inisialisasi TFX pipeline.
    Args:
        components: List komponen TFX yang akan digunakan dalam pipeline.
        pipeline_root: Lokasi output dari pipeline.
    Returns:
        pipeline: Objek pipeline yang akan dijalankan.
    """
    logging.info(f"Pipeline root set to: {pipeline_root}")
    
    # Apache Beam arguments
    beam_args = [
        "--direct_running_mode=multi_processing",  # Mode eksekusi menggunakan multiprocessing
        "--direct_num_workers=0"  # 0 berarti auto-detect jumlah CPU yang tersedia
    ]
    
    return pipeline.Pipeline(
        pipeline_name=PIPELINE_NAME,
        pipeline_root=pipeline_root,
        components=components,
        enable_cache=True,  # Menggunakan caching untuk menghemat waktu
        metadata_connection_config=metadata.sqlite_metadata_connection_config(
            METADATA_PATH
        ),
        beam_pipeline_args=beam_args,  # Argumen untuk Apache Beam
    )


# Menjalankan pipeline
if __name__ == "__main__":
    # Set level logging
    logging.set_verbosity(logging.INFO)

    # Menambahkan path modul (opsional, jika modul tidak terdeteksi)
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    try:
        # Memastikan modul ditemukan
        from modules.components import init_components
    except ModuleNotFoundError:
        logging.error("Module 'modules.components' tidak ditemukan. Pastikan path benar.")
        sys.exit(1)

    # Inisialisasi komponen pipeline
    components = init_components(
        data_root=DATA_ROOT,
        training_module=TRAINER_MODULE_FILE,
        transform_module=TRANSFORM_MODULE_FILE,
        training_steps=5000,
        eval_steps=1000,
        serving_model_dir=SERVING_MODEL_DIR,
    )

    # Membuat pipeline
    pipeline_obj = init_local_pipeline(components, PIPELINE_ROOT)

    # Menjalankan pipeline menggunakan Apache Beam
    logging.info("Menjalankan pipeline...")
    BeamDagRunner().run(pipeline=pipeline_obj)
    logging.info("Pipeline selesai dijalankan.")
