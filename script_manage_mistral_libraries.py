#!/usr/bin/env python3
"""
Cleanup script to remove duplicate or unwanted libraries.
Helps manage libraries created during testing.
"""
import os
from shared_lib.config_manager import config
from mistral_lib.library_management import list_libraries, delete_library, get_library, list_all_libraries

# Configuration
api_key = config.get("mistral_key")

def cleanup_duplicate_libraries():
    """Clean up libraries with duplicate names"""
    print("=== LIBRARY MANAGEMENT SCRIPT ===")
    print("This script helps manage libraries - create, view, and delete.\n")
    
    # List all libraries
    libraries = list_libraries(api_key=api_key)
    
    # Show libraries in nice format
    if libraries:
        list_all_libraries(api_key=api_key)
    else:
        print("📚 No libraries found.")
    
    # Ask if user wants to create a library or manage existing ones
    print("\n" + "="*60)
    print("MAIN MENU:")
    print("1. Create a new library")
    print("2. Manage existing libraries (view/delete)")
    print("3. Exit")
    
    main_choice = input("\nEnter your choice (1-3): ").strip()
    
    if main_choice == '1':
        create_new_library()
        return
    elif main_choice == '2':
        pass  # Continue with existing management logic
    elif main_choice == '3':
        print("👋 Exiting library management script.")
        return
    else:
        print("❌ Invalid choice. Exiting.")
        return
    
    # Group libraries by name to find duplicates
    name_groups = {}
    for library in libraries:
        name = library.name
        if name not in name_groups:
            name_groups[name] = []
        name_groups[name].append(library)
    
    # Find duplicate names
    duplicates = {name: libs for name, libs in name_groups.items() if len(libs) > 1}
    
    if duplicates:
        print(f"\nFound duplicate libraries for {len(duplicates)} names:")
        for name, libs in duplicates.items():
            print(f"\n  '{name}' ({len(libs)} libraries):")
            for i, lib in enumerate(libs, 1):
                created = lib.created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(lib.created_at, 'strftime') else str(lib.created_at)
                print(f"    {i}. {lib.id} - Created: {created}")
    else:
        print("✅ No duplicate libraries found!")
    
    # Always show cleanup options for general library management
    print("\n" + "="*60)
    print("LIBRARY MANAGEMENT OPTIONS:")
    
    if duplicates:
        print("1. Keep only the newest library for each duplicate name")
        print("2. Keep only the oldest library for each duplicate name")
        print("3. Delete specific libraries by ID")
        print("4. Delete libraries by name pattern")
        print("5. Delete all libraries (DANGER!)")
        print("6. Cancel (do nothing)")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':  # Keep newest
            cleanup_strategy(duplicates, 'newest')
        elif choice == '2':  # Keep oldest
            cleanup_strategy(duplicates, 'oldest')
        elif choice == '3':  # Specific IDs
            cleanup_specific(duplicates)
        elif choice == '4':  # By name pattern
            cleanup_by_name_pattern()
        elif choice == '5':  # Delete all
            cleanup_all_libraries()
        elif choice == '6':  # Cancel
            print("❌ Operation cancelled. No libraries were deleted.")
        else:
            print("❌ Invalid choice. No libraries were deleted.")
    else:
        print("1. Delete specific libraries by ID")
        print("2. Delete libraries by name pattern")
        print("3. Delete all libraries (DANGER!)")
        print("4. Cancel (do nothing)")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':  # Specific IDs - use all libraries
            cleanup_specific_all()
        elif choice == '2':  # By name pattern
            cleanup_by_name_pattern()
        elif choice == '3':  # Delete all
            cleanup_all_libraries()
        elif choice == '4':  # Cancel
            print("❌ Operation cancelled. No libraries were deleted.")
        else:
            print("❌ Invalid choice. No libraries were deleted.")

def cleanup_strategy(duplicates, strategy):
    """Clean up using a strategy (keep newest/oldest)"""
    print(f"\n🗑️  Cleaning up using strategy: keep {strategy}\n")
    
    deleted_count = 0
    kept_count = 0
    
    for name, libs in duplicates.items():
        # Sort by creation date
        sorted_libs = sorted(libs, key=lambda x: x.created_at, reverse=(strategy == 'newest'))
        
        # Keep the first one, delete the rest
        to_keep = sorted_libs[0]
        to_delete = sorted_libs[1:]
        
        print(f"Library '{name}':")
        print(f"  🔹 Keeping: {to_keep.id} (created: {to_keep.created_at})")
        
        for lib in to_delete:
            try:
                delete_library(library_id=lib.id, api_key=api_key)
                print(f"  🗑️  Deleted: {lib.id}")
                deleted_count += 1
            except Exception as e:
                print(f"  ❌ Failed to delete {lib.id}: {e}")
        
        kept_count += 1
    
    print(f"\n📊 Cleanup complete!")
    print(f"   Libraries kept: {kept_count}")
    print(f"   Libraries deleted: {deleted_count}")

def cleanup_specific(duplicates):
    """Clean up specific libraries by ID"""
    print("\n🔍 Specific library cleanup")
    print("Enter the IDs of libraries to delete (comma-separated), or 'all' to delete all duplicates:")
    
    all_ids = []
    for libs in duplicates.values():
        all_ids.extend(lib.id for lib in libs)
    
    print(f"Available IDs: {', '.join(all_ids)}")
    
    choice = input("Enter IDs to delete: ").strip().lower()
    
    if choice == 'all':
        ids_to_delete = all_ids
    else:
        ids_to_delete = [id.strip() for id in choice.split(',') if id.strip() in all_ids]
    
    if not ids_to_delete:
        print("❌ No valid IDs specified. No libraries deleted.")
        return
    
    print(f"\n🗑️  Deleting {len(ids_to_delete)} libraries:")
    deleted_count = 0
    
    for lib_id in ids_to_delete:
        try:
            delete_library(library_id=lib_id, api_key=api_key)
            print(f"  🗑️  Deleted: {lib_id}")
            deleted_count += 1
        except Exception as e:
            print(f"  ❌ Failed to delete {lib_id}: {e}")
    
    print(f"\n📊 Cleanup complete! Deleted {deleted_count} libraries.")


def cleanup_by_name_pattern():
    """Delete libraries matching a name pattern"""
    print("\n🔍 Delete libraries by name pattern")
    print("This will delete all libraries whose names contain the specified text.")
    
    # Get all libraries first
    all_libraries = list_libraries(api_key=api_key)
    if not all_libraries:
        print("✅ No libraries found to delete.")
        return
    
    print("\nCurrent libraries:")
    for i, lib in enumerate(all_libraries, 1):
        print(f"  {i}. {lib.id} - '{lib.name}'")
    
    pattern = input("\nEnter text to match in library names (or 'cancel' to abort): ").strip()
    
    if pattern.lower() == 'cancel':
        print("❌ Operation cancelled.")
        return
    
    if not pattern:
        print("❌ No pattern specified.")
        return
    
    # Find matching libraries
    matching_libs = [lib for lib in all_libraries if pattern.lower() in lib.name.lower()]
    
    if not matching_libs:
        print(f"✅ No libraries found with names containing '{pattern}'.")
        return
    
    print(f"\n🎯 Found {len(matching_libs)} libraries matching '{pattern}':")
    for lib in matching_libs:
        print(f"  - {lib.id}: '{lib.name}'")
    
    confirm = input("\n⚠️  Are you sure you want to delete these libraries? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("❌ Operation cancelled.")
        return
    
    deleted_count = 0
    for lib in matching_libs:
        try:
            delete_library(library_id=lib.id, api_key=api_key)
            print(f"  🗑️  Deleted: {lib.id} - '{lib.name}'")
            deleted_count += 1
        except Exception as e:
            print(f"  ❌ Failed to delete {lib.id}: {e}")
    
    print(f"\n📊 Cleanup complete! Deleted {deleted_count} libraries.")


def cleanup_specific_all():
    """Clean up specific libraries by index from all libraries"""
    print("\n🔍 Specific library cleanup (all libraries)")
    
    # Get all libraries
    all_libraries = list_libraries(api_key=api_key)
    if not all_libraries:
        print("✅ No libraries found.")
        return
    
    print(f"Available libraries ({len(all_libraries)} total):")
    for i, lib in enumerate(all_libraries, 1):
        print(f"  {i}. {lib.id} - '{lib.name}'")
    
    # Create mapping from indices to library objects
    index_to_lib = {str(i): lib for i, lib in enumerate(all_libraries, 1)}
    
    choice = input("\nEnter library NUMBERS to delete (e.g., '1,3' or 'all'): ").strip().lower()
    
    if choice == 'all':
        libs_to_delete = all_libraries
    else:
        # Parse indices and validate
        indices = [idx.strip() for idx in choice.split(',')]
        libs_to_delete = []
        
        for idx in indices:
            if idx in index_to_lib:
                libs_to_delete.append(index_to_lib[idx])
            elif idx.isdigit() and 1 <= int(idx) <= len(all_libraries):
                libs_to_delete.append(all_libraries[int(idx) - 1])
        
        # Also support direct ID entry for advanced users
        if not libs_to_delete:
            # Try direct ID matching as fallback
            all_ids = [lib.id for lib in all_libraries]
            for item in indices:
                if item in all_ids:
                    lib = next(lib for lib in all_libraries if lib.id == item)
                    libs_to_delete.append(lib)
    
    if not libs_to_delete:
        print("❌ No valid library numbers or IDs specified. No libraries deleted.")
        return
    
    print(f"\n🗑️  Preparing to delete {len(libs_to_delete)} libraries:")
    for lib in libs_to_delete:
        print(f"  - {lib.id}: '{lib.name}'")
    
    confirm = input("\n⚠️  Are you sure you want to delete these libraries? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("❌ Operation cancelled.")
        return
    
    deleted_count = 0
    for lib in libs_to_delete:
        try:
            delete_library(library_id=lib.id, api_key=api_key)
            print(f"  🗑️  Deleted: {lib.id} - '{lib.name}'")
            deleted_count += 1
        except Exception as e:
            print(f"  ❌ Failed to delete {lib.id}: {e}")
    
    print(f"\n📊 Cleanup complete! Deleted {deleted_count} libraries.")


def create_new_library():
    """Create a new library with user-specified name and optional description"""
    print("\n📚 CREATE NEW LIBRARY")
    print("Let's create a new library for your documents.\n")
    
    # Get library name
    while True:
        name = input("Enter library name: ").strip()
        if name:
            break
        print("❌ Library name cannot be empty. Please try again.")
    
    # Get optional description
    description = input("Enter library description (optional, press Enter to skip): ").strip()
    if description:
        print(f"📝 Description set: '{description}'")
    else:
        print("📝 No description - that's fine!")
    
    print(f"\n🔧 Creating library '{name}'...")
    
    try:
        # Create the library
        from mistral_lib.library_management import create_library
        
        library_data = {"name": name}
        if description:
            library_data["description"] = description
        
        new_library = create_library(
            api_key=api_key,
            **library_data
        )
        
        print(f"🎉 Library created successfully!")
        print(f"   📚 Name: {new_library.name}")
        print(f"   🆔 ID: {new_library.id}")
        if hasattr(new_library, 'description') and new_library.description:
            print(f"   📝 Description: {new_library.description}")
        print(f"   📅 Created: {new_library.created_at}")
        
        # Offer to upload documents immediately
        upload_now = input("\n📁 Would you like to upload documents to this library now? (yes/no): ").strip().lower()
        if upload_now == 'yes':
            upload_documents_to_library(new_library.id)
        else:
            print("✅ Library created! You can upload documents later using the Mistral AI platform.")
            
    except Exception as e:
        print(f"❌ Failed to create library: {e}")
        import traceback
        traceback.print_exc()


def upload_documents_to_library(library_id):
    """Upload documents to a specific library"""
    print(f"\n📁 UPLOAD DOCUMENTS TO LIBRARY {library_id}")
    
    from mistral_lib.library_management import upload_document
    import os
    
    while True:
        file_path = input("Enter path to document file (or 'done' to finish): ").strip()
        
        if file_path.lower() == 'done':
            break
        
        if not file_path:
            print("❌ Please enter a file path or 'done' to finish.")
            continue
        
        if not os.path.isfile(file_path):
            print(f"❌ File not found: {file_path}")
            continue
        
        # Check file extension
        file_ext = os.path.splitext(file_path)[1].lower()
        supported_extensions = {'.txt', '.csv', '.pdf', '.md', '.markdown', '.json'}
        
        if file_ext not in supported_extensions:
            print(f"⚠️  Unsupported file type: {file_ext}. Supported: {', '.join(supported_extensions)}")
            continue
        
        # Get custom document name
        custom_name = input(f"Enter custom document name (or press Enter to use '{os.path.basename(file_path)}'): ").strip()
        document_name = custom_name or os.path.basename(file_path)
        
        try:
            print(f"📤 Uploading '{document_name}'...")
            result = upload_document(
                library_id=library_id,
                file_path=file_path,
                api_key=api_key,
                document_name=document_name
            )
            print(f"✅ Upload successful! Document ID: {result.id}")
            
        except Exception as e:
            print(f"❌ Failed to upload '{file_path}': {e}")
    
    print("🎉 Document upload complete!")


def cleanup_all_libraries():
    """Delete ALL libraries - use with extreme caution!"""
    print("\n💀 DANGER ZONE: Delete ALL libraries")
    print("⚠️  THIS WILL DELETE EVERY LIBRARY YOU HAVE ACCESS TO!")
    print("⚠️  THIS ACTION CANNOT BE UNDONE!")
    
    # Get all libraries
    all_libraries = list_libraries(api_key=api_key)
    if not all_libraries:
        print("✅ No libraries found to delete.")
        return
    
    print(f"\n📚 Found {len(all_libraries)} libraries that will be deleted:")
    for i, lib in enumerate(all_libraries, 1):
        print(f"  {i}. {lib.id} - '{lib.name}'")
    
    # Require explicit confirmation with the word "DELETE ALL"
    confirm = input("\n🔴 Type 'DELETE ALL' (in uppercase) to confirm: ").strip()
    
    if confirm != 'DELETE ALL':
        print("❌ Operation cancelled. Libraries were NOT deleted.")
        return
    
    print("\n💀 DELETING ALL LIBRARIES...")
    deleted_count = 0
    
    for lib in all_libraries:
        try:
            delete_library(library_id=lib.id, api_key=api_key)
            print(f"  🗑️  Deleted: {lib.id} - '{lib.name}'")
            deleted_count += 1
        except Exception as e:
            print(f"  ❌ Failed to delete {lib.id}: {e}")
    
    print(f"\n📊 Mass deletion complete! Deleted {deleted_count} libraries.")
    print("💀 All your libraries have been permanently removed.")

def main():
    """Run the cleanup script"""
    try:
        cleanup_duplicate_libraries()
    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
