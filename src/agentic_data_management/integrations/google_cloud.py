"""
Google Cloud Integration Module

This module provides integration with Google Cloud services for the agent system.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import logging
from google.cloud import bigquery
from google.cloud import storage
from google.cloud import firestore
from google.cloud import pubsub_v1
from google.api_core import retry
from google.cloud.exceptions import GoogleCloudError

class GoogleCloudIntegration:
    """Provides integration with Google Cloud services."""
    
    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize Google Cloud integration.
        
        Args:
            project_id: Google Cloud project ID
            location: Default location for resources
            config: Optional configuration dictionary
        """
        self.project_id = project_id
        self.location = location
        self.config = config or {}
        self.logger = logging.getLogger("google_cloud_integration")
        
        # Initialize clients
        self._initialize_clients()
    
    def _initialize_clients(self) -> None:
        """Initialize Google Cloud clients."""
        try:
            self.bq_client = bigquery.Client(project=self.project_id)
            self.storage_client = storage.Client(project=self.project_id)
            self.firestore_client = firestore.Client(project=self.project_id)
            self.pubsub_client = pubsub_v1.PublisherClient()
        except GoogleCloudError as e:
            self.logger.error(f"Failed to initialize Google Cloud clients: {str(e)}")
            raise
    
    async def store_metadata(
        self,
        collection: str,
        document_id: str,
        data: Dict[str, Any]
    ) -> None:
        """Store metadata in Firestore.
        
        Args:
            collection: Firestore collection name
            document_id: Document ID
            data: Document data
        """
        try:
            doc_ref = self.firestore_client.collection(collection).document(document_id)
            doc_ref.set(data)
        except GoogleCloudError as e:
            self.logger.error(f"Failed to store metadata: {str(e)}")
            raise
    
    async def get_metadata(
        self,
        collection: str,
        document_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get metadata from Firestore.
        
        Args:
            collection: Firestore collection name
            document_id: Document ID
            
        Returns:
            Document data if found, None otherwise
        """
        try:
            doc_ref = self.firestore_client.collection(collection).document(document_id)
            doc = doc_ref.get()
            return doc.to_dict() if doc.exists else None
        except GoogleCloudError as e:
            self.logger.error(f"Failed to get metadata: {str(e)}")
            raise
    
    async def store_data(
        self,
        bucket_name: str,
        blob_name: str,
        data: bytes
    ) -> str:
        """Store data in Cloud Storage.
        
        Args:
            bucket_name: Storage bucket name
            blob_name: Blob name
            data: Data to store
            
        Returns:
            Public URL of the stored data
        """
        try:
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.upload_from_string(data)
            return blob.public_url
        except GoogleCloudError as e:
            self.logger.error(f"Failed to store data: {str(e)}")
            raise
    
    async def query_data(
        self,
        query: str,
        params: Optional[List[Any]] = None
    ) -> List[Dict[str, Any]]:
        """Query data from BigQuery.
        
        Args:
            query: SQL query
            params: Optional query parameters
            
        Returns:
            Query results
        """
        try:
            job_config = bigquery.QueryJobConfig(
                query_parameters=params or []
            )
            query_job = self.bq_client.query(
                query,
                job_config=job_config,
                location=self.location
            )
            return [dict(row) for row in query_job]
        except GoogleCloudError as e:
            self.logger.error(f"Failed to query data: {str(e)}")
            raise
    
    async def publish_event(
        self,
        topic_name: str,
        data: Dict[str, Any]
    ) -> str:
        """Publish event to Pub/Sub.
        
        Args:
            topic_name: Pub/Sub topic name
            data: Event data
            
        Returns:
            Message ID
        """
        try:
            topic_path = self.pubsub_client.topic_path(
                self.project_id,
                topic_name
            )
            future = self.pubsub_client.publish(
                topic_path,
                data=str(data).encode("utf-8")
            )
            return future.result()
        except GoogleCloudError as e:
            self.logger.error(f"Failed to publish event: {str(e)}")
            raise
    
    @retry.Retry()
    async def create_dataset(
        self,
        dataset_id: str,
        description: Optional[str] = None
    ) -> None:
        """Create a BigQuery dataset.
        
        Args:
            dataset_id: Dataset ID
            description: Optional dataset description
        """
        try:
            dataset = bigquery.Dataset(
                f"{self.project_id}.{dataset_id}"
            )
            dataset.location = self.location
            if description:
                dataset.description = description
            self.bq_client.create_dataset(dataset)
        except GoogleCloudError as e:
            self.logger.error(f"Failed to create dataset: {str(e)}")
            raise
    
    @retry.Retry()
    async def create_table(
        self,
        dataset_id: str,
        table_id: str,
        schema: List[Dict[str, Any]]
    ) -> None:
        """Create a BigQuery table.
        
        Args:
            dataset_id: Dataset ID
            table_id: Table ID
            schema: Table schema
        """
        try:
            table_ref = f"{self.project_id}.{dataset_id}.{table_id}"
            table = bigquery.Table(table_ref, schema=schema)
            self.bq_client.create_table(table)
        except GoogleCloudError as e:
            self.logger.error(f"Failed to create table: {str(e)}")
            raise 