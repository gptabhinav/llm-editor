import sys
import os
import shutil
import argparse
import datetime
from .agent import Agent
from .config import Config
from .utils import parse_input_file

def log_error(message):
    timestamp = datetime.datetime.now().isoformat()
    try:
        with open("error.log", "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass # Fallback if logging fails

def main():
    # 1. Parse Arguments
    parser = argparse.ArgumentParser(description="LLM Text Editor")
    parser.add_argument("input_file", nargs="?", help="Path to the input file")
    parser.add_argument("--outfile", help="Path to the output file. If provided, the input file will not be modified.", default=None)
    parser.add_argument("--inplace", help="Modify the input file in-place, skipping backup regardless of config.", action="store_true")
    parser.add_argument("--init-config", help="Initialize configuration in ~/.llm-editor/", action="store_true")
    args = parser.parse_args()

    if args.init_config:
        config_dir = os.path.expanduser("~/.llm-editor")
        os.makedirs(config_dir, exist_ok=True)
        config_path = os.path.join(config_dir, "config.yaml")
        
        if os.path.exists(config_path):
            print(f"Config file already exists at {config_path}")
            return

        default_config = """llm:
  provider: openai
  api_key: "your_api_key_here"
  model: "gpt-4o"

app:
  backup_enabled: true
  backup_suffix: ".backup"
"""
        with open(config_path, 'w') as f:
            f.write(default_config)
        print(f"Created default config at {config_path}")
        print("Please edit it to add your API key.")
        return

    if not args.input_file:
        parser.print_help()
        return

    # 2. Load and Validate Config
    try:
        Config.load()
        Config.validate()
    except FileNotFoundError:
        print("Configuration file not found.")
        print("Please run 'edit --init-config' to generate a default configuration.")
        return
    except ValueError as e:
        log_error(f"Configuration Error: {e}")
        print(f"Configuration Error: {e}")
        print("Failure. Check error.log for details.")
        return

    input_filepath = args.input_file

    # 3. Parse File
    try:
        user_prompt, content = parse_input_file(input_filepath)
        
        if not user_prompt:
            log_error("Warning: No prompt found between <tag> start_prompt and <tag> end_prompt.")
            # Continuing despite warning, but logging it.
        
    except Exception as e:
        log_error(f"Error parsing file: {e}")
        print("Failure. Check error.log for details.")
        return

    # 4. Initialize Agent
    # You can customize the system prompt here
    system_prompt = (
        "You are an expert text editor. Your task is to rewrite the provided content based on the user's instructions. "
        "You must output ONLY the rewritten content. Do not add any introductory or concluding remarks. "
        "Do not wrap the output in markdown code blocks (```) unless the user asks for it or the file format requires it."
    )
    agent = Agent(system_prompt=system_prompt)

    # 5. Run Agent
    try:
        result = agent.process(user_prompt, content)
    except Exception as e:
        log_error(f"Error during LLM processing: {e}")
        print("Failure. Check error.log for details.")
        return

    # 6. Output Result and Backup
    
    # Determine output mode
    if args.inplace:
        # In-place mode: Overwrite input file, skip backup
        target_file = input_filepath
        should_backup = False
    elif args.outfile:
        # Outfile mode: Write to new file, no backup needed
        target_file = args.outfile
        should_backup = False
    else:
        # Default mode: Overwrite input file, respect backup config
        target_file = input_filepath
        should_backup = Config.BACKUP_ENABLED

    # Perform write operation
    backup_path = None
    try:
        # Create backup if needed
        if should_backup:
            backup_path = input_filepath + Config.BACKUP_SUFFIX
            shutil.copy2(input_filepath, backup_path)

        # Write to target file
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(result)
            
        success_msg = f"Successful. Output: {target_file}"
        if backup_path:
            success_msg += f", Backup: {backup_path}"
        print(success_msg)
            
    except Exception as e:
        log_error(f"Error saving file: {e}")
        # Only attempt restore if we were overwriting the input file AND made a backup
        if target_file == input_filepath and backup_path and os.path.exists(backup_path):
            log_error(f"Attempting to restore from backup: {backup_path}")
            try:
                shutil.copy2(backup_path, input_filepath)
                log_error("Restoration successful.")
            except Exception as restore_error:
                log_error(f"CRITICAL: Failed to restore from backup: {restore_error}")
        
        print("Failure. Check error.log for details.")

if __name__ == "__main__":
    main()
