
import subprocess
from ..formatting import status_update_prefix as sup


def processor(input: str) -> str:   # definitely needs re-optimization
    # now can only accept oneliners
    try:
        # run in separate process
        process = subprocess.Popen(
            ["python", "-c", input],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            shell=True,
        )

        # capture stdio
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            return sup(stderr)
        return stdout
    except Exception as e:
        return sup(e)