# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "httpx>=0.27.0",
#     "structlog>=24.4.0",
#     "pydantic>=2.0.0",
#     "pydantic-settings>=2.0.0",
#     "deno>=2.0.0",
# ]
# ///
"""
OpenAPI Client Generator for Artifacts MMO

This script generates a Python client using Deno 2.6's 'deno x' command
to run the OpenAPI Generator. It requires no external installations 
as it uses the bundled Python-Deno bridge.
"""

import sys
import subprocess
import structlog
import deno
from pathlib import Path
from pydantic import HttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_PATH = PROJECT_ROOT / "artifacts_api_client"

log = structlog.get_logger()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_prefix='ARTIFACTS_MMO_', extra='ignore')
    openapi_spec_url: HttpUrl = Field(default="https://api.artifactsmmo.com/openapi.json")

def main():
    try:
        cfg = Settings()
        
        deno_bin = deno.find_deno_bin()
        
        log.info("config_loaded", url=str(cfg.openapi_spec_url), output=str(OUTPUT_PATH))
        log.info("generating_client", message="Using Deno X (Deno 2.6+) to run OpenAPI Generator")

        subprocess.run([
            deno_bin, "x", "npm:@openapitools/openapi-generator-cli", "generate",
            "-i", str(cfg.openapi_spec_url),
            "-g", "python",
            "-o", str(OUTPUT_PATH),
            "--additional-properties=packageName=artifacts_api_client",
            "--skip-validate-spec"
        ], check=True)
        
        log.info("generation_complete", status="success", path=str(OUTPUT_PATH))
        
        log.info("installing_client", message="Installing into virtual environment via uv")
        subprocess.run([
            "uv", "pip", "install", "-e", str(OUTPUT_PATH)
        ], check=True)
        
        log.info("workflow_complete", message="Client generated and installed via Deno!")

    except subprocess.CalledProcessError as e:
        log.error("generation_failed", error=str(e))
        sys.exit(1)
    except Exception as e:
        log.error("execution_failed", error=str(e), error_type=type(e).__name__)
        sys.exit(1)

if __name__ == "__main__":
    main()