import sys
import os

# Add the parent directory of `src` to the system path
# src_directory = os.path.dirname(os.path.abspath(__file__))  # 'src/cli'
# project_root = os.path.dirname(src_directory)  # 'src'
# sys.path.append(project_root)

# print("Updated sys.path:", sys.path)

from admin.admin import admin_portal

def main():
    admin_portal()

if __name__ == "__main__":
    main()
