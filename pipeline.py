import logging
import subprocess
import os
import sys

logging.basicConfig(
    filename='pipeline.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def run_extract():
    try:
        logging.info('Starting extract...')
        subprocess.run([sys.executable, 'Pipeline/src/extract_weather.py'], check=True)
        subprocess.run([sys.executable, 'Pipeline/src/extract_airquality.py'], check=True)
        logging.info("Extract completed successfully")
    except Exception as e:
        logging.error(f'Extract failed: {e}')

def run_transform():
    try:
        logging.info('Starting transform...')
        subprocess.run([sys.executable, 'Pipeline/src/transform_weather.py'], check=True)
        subprocess.run([sys.executable, 'Pipeline/src/transform_airquality.py'], check=True)
        logging.info('Transform completed successfully')
    except Exception as e:
        logging.error(f'Transform failed: {e}')

def run_load():
    try:
        logging.info('Starting to load...')
        subprocess.run([sys.executable, 'Pipeline/src/load.py'], check=True)
        logging.info('Load completed successfully')
    except Exception as e:
        logging.error(f'Loading failed: {e}')


if __name__ == "__main__":
    logging.info("==== Pipeline started ====")
    run_extract()
    run_transform()
    run_load()
    logging.info("==== Pipeline finished ====")