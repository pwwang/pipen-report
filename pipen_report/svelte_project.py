from pathlib import Path
from liquid import Liquid

class SvelteProject:

    def __init__(self,
                 name,
                 scaffolding,
                 dest_dir,
                 *,
                 dev_port
                 ) -> None:

        package_json = Path(dest_dir)
        scf_package_json = Path(scaffolding) / 'package.json'
        with package_json.open('w') as fpck, scf_package_json.open('r') as scf:
            liq = Liquid(scf)
            fpck.write(liq.render(project_name=name, dev_port=dev_port))

