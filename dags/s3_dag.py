from airflow import DAG
from airflow.providers.amazon.aws.operators.s3 import S3ListOperator, S3CreateBucketOperator, S3CopyObjectOperator
from datetime import datetime, timedelta
from airflow.providers.amazon.aws.transfers.local_to_s3 import LocalFilesystemToS3Operator
from airflow.operators.bash import BashOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.operators.python import PythonOperator



default_args = {
    'owner':'abhi',
    'retries':5,
    'retry_delay': timedelta(minutes=2)
}


def local_to_s3(filename: str ,key: str , bucket_name : str) -> None:
    hook=S3Hook('s3_conn')
    hook.load_file(filename=filename, key=key, bucket_name= bucket_name)


def s3_to_local(local_filepath: str ,key: str , bucket_name : str) -> None:
    hook=S3Hook('s3_conn')
    hook.download_file(local_filepath=local_filepath, key=key, bucket_name= bucket_name)


dag = DAG(
    dag_id='perform_s3_tasks',
    description='this will implement various s3 operations',
    start_date=datetime(2022, 7,10,2),
    schedule_interval=None,
    default_args=default_args
)

start = BashOperator(
    task_id = 'start',
    bash_command= 'echo The dag has started running',
    dag=dag
)

"""
create_bucket = S3CreateBucketOperator(
        task_id="create_bucket",
        bucket_name='airflow-test-create-bucket',
        aws_conn_id='s3_conn'
    )
"""

upload_to_s3 = PythonOperator(
        task_id='upload_to_s3',
        python_callable=local_to_s3,
        dag=dag,
        op_kwargs={
            'filename':'/Users/abhishekpatkar/Documents/Projects/airflow/local_files/local_file/load_file_into_s3.txt',
            'key':'load_file_into_s3.txt',
            'bucket_name':'airflow-s3-fileloader'
            }
)

download_from_s3 = PythonOperator(
        task_id='download_from_s3',
        python_callable=s3_to_local,
        dag=dag,
        op_kwargs={
            'local_filepath':'/Users/abhishekpatkar/Documents/Projects/airflow/local_files/local_file/',
            'key':'test_file.txt',
            'bucket_name':'airflow-s3-fileloader'
            }
)

"""
copy_files = S3CopyObjectOperator(
        task_id='copy_files_between_buckets',
        source_bucket_key='s3://airflow-s3-fileloader/test_file.txt',
        dest_bucket_key='s3://airflow-test-create-bucket/test_file.txt',
        source_bucket_name=None,
        dest_bucket_name=None,
        aws_conn_id='s3_conn',
        dag=dag
    )


load_file_into_s3 = LocalFilesystemToS3Operator(
        task_id='load_files_into_bucket',
        filename='/load_file_into_s3.txt',
        dest_key='airflow-s3-fileloader',
        dest_bucket='airflow_source',
        aws_conn_id='s3_conn',
        verify=None,
        dag=dag
    )
"""

list_bucket = S3ListOperator(
            task_id='list_files_in_bucket',
            bucket='airflow-s3-fileloader',
            delimiter='/',
            aws_conn_id='s3_conn',
            dag=dag
        )

end = BashOperator(
    task_id = 'end',
    bash_command= 'echo The dag has completed its run',
    dag=dag
)



start >> upload_to_s3 >> download_from_s3 >>list_bucket >> end