"""
Library management module for Mistral AI.
Provides functions to manage libraries and documents for agent access.
"""

from mistralai.client import Mistral
from typing import List, Dict, Any, Optional, Union
import os
import time
from library.ConfigManager import config


def list_libraries(api_key: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    List all libraries accessible to the current API key.

    Args:
        api_key (str, optional): Your Mistral API key. Uses config.get("mistral_key") if not provided

    Returns:
        list: List of library objects with id, name, description, etc.

    Example:
        >>> # Using default API key from ConfigManager
        >>> libraries = list_libraries()
        >>> for library in libraries:
        ...     print(f"Library: {library.id} - {library.name}")

        >>> # Override with specific API key
        >>> libraries = list_libraries(api_key="different_key")
    """
    # Use default from secrets if not provided
    api_key = api_key or config.get("mistral_key")

    client = Mistral(api_key=api_key)
    libraries_response = client.beta.libraries.list()

    # Handle different response formats
    if hasattr(libraries_response, 'data'):
        libraries = libraries_response.data
    elif isinstance(libraries_response, list):
        libraries = libraries_response
    else:
        # Try to iterate over the response
        libraries = list(libraries_response)
    return libraries


def get_library(library_id: Optional[str] = None, api_key: Optional[str] = None) -> dict:
    """
    Get detailed information about a specific library.

    Args:
        api_key (str, optional): Your Mistral API key. Uses config.get("mistral_key") if not provided
        library_id (str): The ID of the library to retrieve

    Returns:
        dict: Library details including id, name, description, created_at, etc.

    Raises:
        Exception: If the library doesn't exist or API request fails

    Example:
        >>> # Using default API key
        >>> library = get_library(library_id="lib_123")
        >>> print(f"Library name: {library.name}")

        >>> # Override API key
        >>> library = get_library(api_key="different_key", library_id="lib_123")
    """
    # Use default from secrets if not provided
    api_key = api_key or config.get("mistral_key")
    if library_id is None:
        raise ValueError("library_id must be explicitly provided")

    client = Mistral(api_key=api_key)
    library = client.beta.libraries.get(library_id=library_id)
    return library


def create_library(name: str, api_key: Optional[str] = None, description: Optional[str] = None) -> dict:
    """
    Create a new library for storing documents.

    Args:
        api_key (str, optional): Your Mistral API key. Uses config.get("mistral_key") if not provided
        name (str): Name of the new library
        description (str, optional): Description of the library's purpose

    Returns:
        dict: The newly created library object

    Example:
        >>> # Using default API key
        >>> library = create_library(
        ...     name="Robot Documentation",
        ...     description="Technical documentation for robot operations"
        ... )
        >>> print(f"Created library: {library.id}")

        >>> # Override API key
        >>> library = create_library(
        ...     api_key="different_key",
        ...     name="Robot Documentation",
        ...     description="Technical documentation for robot operations"
        ... )
    """
    # Use default from secrets if not provided
    api_key = api_key or config.get("mistral_key")

    client = Mistral(api_key=api_key)

    library_data = {
        "name": name
    }

    if description:
        library_data["description"] = description

    library = client.beta.libraries.create(**library_data)
    return library


def upload_document(
    file_path: str,
    library_id: Optional[str] = None,
    api_key: Optional[str] = None,
    document_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Upload a document to a library.

    Supports common text formats: TXT, CSV, PDF, MD, etc.

    Args:
        api_key (str, optional): Your Mistral API key. Uses config.get("mistral_key") if not provided
        library_id (str): The ID of the target library
        file_path (str): Path to the file to upload. Can be:
                        - A filename (e.g., "programming_blocks.md") to load from agent_files/documents/
                        - A full path to any document file
        document_name (str, optional): Custom name for the document in the library

    Returns:
        dict: The uploaded document object

    Raises:
        FileNotFoundError: If the file doesn't exist
        Exception: If upload fails or file type is unsupported

    Example:
        >>> # Using default API key and default documents folder
        >>> document = upload_document(
        ...     library_id="lib_123",
        ...     file_path="programming_blocks.md",  # Looks in agent_files/documents/
        ...     document_name="mBlock Programming Guide"
        ... )
        >>> print(f"Uploaded document: {document.id}")

        >>> # Using full path
        >>> document = upload_document(
        ...     library_id="lib_123",
        ...     file_path="/full/path/to/robot_manual.txt",
        ...     document_name="Robot Operation Manual"
        ... )

        >>> # Override API key
        >>> document = upload_document(
        ...     api_key="different_key",
        ...     library_id="lib_123",
        ...     file_path="technological_details_robot.md",  # Looks in agent_files/documents/
        ...     document_name="Robot Technical Specs"
        ... )
    """
    # Use default from secrets if not provided
    api_key = api_key or config.get("mistral_key")
    if library_id is None:
        raise ValueError("library_id must be explicitly provided")

    # Check if file_path is just a filename (no path), look in default documents folder
    if not os.path.isfile(file_path) and not os.path.isabs(file_path):
        # Try to find the file in the default documents directory
        default_documents_dir = os.path.join('agent_files', 'documents')
        potential_path = os.path.join(default_documents_dir, file_path)
        if os.path.isfile(potential_path):
            file_path = potential_path

    # Validate file exists
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Check file type (basic validation)
    file_ext = os.path.splitext(file_path)[1].lower()
    supported_extensions = {'.txt', '.csv', '.pdf', '.md', '.markdown', '.json'}

    if file_ext not in supported_extensions:
        raise ValueError(f"Unsupported file type: {file_ext}. Supported: {', '.join(supported_extensions)}")

    client = Mistral(api_key=api_key)

    # Use custom name or fallback to filename
    display_name = document_name or os.path.basename(file_path)

    # Upload the document using the Mistral File model
    from mistralai.client.models.file import File as MistralFile

    try:
        with open(file_path, 'rb') as file:
            file_content = file.read()

        # Create File object with the correct parameter names
        file_obj = MistralFile(content=file_content, fileName=display_name)

        document = client.beta.libraries.documents.upload(
            library_id=library_id,
            file=file_obj
        )
        return document
    except Exception as e:
        # Check if this is a duplicate document error (HTTP 409 or similar)
        error_msg = str(e).lower()
        if "already exists" in error_msg or "duplicate" in error_msg:
            # Try to find the existing document
            try:
                existing_docs = client.beta.libraries.documents.list(library_id=library_id)
                for doc in existing_docs:
                    if hasattr(doc, 'filename') and doc.filename == display_name:
                        return doc
                    elif hasattr(doc, 'id') and str(doc.id) in error_msg:
                        # If the error contains the document ID, return that document
                        return client.beta.libraries.documents.get(
                            library_id=library_id,
                            document_id=doc.id
                        )
            except Exception:
                pass
            raise Exception(f"Document already exists but could not be retrieved: {e}") from e
        else:
            raise Exception(f"Document upload failed: {e}") from e


def upload_document_and_wait(
    library_id: str,
    file_path: str,
    document_name: Optional[str] = None,
    api_key: Optional[str] = None,
    max_wait_time: int = 60,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Upload a document to a library and wait for processing to complete.
    
    This function uploads a document and monitors its processing status until completion,
    making it easier to ensure documents are ready for agent use.
    
    Args:
        library_id: ID of the library to upload to
        file_path: Path to the file to upload
        document_name: Optional custom name for the document
        api_key: Your Mistral API key (uses config.get("mistral_key") if not provided)
        max_wait_time: Maximum time to wait for processing in seconds (default: 60)
        verbose: Whether to print progress updates (default: True)
        
    Returns:
        The processed document object
        
    Raises:
        Exception: If upload fails or processing doesn't complete within max_wait_time
        
    Example:
        >>> # Upload and wait for processing
        >>> document = upload_document_and_wait(
        ...     library_id="lib_123",
        ...     file_path="paper.pdf",
        ...     document_name="research_paper.pdf",
        ...     verbose=True
        ... )
        >>> print(f"Document ready: {document.id}")
    """
    # First upload the document
    if verbose:
        print(f"📤 Uploading document to library {library_id}...")
    
    # Auto-set document name if not provided
    if document_name is None:
        document_name = os.path.basename(file_path)
    
    document = upload_document(
        library_id=library_id,
        file_path=file_path,
        document_name=document_name,
        api_key=api_key
    )
    
    if verbose:
        print(f"✅ Upload complete! Document ID: {document.id}")
        print(f"   Initial status: {document.processing_status}")
    
    # Wait for processing to complete
    if verbose:
        print(f"🕒 Waiting for processing to complete (max {max_wait_time}s)...")
    
    start_time = time.time()
    api_key = api_key or config.get("mistral_key")
    
    while time.time() - start_time < max_wait_time:
        # Get current document status
        docs = list_library_documents(library_id=library_id, api_key=api_key, display=False)
        current_doc = next((d for d in docs if d.id == document.id), None)
        
        if current_doc:
            current_status = current_doc.processing_status
            if verbose:
                print(f"   Status: {current_status}", end="\r")
            
            # Check if processing is complete
            if current_status in ['Completed', 'completed', 'done']:
                if verbose:
                    print(f"   ✅ Processing completed! Status: {current_status}")
                    tokens = getattr(current_doc, 'tokens_processing_total', 'N/A')
                    print(f"   Tokens extracted: {tokens}")
                return current_doc
        
        time.sleep(5)  # Check every 5 seconds
    
    # If we get here, processing didn't complete in time
    raise Exception(f"❌ Document processing did not complete within {max_wait_time} seconds")


def list_all_libraries(api_key: Optional[str] = None, display: bool = True) -> List[Dict[str, Any]]:
    """
    List all libraries accessible to the current API key.

    This function provides both programmatic access to library data and optional
    formatted display, making it consistent with other list_* functions in the library.

    Args:
        api_key (str, optional): Your Mistral AI API key. Uses config.get("mistral_key") if not provided
        display (bool, optional): If True, prints the libraries in a formatted table. Default: True

    Returns:
        list: List of library objects (same format as list_libraries())

    Example:
        >>> # Get libraries without displaying
        >>> libraries = list_all_libraries(display=False)
        >>> for lib in libraries:
        ...     print(f"Library: {lib.name} ({lib.id})")

        >>> # Get and display libraries (default behavior)
        >>> libraries = list_all_libraries()

        >>> # Override API key
        >>> libraries = list_all_libraries(api_key="different_key", display=True)
    """
    # Use default from secrets if not provided
    api_key = api_key or config.get("mistral_key")

    libraries = list_libraries(api_key=api_key)

    if display:
        if not libraries:
            print("📚 No libraries found.")
        else:
            # Print header
            print("\n" + "="*80)
            print("📚 YOUR MISTRAL AI LIBRARIES")
            print("="*80)

            # Print each library with formatting
            for i, library in enumerate(libraries, 1):
                # Handle both dictionary and Pydantic object formats
                if hasattr(library, 'get'):  # Dictionary format
                    library_id = library.get('id', 'N/A')
                    name = library.get('name', 'Unnamed Library')
                    description = library.get('description', 'No description')
                    created_at = library.get('created_at', 'Unknown date')
                else:  # Pydantic object format
                    library_id = getattr(library, 'id', 'N/A')
                    name = getattr(library, 'name', 'Unnamed Library')
                    description = getattr(library, 'description', 'No description')
                    created_at = getattr(library, 'created_at', 'Unknown date')

                print(f"\n📖 Library #{i}")
                print(f"   ID: {library_id}")
                print(f"   Name: {name}")
                print(f"   Description: {description}")
                print(f"   Created: {created_at}")
                print("-" * 80)

            print(f"\n📊 Total: {len(libraries)} library{'es' if len(libraries) != 1 else ''}")
            print("="*80 + "\n")

    return libraries


def delete_library(library_id: Optional[str] = None, api_key: Optional[str] = None) -> bool:
    """
    Delete a library and all its contents.

    Args:
        api_key (str, optional): Your Mistral API key. Uses config.get("mistral_key") if not provided
        library_id (str): The ID of the library to delete

    Returns:
        bool: True if deletion was successful

    Example:
        >>> # Using default API key
        >>> success = delete_library(library_id="lib_123")
        >>> print(f"Library deleted: {success}")

        >>> # Override API key
        >>> success = delete_library(library_id="lib_123",api_key="different_key")
    """
    # Use default from secrets if not provided
    api_key = api_key or config.get("mistral_key")
    if library_id is None:
        raise ValueError("library_id must be explicitly provided")

    client = Mistral(api_key=api_key)
    client.beta.libraries.delete(library_id=library_id)
    return True


def remove_all_documents_from_library(
    library_id: Optional[str] = None,
    api_key: Optional[str] = None,
    confirm: bool = True
) -> int:
    """
    Remove all documents from a library.

    Args:
        library_id (str, optional): The ID of the library to clear. Must be explicitly provided
        api_key (str, optional): Your Mistral AI API key. Uses config.get("mistral_key") if not provided
        confirm (bool, optional): If True, asks for confirmation before deleting. Default: True

    Returns:
        int: Number of documents deleted

    Raises:
        Exception: If the API request fails

    Example:
        >>> # Remove all documents with confirmation
        >>> count = remove_all_documents_from_library(library_id="lib_123")
        >>> print(f"Deleted {count} documents")

        >>> # Remove all documents without confirmation
        >>> count = remove_all_documents_from_library(library_id="lib_123", confirm=False)

        >>> # Override API key
        >>> count = remove_all_documents_from_library(library_id="lib_123", api_key="different_key")
    """
    # Use defaults from Configuration if not provided
    api_key = api_key or config.get("mistral_key")
    if library_id is None:
        raise ValueError("library_id must be explicitly provided")

    client = Mistral(api_key=api_key)

    # Get list of documents in the library
    try:
        documents = list_library_documents(library_id=library_id, api_key=api_key)

        if not documents:
            print("📚 Library is already empty.")
            return 0

        # Ask for confirmation unless confirm=False
        if confirm:
            print(f"🚨 WARNING: This will permanently delete {len(documents)} document{'s' if len(documents) != 1 else ''} from library {library_id}")
            response = input("Type 'DELETE' to confirm: ")
            if response.strip().upper() != 'DELETE':
                print("🔒 Operation cancelled.")
                return 0

        # Delete each document
        deleted_count = 0
        for doc in documents:
            try:
                doc_id = getattr(doc, 'id', None)
                if doc_id:
                    client.beta.libraries.documents.delete(
                        library_id=library_id,
                        document_id=doc_id
                    )
                    deleted_count += 1
                    print(f"🗑️  Deleted document: {getattr(doc, 'filename', 'Unknown')} ({doc_id})")
            except Exception as e:
                print(f"❌ Failed to delete document {getattr(doc, 'id', 'Unknown')}: {e}")

        print(f"🎉 Successfully deleted {deleted_count} document{'s' if deleted_count != 1 else ''}")
        return deleted_count

    except Exception as e:
        raise Exception(f"Failed to remove documents from library: {e}") from e


def list_library_documents(library_id: Optional[str] = None, api_key: Optional[str] = None, display: bool = False) -> List[Dict[str, Any]]:
    """
    List all documents in a specific library.

    Args:
        api_key (str, optional): Your Mistral API key. Uses config.get("mistral_key") if not provided
        library_id (str): The ID of the library

    Returns:
        list: List of document objects in the library

    Example:
        >>> # Using default API key
        >>> documents = list_library_documents(library_id="lib_123")
        >>> for doc in documents:
        ...     print(f"Document: {doc.id} - {doc.filename}")

        >>> # Override API key
        >>> documents = list_library_documents(api_key="different_key", library_id="lib_123")
    """
    # Use default from secrets if not provided
    api_key = api_key or config.get("mistral_key")
    if library_id is None:
        raise ValueError("library_id must be explicitly provided")

    client = Mistral(api_key=api_key)
    documents_response = client.beta.libraries.documents.list(library_id=library_id)

    # Handle different response formats
    if hasattr(documents_response, 'data'):
        documents = documents_response.data
    elif isinstance(documents_response, list):
        documents = documents_response
    else:
        # Try to iterate over the response
        documents = list(documents_response)

    # Display formatted document list if requested
    if display:
        print("\n" + "="*80)
        print("📄 LIBRARY DOCUMENTS")
        print("="*80)

        if not documents:
            print("📚 No documents found in this library.")
        else:
            print(f"📊 Total: {len(documents)} document{'s' if len(documents) != 1 else ''}")
            print("-" * 80)

            for i, doc in enumerate(documents, 1):
                doc_id = getattr(doc, 'id', 'N/A')
                filename = getattr(doc, 'name', 'Unknown')  # Changed from 'filename' to 'name'
                status = getattr(doc, 'processing_status', 'Unknown')  # Changed from 'status' to 'processing_status'
                created_at = getattr(doc, 'created_at', 'Unknown')

                print(f"\n📄 Document #{i}")
                print(f"   🆔 ID: {doc_id}")
                print(f"   📁 File: {filename}")
                print(f"   🔄 Status: {status}")
                print(f"   🕒 Created: {created_at}")

        print("="*80 + "\n")

    return documents